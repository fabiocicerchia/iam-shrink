@domain:usage-data @area:action-extraction @from:iam-shrink/iam-shrink
Feature: Recognising which IAM actions a role used
  Lets an operator feed CloudTrail events to iam-shrink so it knows which IAM actions the role really exercised, the basis of every keep/remove decision.

  Background:
    Given the role "my-app-role" exists in the AWS account

  @id:usage-data.action-extraction.001 @rule:usage.events.mapped-to-iam-actions @verified @source:iam_shrink.py#event_action @test:tests/test_iam_shrink.py#test_event_mapping_known_and_fallback
  Scenario Outline: Each CloudTrail event counts as use of the IAM action iam-shrink maps it to
    Given a usage file containing an event from "<event_source>" named "<event_name>"
    When the operator analyzes "my-app-role" with that usage file
    Then the action "<iam_action>" is counted as used

    Examples:
      | event_source         | event_name     | iam_action         |
      | s3.amazonaws.com     | GetObject      | s3:GetObject       |
      | s3.amazonaws.com     | ListObjects    | s3:ListBucket      |
      | sqs.amazonaws.com    | ReceiveMessage | sqs:ReceiveMessage |
      | lambda.amazonaws.com | Invoke         | lambda:Invoke      |

  @id:usage-data.action-extraction.002 @rule:usage.events.unmapped-name-used-verbatim @gap @source:iam_shrink.py#event_action @questionable
  Scenario: An event whose name is not its IAM action does not keep the permission that authorised it
    Given the role is allowed "s3:ListBucket"
    And a usage file whose only event is "ListObjectsV2" from "s3.amazonaws.com"
    When the operator analyzes "my-app-role" with that usage file
    Then "s3:ListBucket" is listed under REMOVE
    And "s3:ListObjectsV2" is counted as a used action

  @id:usage-data.action-extraction.003 @rule:usage.event-file.missing-file-aborts @gap @source:iam_shrink.py#main @questionable
  Scenario: A usage file that does not exist stops the analysis
    Given no file exists at "missing.json"
    When the operator analyzes "my-app-role" with usage file "missing.json"
    Then no report, policy or Terraform is printed
    And the command exits with a non-zero status and a file-not-found error traceback
