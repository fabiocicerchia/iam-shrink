# Specifications of iam-shrink

What this code does, one atomic Gherkin scenario per behaviour, read from the code by code-atlas.
Tags: `@verified` a test asserts it · `@inferred` read from the code only · `@gap` an entry point no test covers · `@human` written or amended by a person, never rewritten.

## Change Delivery
Getting the recommended policy change into the infrastructure repository for review.

- **Command line**: [Running the analyze command](change-delivery/command-line/analyze-command-line.feature) (1)
- **Pull requests**: [Opening a pull request with the proposed change](change-delivery/pull-requests/pull-requests.feature) (2)

## Distribution
How users obtain and run iam-shrink.

- **Container image**: [Running iam-shrink from the container image](distribution/container-image/container-image.feature) (2)
- **Installer**: [Installing iam-shrink with the one-line installer](distribution/installer/one-line-installer.feature) (3)

## Outputs
The forms in which iam-shrink presents its recommendation.

- **Minimized policy**: [Producing a least-privilege policy document](outputs/minimized-policy/minimized-policy.feature) (4)
- **Terraform diff**: [Proposing the change as Terraform](outputs/terraform-diff/terraform-diff.feature) (3)
- **Usage report**: [Reviewing the usage report](outputs/usage-report/usage-report.feature) (3)

## Policy Analysis
Comparing what a role is allowed to do with what it actually used.

- **Permission shrinking**: [Deciding which permissions a role keeps](policy-analysis/permission-shrinking/permission-shrinking.feature) (4)

## Usage Data
Collecting the record of what a role actually did, from files or AWS sources.

- **Action extraction**: [Recognising which IAM actions a role used](usage-data/action-extraction/observed-usage-from-events.feature) (3)
- **Athena queries**: [Querying CloudTrail Lake for a role's usage](usage-data/athena-queries/athena-usage-query.feature) (3)
