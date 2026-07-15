# Getting Started

## Prerequisites

- Python 3.10+
- CloudTrail usage data for the role you want to shrink (see below).

## Setup

```sh
pip install iam-shrink        # or: make dev  (editable, with dev deps)
```

## Run

```sh
iam-shrink analyze my-app-role --usage q3-events.json
iam-shrink analyze my-app-role --usage q3-events.json \
    --format tf-diff > shrink.tf
```

`--usage` takes a JSON file of `{eventSource, eventName}` pairs exported from
CloudTrail. See the [README](../README.md#getting-usage-data) for the query,
and [`examples/basic/`](../examples/basic/README.md) for a runnable sample.

Or skip the export step and query CloudTrail Lake directly:

```sh
iam-shrink analyze my-app-role \
    --athena-table cloudtrail_logs --athena-output s3://my-bucket/athena-out/
```
