@domain:usage-data @area:athena-queries @from:iam-shrink/iam-shrink
Feature: Querying CloudTrail Lake for a role's usage
  Lets an operator skip exporting events by having iam-shrink query a CloudTrail Lake / Athena table over a lookback window.

  Background:
    Given a CloudTrail Lake table "cloudtrail_logs" and a results location "s3://example-bucket/out/"

  @id:usage-data.athena-queries.001 @rule:usage.athena.role-and-lookback-window @verified @source:iam_shrink.py#fetch_events_via_athena @test:tests/test_iam_shrink.py#test_fetch_events_via_athena_runs_query_and_parses_rows
  Scenario Outline: Usage is read from the role's events within the lookback window
    Given the operator asks for a lookback of <days_option>
    When the operator analyzes "my-app-role" against the Athena table
    Then the query covers events issued by "my-app-role" in the last <days> days
    And the query results are written to "s3://example-bucket/out/"

    Examples:
      | days_option        | days |
      | no explicit window | 90   |
      | 30 days            | 30   |

  @id:usage-data.athena-queries.002 @rule:usage.athena.role-match-by-name-suffix @gap @source:iam_shrink.py#ATHENA_QUERY @questionable
  Scenario: Another role whose name ends with the analysed name also counts as usage
    Given role "my-app-role" called "dynamodb:Query" in the window
    And role "app-role" never called "dynamodb:Query"
    When the operator analyzes "app-role" against the Athena table
    Then "dynamodb:Query" is counted as used by "app-role"

  @id:usage-data.athena-queries.003 @rule:usage.athena.unfinished-query-aborts @gap @source:iam_shrink.py#fetch_events_via_athena
  Scenario Outline: An Athena query that does not succeed stops the analysis
    Given the Athena query <outcome>
    When the operator analyzes "my-app-role" against the Athena table
    Then the analysis stops with the error "Athena query <query_id> ended in state <state>"
    And no report, policy or Terraform is printed

    Examples:
      | outcome                                 | state     |
      | fails                                   | FAILED    |
      | is cancelled                            | CANCELLED |
      | is still running after about 60 seconds | RUNNING   |
