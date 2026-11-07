@domain:outputs @area:terraform-diff @from:iam-shrink/iam-shrink
Feature: Proposing the change as Terraform
  Gives the operator a Terraform snippet for the minimized policy that can be reviewed and applied in their IaC repo.

  Background:
    Given the role "my-role" is allowed "s3:*" and "dynamodb:*"
    And the usage shows "s3:GetObject"

  @id:outputs.terraform-diff.001 @rule:tfdiff.role-policy-resource @verified @source:iam_shrink.py#tf_diff @test:tests/test_iam_shrink.py#test_outputs_are_deterministic @questionable
  Scenario: The Terraform proposes a minimized inline policy on the role
    When the operator analyzes "my-role" with format "tf-diff"
    Then it starts with "# iam-shrink suggestion for role \"my-role\"" and "# 1 unused action pattern(s) removed, 1 kept"
    And it declares resource "aws_iam_role_policy" "my_role_minimized" named "my-role-minimized"
    And the policy is attached to "aws_iam_role.my_role.id"
    And it allows "s3:GetObject" on Resource "*"

  @id:outputs.terraform-diff.002 @rule:tfdiff.removed-permissions-commented @verified @source:iam_shrink.py#tf_diff @test:tests/test_iam_shrink.py#test_outputs_are_deterministic
  Scenario: Removed permissions are listed as comments in the Terraform
    When the operator analyzes "my-role" with format "tf-diff"
    Then the Terraform ends with "# removed (never used in observation window): dynamodb:*"

  @id:outputs.terraform-diff.003 @rule:tfdiff.scoped-to-observed-resources @verified @source:iam_shrink.py#tf_diff @test:tests/test_iam_shrink.py#test_tf_diff_narrows_resource_for_actions_with_known_arns
  Scenario: The Terraform scopes used actions to the resources recorded for them
    Given the usage records "s3:GetObject" on "arn:aws:s3:::example-bucket/key"
    And the usage also shows "sqs:SendMessage" with no recorded resource
    And the role is allowed "sqs:SendMessage"
    When the operator analyzes "my-role" with format "tf-diff"
    Then one statement allows "s3:GetObject" on ["arn:aws:s3:::example-bucket/key"]
    And another statement allows "sqs:SendMessage" on Resource "*"
