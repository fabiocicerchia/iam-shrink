# iam-shrink

[![CI](https://github.com/fabiocicerchia/iam-shrink/actions/workflows/ci.yml/badge.svg)](https://github.com/fabiocicerchia/iam-shrink/actions/workflows/ci.yml)
[![Security](https://github.com/fabiocicerchia/iam-shrink/actions/workflows/security.yml/badge.svg)](https://github.com/fabiocicerchia/iam-shrink/actions/workflows/security.yml)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![OpenSSF Scorecard](https://api.securityscorecards.dev/projects/github.com/fabiocicerchia/iam-shrink/badge)](https://securityscorecards.dev/viewer/?uri=github.com/fabiocicerchia/iam-shrink)
[![FOSSA Status](https://app.fossa.com/api/projects/git%2Bgithub.com%2Ffabiocicerchia%2Fiam-shrink.svg?type=shield)](https://app.fossa.com/projects/git%2Bgithub.com%2Ffabiocicerchia%2Fiam-shrink?ref=badge_shield)
[![Release](https://img.shields.io/github/v/release/fabiocicerchia/iam-shrink)](https://github.com/fabiocicerchia/iam-shrink/releases)

**CloudTrail usage → minimized IAM policies as Terraform diffs.** Compares
what a role is *allowed* to do with what it *actually did* over an
observation window, narrows wildcards to observed actions, and emits a
reviewable Terraform snippet — the "usage → PR" loop IAM never had.

```console
$ iam-shrink analyze my-app-role --usage q3-events.json
allowed patterns: 4, used actions: 3

KEEP (3):
  ✓ s3:GetObject
  ✓ s3:PutObject
  ✓ sqs:SendMessage

REMOVE (1):
  ✗ dynamodb:*

$ iam-shrink analyze my-app-role --usage q3-events.json \
    --format tf-diff > shrink.tf
```

## Install

```sh
curl -fsSL https://raw.githubusercontent.com/fabiocicerchia/iam-shrink/main/install.sh | bash
```

Or with pipx directly:

```sh
pipx install git+https://github.com/fabiocicerchia/iam-shrink
```

## Getting usage data

Export `{eventSource, eventName}` pairs for the role from CloudTrail — e.g.
CloudTrail Lake / Athena:

```sql
SELECT eventsource AS eventSource, eventname AS eventName
FROM cloudtrail_logs
WHERE useridentity.sessioncontext.sessionissuer.arn LIKE '%my-app-role'
  AND eventtime > date_add('day', -90, now())
GROUP BY 1, 2
```

## Honest caveats (IAM is a swamp)

- CloudTrail doesn't log **data events** by default (S3 object ops, etc.) —
  enable them or the shrink will over-remove; review the diff, always.
- Resource-level narrowing is not attempted yet (`Resource: "*"` kept) —
  action narrowing first, resources are phase 2.
- Non-CloudTrail-visible actions (some `List`/`Describe`) need an allowlist.

## Status & roadmap

- [x] Usage mapping, wildcard narrowing, report / JSON policy / TF diff
- [ ] Built-in Athena/CloudTrail Lake query runner (`--athena-table`)
- [ ] IAM Access Analyzer cross-check (their unused-access findings as input)
- [ ] Resource-level narrowing from event resources
- [ ] `--open-pr` mode

## Documentation

Full docs live in [`docs/`](docs/). Runnable examples live in
[`examples/`](examples/).

## Development

`make dev && make setup`, then `make test` / `make lint`. See
[CONTRIBUTING.md](CONTRIBUTING.md).

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). By participating you agree to the
[Code of Conduct](CODE_OF_CONDUCT.md).

## Security

Found a vulnerability? See [SECURITY.md](SECURITY.md) — please don't open a
public issue.

## License

Apache 2.0 — see [LICENSE](LICENSE).
