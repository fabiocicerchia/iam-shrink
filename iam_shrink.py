#!/usr/bin/env python3
"""iam-shrink — shrink IAM policies to what CloudTrail says is actually used.

Pipeline:
  1. Pull the actions a role is ALLOWED (attached+inline policies)
  2. Pull the actions the role actually USED (Athena over CloudTrail, or a
     pre-exported JSON of eventSource/eventName pairs)
  3. Emit the minimized policy + a Terraform-style diff for review

  iam-shrink analyze my-app-role --usage usage.json
  iam-shrink analyze my-app-role --usage usage.json --format tf-diff
"""

import argparse
import fnmatch
import json
import sys

# The AWS policy language version every emitted document carries; not this tool's.
POLICY_VERSION = "2012-10-17"
SID_PREFIX = "IamShrinkMinimized"

# CloudTrail eventSource/eventName -> IAM action (subset; grows over time)
EVENT_TO_ACTION = {
    ("s3.amazonaws.com", "GetObject"): "s3:GetObject",
    ("s3.amazonaws.com", "PutObject"): "s3:PutObject",
    ("s3.amazonaws.com", "ListObjects"): "s3:ListBucket",
    ("dynamodb.amazonaws.com", "GetItem"): "dynamodb:GetItem",
    ("dynamodb.amazonaws.com", "Query"): "dynamodb:Query",
    ("sqs.amazonaws.com", "SendMessage"): "sqs:SendMessage",
    ("sqs.amazonaws.com", "ReceiveMessage"): "sqs:ReceiveMessage",
}

# Athena / CloudTrail Lake. The poll budget is ATTEMPTS x INTERVAL seconds,
# plenty for a small aggregate query.
DEFAULT_LOOKBACK_DAYS = 90
ATHENA_SUCCEEDED = "SUCCEEDED"
ATHENA_TERMINAL_STATES = (ATHENA_SUCCEEDED, "FAILED", "CANCELLED")
ATHENA_POLL_ATTEMPTS = 60
ATHENA_POLL_INTERVAL_S = 1

# The exact query documented in the README, parameterized by role + window.
ATHENA_QUERY = """\
SELECT eventsource AS eventSource, eventname AS eventName
FROM {table}
WHERE useridentity.sessioncontext.sessionissuer.arn LIKE '%{role_name}'
  AND eventtime > date_add('day', -{days}, now())
GROUP BY 1, 2
"""


def event_action(event):
    """The IAM action a CloudTrail event maps to (best-effort, else source:Name)."""
    source = event.get("eventSource", "")
    name = event.get("eventName", "")
    return EVENT_TO_ACTION.get((source, name), f"{source.split('.')[0]}:{name}")


def used_actions(events):
    """Map CloudTrail events to IAM actions (best-effort, else source:Name)."""
    return {event_action(e) for e in events}


def used_action_resources(events):
    """Map used action -> resource ARNs, where CloudTrail recorded them on the event."""
    mapping = {}
    for e in events:
        arns = {r["ARN"] for r in e.get("resources", []) if r.get("ARN")}
        if arns:
            mapping.setdefault(event_action(e), set()).update(arns)
    return mapping


def allowed_actions(policy_documents):
    """Flatten Allow statements into a set of action patterns."""
    patterns = set()
    for doc in policy_documents:
        statements = doc.get("Statement", [])
        if isinstance(statements, dict):
            statements = [statements]
        for statement in statements:
            if statement.get("Effect") != "Allow":
                continue
            actions = statement.get("Action", [])
            patterns.update([actions] if isinstance(actions, str) else actions)
    return patterns


def shrink(allowed_patterns, used):
    """Split allowed patterns into (kept, removable).

    A pattern is kept iff at least one observed action matches it; wildcards
    are then narrowed to the concrete used actions they matched.
    """
    kept, removable = set(), set()
    for pattern in allowed_patterns:
        matches = {a for a in used if fnmatch.fnmatchcase(a.lower(), pattern.lower())}
        if matches:
            kept.update(matches if "*" in pattern else {pattern})
        else:
            removable.add(pattern)
    return kept, removable


def _split_by_resource(kept, resource_map):
    """kept actions with a known resource ARN vs. the rest (stay on Resource: "*")."""
    resource_map = resource_map or {}
    scoped = {a: sorted(resource_map[a]) for a in kept if resource_map.get(a)}
    wildcard = sorted(a for a in kept if a not in scoped)
    return wildcard, scoped


def minimized_policy(kept, resource_map=None):
    wildcard, scoped = _split_by_resource(kept, resource_map)
    statements = []
    if wildcard:
        statements.append(
            {
                "Sid": SID_PREFIX,
                "Effect": "Allow",
                "Action": wildcard,
                "Resource": "*",
            }
        )
    for action, arns in sorted(scoped.items()):
        sid = SID_PREFIX + action.replace(":", "").replace("*", "Any")
        statements.append({"Sid": sid, "Effect": "Allow", "Action": [action], "Resource": arns})
    return {"Version": POLICY_VERSION, "Statement": statements}


