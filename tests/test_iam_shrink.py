from iam_shrink import allowed_actions, minimized_policy, shrink, tf_diff, used_actions


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
