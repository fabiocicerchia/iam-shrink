@domain:outputs @area:minimized-policy @from:iam-shrink/iam-shrink
Feature: Producing a least-privilege policy document
  Gives the operator an IAM policy JSON containing only the actions the role used, scoped to the resources CloudTrail recorded.

  Background:
    Given the role "my-app-role" exists in the AWS account

  @id:outputs.minimized-policy.001 @rule:policy.unscoped-actions-on-any-resource @verified @source:iam_shrink.py#minimized_policy @test:tests/test_iam_shrink.py#test_outputs_are_deterministic @test:tests/test_iam_shrink.py#test_minimized_policy_narrows_resource_for_actions_with_known_arns
  Scenario: Used actions with no recorded resource are granted in one sorted statement on any resource
    Given the kept actions are "sqs:SendMessage" and "dynamodb:GetItem"
    And the usage records no resource for either action
    When the operator analyzes "my-app-role" with format "policy"
    Then the policy Version is "2012-10-17"
    And one statement "IamShrinkMinimized" allows "dynamodb:GetItem" and "sqs:SendMessage" in that order
    And that statement's Resource is "*"

  @id:outputs.minimized-policy.002 @rule:policy.scoped-to-observed-resources @verified @source:iam_shrink.py#minimized_policy @test:tests/test_iam_shrink.py#test_minimized_policy_narrows_resource_for_actions_with_known_arns @test:tests/test_iam_shrink.py#test_used_action_resources_only_collects_actions_with_arns
  Scenario: A used action with recorded resources is granted only on those resources
    Given the kept actions are "s3:GetObject" and "sqs:SendMessage"
    And the usage records "s3:GetObject" on "arn:aws:s3:::example-bucket/key"
    When the operator analyzes "my-app-role" with format "policy"
    Then statement "IamShrinkMinimizeds3GetObject" allows only "s3:GetObject" on "arn:aws:s3:::example-bucket/key"
    And "sqs:SendMessage" stays on Resource "*"

  @id:outputs.minimized-policy.003 @rule:policy.original-resource-scope-not-preserved @gap @source:iam_shrink.py#allowed_actions @questionable
  Scenario: A permission limited to specific resources becomes a grant on any resource when usage records none
    Given the role allows "s3:GetObject" only on "arn:aws:s3:::example-bucket/*"
    And the usage shows "s3:GetObject" with no recorded resource
    When the operator analyzes "my-app-role" with format "policy"
    Then the policy allows "s3:GetObject" on Resource "*"

  @id:outputs.minimized-policy.004 @rule:policy.nothing-used-empty-policy @gap @source:iam_shrink.py#minimized_policy @questionable
  Scenario: When nothing the role holds was used the policy has no statements
    Given the role is allowed "dynamodb:*"
    And the usage shows only "s3:GetObject"
    When the operator analyzes "my-app-role" with format "policy"
    Then the policy is {"Version": "2012-10-17", "Statement": []}
