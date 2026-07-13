# Architecture

## Overview

iam-shrink compares what an IAM role is *allowed* to do (its policy's action
patterns) with what it *actually did* over an observation window (CloudTrail
usage), then narrows wildcards to the observed actions and emits the result.

## Components

- **Usage loader** — reads the `{eventSource, eventName}` pairs and maps them
  to IAM action names (`s3.amazonaws.com` + `GetObject` → `s3:GetObject`).
- **Matcher** — expands the policy's allowed patterns and intersects them with
  observed actions to decide KEEP vs REMOVE.
- **Renderer** — emits a human report, a minimized JSON policy, or a
  Terraform diff (`--format`).

## Data flow

CloudTrail export → usage loader → matcher (allowed ∩ used) → renderer.

## Decisions

Record significant choices here (or in a `docs/adr/` folder if they pile up).
See the README's "Honest caveats" for current scope limits (data events,
resource-level narrowing).
