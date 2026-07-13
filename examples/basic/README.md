# Basic Example

What it shows: shrinking a role to the three actions it actually used
(`s3:GetObject`, `s3:PutObject`, `sqs:SendMessage`) from a small CloudTrail
usage sample, and rendering the change as a Terraform diff.

## Run

```sh
# Requires AWS credentials able to read the role's policies (get_role_policy).
iam-shrink analyze my-app-role --usage usage.json
iam-shrink analyze my-app-role --usage usage.json --format tf-diff
```

`usage.json` in this folder is the exported `{eventSource, eventName}` list —
swap it for your own CloudTrail export.