def tf_diff(role_name, kept, removable, resource_map=None):
    wildcard, scoped = _split_by_resource(kept, resource_map)
    statements = []
    if wildcard:
        statements.append((wildcard, '"*"'))
    for action, arns in sorted(scoped.items()):
        arn_list = "[" + ", ".join(f'"{a}"' for a in arns) + "]"
        statements.append(([action], arn_list))

    # The resource label and the role reference must stay the same identifier,
    # or the emitted snippet points at a resource that does not exist.
    tf_name = role_name.replace("-", "_")
    lines = [
        f'# iam-shrink suggestion for role "{role_name}"',
        f"# {len(removable)} unused action pattern(s) removed, {len(kept)} kept",
        "",
        f'resource "aws_iam_role_policy" "{tf_name}_minimized" {{',
        f'  name = "{role_name}-minimized"',
        f"  role = aws_iam_role.{tf_name}.id",
        "  policy = jsonencode({",
        f'    Version = "{POLICY_VERSION}"',
        "    Statement = [",
    ]
    for actions, resource in statements:
        lines.append("      {")
        lines.append('        Effect   = "Allow"')
        lines.append("        Action   = [")
        for a in actions:
            lines.append(f'          "{a}",')
        lines.append("        ]")
        lines.append(f"        Resource = {resource}")
        lines.append("      },")
    lines += ["    ]", "  })", "}", ""]
    for r in sorted(removable):
        lines.append(f"# removed (never used in observation window): {r}")
    return "\n".join(lines)


def fetch_role_policies(role_name, client=None):
    import boto3

    iam = client or boto3.client("iam")
    docs = []
    for name in iam.list_role_policies(RoleName=role_name)["PolicyNames"]:
        docs.append(iam.get_role_policy(RoleName=role_name, PolicyName=name)["PolicyDocument"])
    for attached in iam.list_attached_role_policies(RoleName=role_name)["AttachedPolicies"]:
        arn = attached["PolicyArn"]
        policy = iam.get_policy(PolicyArn=arn)["Policy"]
        version = iam.get_policy_version(PolicyArn=arn, VersionId=policy["DefaultVersionId"])
        docs.append(version["PolicyVersion"]["Document"])
    return docs


def fetch_events_via_athena(
    role_name, table, output_location, days=DEFAULT_LOOKBACK_DAYS, client=None
):
    """Run the CloudTrail Lake query from the README and return CloudTrail-shaped events."""
    import time

    import boto3

    athena = client or boto3.client("athena")
    query = ATHENA_QUERY.format(table=table, role_name=role_name, days=days)
    exec_id = athena.start_query_execution(
        QueryString=query,
        ResultConfiguration={"OutputLocation": output_location},
    )["QueryExecutionId"]

    for _ in range(ATHENA_POLL_ATTEMPTS):
        state = athena.get_query_execution(QueryExecutionId=exec_id)["QueryExecution"]["Status"][
            "State"
        ]
        if state in ATHENA_TERMINAL_STATES:
            break
        time.sleep(ATHENA_POLL_INTERVAL_S)
    if state != ATHENA_SUCCEEDED:
        raise RuntimeError(f"Athena query {exec_id} ended in state {state}")

    rows = athena.get_query_results(QueryExecutionId=exec_id)["ResultSet"]["Rows"]
    header = [c.get("VarCharValue") for c in rows[0]["Data"]]
    events = []
    for row in rows[1:]:
        values = [c.get("VarCharValue") for c in row["Data"]]
        events.append(dict(zip(header, values)))
    return events


def fetch_analyzer_unused_actions(analyzer_arn, role_arn, client=None):
    """IAM Access Analyzer's own UNUSED_PERMISSION findings for a role.

    A second, independent signal for "unused": Access Analyzer sees actions
    CloudTrail doesn't log by default (many List/Describe/Get calls), so this
    is a cross-check on top of the CloudTrail-based shrink, not a replacement.
    """
    import boto3

    analyzer = client or boto3.client("accessanalyzer")
    actions = set()
    next_token = None
    while True:
        kwargs = {
            "analyzerArn": analyzer_arn,
            "filter": {
                "resource": {"eq": [role_arn]},
                "findingType": {"eq": ["UnusedPermission"]},
            },
        }
        if next_token:
            kwargs["nextToken"] = next_token
        page = analyzer.list_findings_v2(**kwargs)
        for finding in page.get("findings", []):
            actions.update(finding.get("action", []) or finding.get("actions", []))
        next_token = page.get("nextToken")
        if not next_token:
            break
    return actions


def _run_checked(cmd):
    """Run a command and raise on a non-zero exit; open_pr's default runner."""
    import subprocess

    return subprocess.run(cmd, check=True, capture_output=True, text=True)


