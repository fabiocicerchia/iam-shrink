from iam_shrink import (
    allowed_actions,
    fetch_analyzer_unused_actions,
    fetch_events_via_athena,
    minimized_policy,
    shrink,
    tf_diff,
    used_action_resources,
    used_actions,
)


def test_event_mapping_known_and_fallback():
    events = [
        {"eventSource": "s3.amazonaws.com", "eventName": "GetObject"},
        {"eventSource": "lambda.amazonaws.com", "eventName": "Invoke"},
    ]
    assert used_actions(events) == {"s3:GetObject", "lambda:Invoke"}


def test_allowed_flattening_handles_string_and_dict_statements():
    docs = [
        {"Statement": {"Effect": "Allow", "Action": "s3:*"}},
        {
            "Statement": [
                {"Effect": "Deny", "Action": "iam:*"},
                {"Effect": "Allow", "Action": ["sqs:SendMessage"]},
            ]
        },
    ]
    assert allowed_actions(docs) == {"s3:*", "sqs:SendMessage"}


def test_shrink_narrows_wildcards_and_finds_unused():
    kept, removable = shrink(
        {"s3:*", "dynamodb:*", "sqs:SendMessage"},
        {"s3:GetObject", "s3:PutObject", "sqs:SendMessage"},
    )
    assert kept == {"s3:GetObject", "s3:PutObject", "sqs:SendMessage"}
    assert removable == {"dynamodb:*"}


def test_outputs_are_deterministic():
    policy = minimized_policy({"b:Two", "a:One"})
    assert policy["Statement"][0]["Action"] == ["a:One", "b:Two"]
    diff = tf_diff("my-role", {"s3:GetObject"}, {"dynamodb:*"})
    assert 'aws_iam_role_policy" "my_role_minimized"' in diff
    assert "# removed (never used in observation window): dynamodb:*" in diff


class _FakeAthenaClient:
    def __init__(self):
        self.query = None

    def start_query_execution(self, QueryString, ResultConfiguration):
        self.query = QueryString
        assert ResultConfiguration["OutputLocation"] == "s3://bucket/out/"
        return {"QueryExecutionId": "abc123"}

    def get_query_execution(self, QueryExecutionId):
        assert QueryExecutionId == "abc123"
        return {"QueryExecution": {"Status": {"State": "SUCCEEDED"}}}

    def get_query_results(self, QueryExecutionId):
        return {
            "ResultSet": {
                "Rows": [
                    {"Data": [{"VarCharValue": "eventSource"}, {"VarCharValue": "eventName"}]},
                    {
                        "Data": [
                            {"VarCharValue": "s3.amazonaws.com"},
                            {"VarCharValue": "GetObject"},
                        ]
                    },
                ]
            }
        }


def test_fetch_events_via_athena_runs_query_and_parses_rows():
    client = _FakeAthenaClient()
    events = fetch_events_via_athena(
        "my-app-role", "cloudtrail_logs", "s3://bucket/out/", days=30, client=client
    )
    assert events == [{"eventSource": "s3.amazonaws.com", "eventName": "GetObject"}]
    assert "cloudtrail_logs" in client.query
    assert "my-app-role" in client.query
    assert "-30" in client.query


class _FakeAnalyzerClient:
    def list_findings_v2(self, analyzerArn, filter, nextToken=None):
        assert analyzerArn == "arn:aws:access-analyzer:us-east-1:1:analyzer/x"
        assert filter["resource"]["eq"] == ["arn:aws:iam::1:role/my-app-role"]
        if nextToken is None:
            return {
                "findings": [{"action": ["s3:ListBucket"]}],
                "nextToken": "page2",
            }
        return {"findings": [{"action": ["dynamodb:Scan"]}]}


def test_fetch_analyzer_unused_actions_paginates():
    actions = fetch_analyzer_unused_actions(
        "arn:aws:access-analyzer:us-east-1:1:analyzer/x",
        "arn:aws:iam::1:role/my-app-role",
        client=_FakeAnalyzerClient(),
    )
    assert actions == {"s3:ListBucket", "dynamodb:Scan"}


def test_used_action_resources_only_collects_actions_with_arns():
    events = [
        {
            "eventSource": "s3.amazonaws.com",
            "eventName": "GetObject",
            "resources": [{"ARN": "arn:aws:s3:::my-bucket/key"}],
        },
        {"eventSource": "sqs.amazonaws.com", "eventName": "SendMessage"},
    ]
    assert used_action_resources(events) == {
        "s3:GetObject": {"arn:aws:s3:::my-bucket/key"}
    }


def test_minimized_policy_narrows_resource_for_actions_with_known_arns():
    resource_map = {"s3:GetObject": {"arn:aws:s3:::my-bucket/key"}}
    policy = minimized_policy({"s3:GetObject", "sqs:SendMessage"}, resource_map)
    by_action = {tuple(s["Action"]): s["Resource"] for s in policy["Statement"]}
    assert by_action[("s3:GetObject",)] == ["arn:aws:s3:::my-bucket/key"]
    assert by_action[("sqs:SendMessage",)] == "*"


def test_tf_diff_narrows_resource_for_actions_with_known_arns():
    resource_map = {"s3:GetObject": {"arn:aws:s3:::my-bucket/key"}}
    diff = tf_diff("my-role", {"s3:GetObject", "sqs:SendMessage"}, set(), resource_map)
    assert '"arn:aws:s3:::my-bucket/key"' in diff
    assert 'Resource = "*"' in diff
