# Changelog

All notable changes to this project are documented here. This file is
maintained automatically by [release-please](https://github.com/googleapis/release-please)
from Conventional Commit messages — do not edit it by hand.

## 0.1.0 (2026-07-29)


### Features

* add --open-pr to commit the tf-diff and open a PR ([7c76ac5](https://github.com/fabiocicerchia/iam-shrink/commit/7c76ac5390e64cb02104246d1733ab1ddb7f3418))
* add built-in Athena/CloudTrail Lake query runner ([7f7ac67](https://github.com/fabiocicerchia/iam-shrink/commit/7f7ac67695ba8e4fefb1ebec7f0c3fcce2573f85))
* add install.sh one-liner installer ([c1ede9b](https://github.com/fabiocicerchia/iam-shrink/commit/c1ede9ba980f4c64fb4de9eccdb38ee3cdd7329f))
* cross-check removable actions against IAM Access Analyzer ([0b2f072](https://github.com/fabiocicerchia/iam-shrink/commit/0b2f0724cd70c94563bf4ad59d77b43d1eb9825b))
* resource-level narrowing from CloudTrail event resources ([89f3258](https://github.com/fabiocicerchia/iam-shrink/commit/89f32589aeda3002f43cf81bc69870263abec437))


### Bug Fixes

* restore executable bit and align codeql-action versions ([#11](https://github.com/fabiocicerchia/iam-shrink/issues/11)) ([5f88903](https://github.com/fabiocicerchia/iam-shrink/commit/5f88903b20623a585ab0cdb6185af46dae34892e))


### Documentation

* add GitHub Pages site, trim completed roadmap items from README ([98e4c55](https://github.com/fabiocicerchia/iam-shrink/commit/98e4c55e1fed78d68e323b3dd27761ffef48ffde))
* add missing README badges ([b2b1b24](https://github.com/fabiocicerchia/iam-shrink/commit/b2b1b2418f49dc5d8d4a1d5c3fd4cc49d4d3c3ca))
* remove the broken FOSSA badge ([b6178c8](https://github.com/fabiocicerchia/iam-shrink/commit/b6178c833fb74b96f1e5b0df712ed60a5ffa37b1))

## [0.1.0] - 2026-07-14

- Initial release: CloudTrail usage → minimized IAM policies as a report,
  JSON policy, or Terraform diff.