def open_pr(role_name, tf_content, run=None):
    """Write the tf-diff, commit it on a new branch, and open a PR with `gh`.

    Assumes it's run inside the IaC repo that should receive the change.
    """
    run = run or _run_checked
    filename = f"{role_name}-minimized.tf"
    with open(filename, "w") as fh:
        fh.write(tf_content)

    branch = f"iam-shrink/{role_name}"
    run(["git", "checkout", "-b", branch])
    run(["git", "add", filename])
    run(["git", "commit", "-m", f"iam-shrink: minimize {role_name}"])
    run(["git", "push", "-u", "origin", branch])
    created = run(
        [
            "gh",
            "pr",
            "create",
            "--title",
            f"iam-shrink: minimize {role_name}",
            "--body",
            f"Generated by `iam-shrink analyze {role_name} --format tf-diff`. Review before merging.",
        ]
    )
    return getattr(created, "stdout", "").strip()


def build_parser():
    """The iam-shrink command line."""
    parser = argparse.ArgumentParser(
        prog="iam-shrink",
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="cmd", required=True)
    analyze = sub.add_parser("analyze")
    analyze.add_argument("role_name")
    usage_src = analyze.add_mutually_exclusive_group(required=True)
    usage_src.add_argument(
        "--usage",
        help="JSON file of CloudTrail events [{eventSource, eventName}, ...]",
    )
    usage_src.add_argument(
        "--athena-table",
        help="CloudTrail Lake table to query instead of --usage (needs --athena-output)",
    )
    analyze.add_argument(
        "--athena-output",
        help="S3 URI for Athena query results, required with --athena-table",
    )
    analyze.add_argument(
        "--athena-days",
        type=int,
        default=DEFAULT_LOOKBACK_DAYS,
        help=f"Lookback window in days (default: {DEFAULT_LOOKBACK_DAYS})",
    )
    analyze.add_argument("--format", choices=["report", "policy", "tf-diff"], default="report")
    analyze.add_argument(
        "--analyzer-arn",
        help="IAM Access Analyzer ARN; cross-checks its UnusedPermission findings "
        "for --role-arn against the CloudTrail-based result (report format only)",
    )
    analyze.add_argument(
        "--role-arn",
        help="Role ARN to look up in Access Analyzer, required with --analyzer-arn",
    )
    analyze.add_argument(
        "--open-pr",
        action="store_true",
        help="Commit the tf-diff on a new branch and open a PR with `gh` "
        "(run from inside the target IaC repo)",
    )
    return parser


def reject_conflicting_flags(parser, args):
    """Flag combinations argparse cannot express. Exits 2 through the parser."""
    if args.athena_table and not args.athena_output:
        parser.error("--athena-table requires --athena-output")
    if args.analyzer_arn and not args.role_arn:
        parser.error("--analyzer-arn requires --role-arn")
    if args.open_pr and args.format != "tf-diff":
        parser.error("--open-pr requires --format tf-diff")


def render_report(role_name, allowed, used, kept, removable):
    """The default human-readable KEEP/REMOVE listing."""
    print(f"# iam-shrink — role {role_name}")
    print(f"allowed patterns: {len(allowed)}, used actions: {len(used)}")
    print(f"\nKEEP ({len(kept)}):")
    for a in sorted(kept):
        print(f"  ✓ {a}")
    print(f"\nREMOVE ({len(removable)}):")
    for a in sorted(removable):
        print(f"  ✗ {a}")


def render_analyzer_crosscheck(analyzer_arn, role_arn, kept):
    """Actions Access Analyzer also calls unused, on top of the CloudTrail result."""
    extra = sorted(fetch_analyzer_unused_actions(analyzer_arn, role_arn) - kept)
    print(f"\nACCESS ANALYZER ALSO FLAGGED AS UNUSED ({len(extra)}):")
    for a in extra:
        print(f"  ⚠ {a}")


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    reject_conflicting_flags(parser, args)

    # Kept inline: an extracted loader adds a frame to the traceback a missing
    # --usage file already raises, which the recorded baseline reads as drift.
    if args.athena_table:
        events = fetch_events_via_athena(
            args.role_name, args.athena_table, args.athena_output, args.athena_days
        )
    else:
        with open(args.usage) as fh:
            events = json.load(fh)
    used = used_actions(events)
    resource_map = used_action_resources(events)
    allowed = allowed_actions(fetch_role_policies(args.role_name))
    kept, removable = shrink(allowed, used)

    if args.format == "policy":
        json.dump(minimized_policy(kept, resource_map), sys.stdout, indent=2)
    elif args.format == "tf-diff":
        diff = tf_diff(args.role_name, kept, removable, resource_map)
        print(diff)
        if args.open_pr:
            pr_url = open_pr(args.role_name, diff)
            print(pr_url, file=sys.stderr)
    else:
        render_report(args.role_name, allowed, used, kept, removable)
        if args.analyzer_arn:
            render_analyzer_crosscheck(args.analyzer_arn, args.role_arn, kept)
    return 0


if __name__ == "__main__":
    sys.exit(main())
