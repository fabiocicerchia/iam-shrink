@domain:change-delivery @area:command-line @from:iam-shrink/iam-shrink
Feature: Running the analyze command
  Protects the operator from contradictory or incomplete option combinations before any AWS call is made.

  @id:change-delivery.command-line.001 @rule:cli.analyze.invalid-flag-combinations-refused @gap @source:iam_shrink.py#reject_conflicting_flags
  Scenario Outline: Incomplete or conflicting options are refused before analysis starts
    When the operator runs analyze for "my-app-role" with <options>
    Then the command prints the usage and the error "<message>"
    And it exits with status 2 without contacting AWS

    Examples:
      | options                                                                                     | message                                                    |
      | --athena-table cloudtrail_logs only                                                         | --athena-table requires --athena-output                    |
      | --usage usage.json --analyzer-arn arn:aws:access-analyzer:us-east-1:111122223333:analyzer/x | --analyzer-arn requires --role-arn                         |
      | --usage usage.json --open-pr                                                                | --open-pr requires --format tf-diff                        |
      | --usage usage.json --athena-table cloudtrail_logs                                           | argument --athena-table: not allowed with argument --usage |
      | no usage source                                                                             | one of the arguments --usage --athena-table is required    |
