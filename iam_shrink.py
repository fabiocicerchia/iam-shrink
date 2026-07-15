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


def used_actions(events):
    """Map CloudTrail events to IAM actions (best-effort, else source:Name)."""
    actions = set()
    for e in events:
        key = (e.get("eventSource", ""), e.get("eventName", ""))
        if key in EVENT_TO_ACTION:
            actions.add(EVENT_TO_ACTION[key])
        else:
            service = key[0].split(".")[0]
            actions.add(f"{service}:{key[1]}")
    return actions


def allowed_actions(policy_documents):
    """Flatten Allow statements into a set of action patterns."""
    patterns = set()
    for doc in policy_documents:
        statements = doc.get("Statement", [])
        if isinstance(statements, dict):
            statements = [statements]
        for st in statements:
            if st.get("Effect") != "Allow":
                continue
            acts = st.get("Action", [])
            patterns.update([acts] if isinstance(acts, str) else acts)
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


def minimized_policy(kept):
    return {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "IamShrinkMinimized",
                "Effect": "Allow",
                "Action": sorted(kept),
                "Resource": "*",  # resource narrowing is phase 2 (see README)
            }
        ],
    }


def tf_diff(role_name, kept, removable):
    lines = [
        f'# iam-shrink suggestion for role "{role_name}"',
        f"# {len(removable)} unused action pattern(s) removed, {len(kept)} kept",
        "",
        f'resource "aws_iam_role_policy" "{role_name.replace("-", "_")}_minimized" {{',
        f'  name = "{role_name}-minimized"',
        f"  role = aws_iam_role.{role_name.replace('-', '_')}.id",
        "  policy = jsonencode({",
        '    Version = "2012-10-17"',
        "    Statement = [{",
        '      Effect   = "Allow"',
        "      Action   = [",
    ]
    for a in sorted(kept):
        lines.append(f'        "{a}",')
    lines += ["      ]", '      Resource = "*"', "    }]", "  })", "}", ""]
    for r in sorted(removable):
        lines.append(f"# removed (never used in observation window): {r}")
    return "\n".join(lines)


def fetch_role_policies(role_name):
    import boto3

    iam = boto3.client("iam")
    docs = []
    for name in iam.list_role_policies(RoleName=role_name)["PolicyNames"]:
        docs.append(
            iam.get_role_policy(RoleName=role_name, PolicyName=name)["PolicyDocument"]
        )
    for att in iam.list_attached_role_policies(RoleName=role_name)["AttachedPolicies"]:
        pol = iam.get_policy(PolicyArn=att["PolicyArn"])["Policy"]
        ver = iam.get_policy_version(
            PolicyArn=att["PolicyArn"], VersionId=pol["DefaultVersionId"]
        )
        docs.append(ver["PolicyVersion"]["Document"])
    return docs


# The exact query documented in the README, parameterized by role + window.
ATHENA_QUERY = """\
SELECT eventsource AS eventSource, eventname AS eventName
FROM {table}
WHERE useridentity.sessioncontext.sessionissuer.arn LIKE '%{role_name}'
  AND eventtime > date_add('day', -{days}, now())
GROUP BY 1, 2
"""


def fetch_events_via_athena(role_name, table, output_location, days=90, client=None):
    """Run the CloudTrail Lake query from the README and return CloudTrail-shaped events."""
    import time

    import boto3

    athena = client or boto3.client("athena")
    query = ATHENA_QUERY.format(table=table, role_name=role_name, days=days)
    exec_id = athena.start_query_execution(
        QueryString=query,
        ResultConfiguration={"OutputLocation": output_location},
    )["QueryExecutionId"]

    for _ in range(60):  # ~60s at 1s/poll, plenty for a small aggregate query
        state = athena.get_query_execution(QueryExecutionId=exec_id)["QueryExecution"][
            "Status"
        ]["State"]
        if state in ("SUCCEEDED", "FAILED", "CANCELLED"):
            break
        time.sleep(1)
    if state != "SUCCEEDED":
        raise RuntimeError(f"Athena query {exec_id} ended in state {state}")

    rows = athena.get_query_results(QueryExecutionId=exec_id)["ResultSet"]["Rows"]
    header = [c.get("VarCharValue") for c in rows[0]["Data"]]
    events = []
    for row in rows[1:]:
        values = [c.get("VarCharValue") for c in row["Data"]]
        events.append(dict(zip(header, values)))
    return events


def main(argv=None):
    p = argparse.ArgumentParser(
        prog="iam-shrink",
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("analyze")
    s.add_argument("role_name")
    usage_src = s.add_mutually_exclusive_group(required=True)
    usage_src.add_argument(
        "--usage",
        help="JSON file of CloudTrail events [{eventSource, eventName}, ...]",
    )
    usage_src.add_argument(
        "--athena-table",
        help="CloudTrail Lake table to query instead of --usage (needs --athena-output)",
    )
    s.add_argument(
        "--athena-output",
        help="S3 URI for Athena query results, required with --athena-table",
    )
    s.add_argument(
        "--athena-days", type=int, default=90, help="Lookback window in days (default: 90)"
    )
    s.add_argument(
        "--format", choices=["report", "policy", "tf-diff"], default="report"
    )
    args = p.parse_args(argv)

    if args.athena_table and not args.athena_output:
        p.error("--athena-table requires --athena-output")

    if args.athena_table:
        events = fetch_events_via_athena(
            args.role_name, args.athena_table, args.athena_output, args.athena_days
        )
    else:
        with open(args.usage) as fh:
            events = json.load(fh)
    used = used_actions(events)
    allowed = allowed_actions(fetch_role_policies(args.role_name))
    kept, removable = shrink(allowed, used)

    if args.format == "policy":
        json.dump(minimized_policy(kept), sys.stdout, indent=2)
    elif args.format == "tf-diff":
        print(tf_diff(args.role_name, kept, removable))
    else:
        print(f"# iam-shrink — role {args.role_name}")
        print(f"allowed patterns: {len(allowed)}, used actions: {len(used)}")
        print(f"\nKEEP ({len(kept)}):")
        for a in sorted(kept):
            print(f"  ✓ {a}")
        print(f"\nREMOVE ({len(removable)}):")
        for a in sorted(removable):
            print(f"  ✗ {a}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
