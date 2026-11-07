@domain:policy-analysis @area:permission-shrinking @from:iam-shrink/iam-shrink
Feature: Deciding which permissions a role keeps
  Gives the operator a keep/remove verdict for every permission the role holds, so unused access can be cut without breaking what the workload calls.

  Background:
    Given the role "my-app-role" exists in the AWS account

  @id:policy-analysis.permission-shrinking.001 @rule:shrink.patterns.keep-used-remove-unused @verified @source:iam_shrink.py#shrink @test:tests/test_iam_shrink.py#test_shrink_narrows_wildcards_and_finds_unused
  Scenario: Wildcards narrow to the actions used and unused permissions are removed
    Given the role is allowed "s3:*", "dynamodb:*" and "sqs:SendMessage"
    And the usage shows "s3:GetObject", "s3:PutObject" and "sqs:SendMessage"
    When the operator analyzes "my-app-role"
    Then the kept actions are "s3:GetObject", "s3:PutObject" and "sqs:SendMessage"
    And the removed permission is "dynamodb:*"

  @id:policy-analysis.permission-shrinking.002 @rule:shrink.patterns.case-insensitive-match @gap @source:iam_shrink.py#shrink
  Scenario: Allowed and used actions match regardless of letter case
    Given the role is allowed "S3:getobject"
    And the usage shows "s3:GetObject"
    When the operator analyzes "my-app-role"
    Then "S3:getobject" is kept as written
    And nothing is removed

  @id:policy-analysis.permission-shrinking.003 @rule:shrink.current.inline-and-attached-policies @verified @source:iam_shrink.py#fetch_role_policies @test:tests/test_iam_shrink.py#test_fetch_role_policies_combines_inline_and_attached
  Scenario: Both inline and attached managed policies count as the role's permissions
    Given an inline policy of the role allows "s3:*"
    And an attached managed policy's default version allows "sqs:SendMessage"
    When the operator analyzes "my-app-role"
    Then the allowed permissions are "s3:*" and "sqs:SendMessage"

  @id:policy-analysis.permission-shrinking.004 @rule:shrink.current.only-allow-statements-considered @verified @source:iam_shrink.py#allowed_actions @test:tests/test_iam_shrink.py#test_allowed_flattening_handles_string_and_dict_statements @questionable
  Scenario: Deny statements are neither kept nor reported as removed
    Given the role has a statement denying "iam:*"
    And the role has a statement allowing "sqs:SendMessage"
    When the operator analyzes "my-app-role"
    Then only "sqs:SendMessage" is counted as allowed
    And "iam:*" appears neither under KEEP nor under REMOVE
