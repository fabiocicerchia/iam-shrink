@domain:outputs @area:usage-report @from:iam-shrink/iam-shrink
Feature: Reviewing the usage report
  Gives the operator a readable KEEP/REMOVE summary for a role, optionally cross-checked against IAM Access Analyzer.

  Background:
    Given the role "my-app-role" is allowed "s3:*" and "dynamodb:*"
    And the usage shows "s3:GetObject"

  @id:outputs.usage-report.001 @rule:report.keep-remove-listing @gap @source:iam_shrink.py#render_report
  Scenario: The report lists kept and removed permissions with their counts
    When the operator analyzes "my-app-role" without choosing a format
    Then the report heading reads "# iam-shrink — role my-app-role"
    And it shows "allowed patterns: 2, used actions: 1"
    And it lists "KEEP (1):" with "✓ s3:GetObject"
    And it lists "REMOVE (1):" with "✗ dynamodb:*"

  @id:outputs.usage-report.002 @rule:report.analyzer.flags-unused-not-kept @gap @source:iam_shrink.py#render_analyzer_crosscheck @questionable
  Scenario: The Access Analyzer cross-check lists unused findings the CloudTrail result did not keep
    Given Access Analyzer reports "s3:GetObject", "s3:ListBucket" and "dynamodb:Scan" as unused for the role, across several result pages
    When the operator analyzes "my-app-role" with an analyzer ARN and the role ARN
    Then the report ends with a section headed "ACCESS ANALYZER ALSO FLAGGED AS UNUSED (2):"
    And that section lists "⚠ dynamodb:Scan" then "⚠ s3:ListBucket"
    And "s3:GetObject" is not listed

  @id:outputs.usage-report.003 @rule:report.analyzer.report-format-only @gap @source:iam_shrink.py#main @questionable
  Scenario Outline: The Access Analyzer cross-check is silently skipped outside the report
    When the operator analyzes "my-app-role" with an analyzer ARN, the role ARN and format "<format>"
    Then the output contains no "ACCESS ANALYZER ALSO FLAGGED AS UNUSED" section
    And no warning says the cross-check was skipped

    Examples:
      | format  |
      | policy  |
      | tf-diff |
