# Changelog

All notable changes to this project are documented here. This file is
maintained automatically by [release-please](https://github.com/googleapis/release-please)
from Conventional Commit messages — do not edit it by hand.

## [0.3.1](https://github.com/fabiocicerchia/iam-shrink/compare/v0.3.0...v0.3.1) (2026-09-11)


### Bug Fixes

* **release:** let the release PR carry a token that isn't GITHUB_TOKEN ([#93](https://github.com/fabiocicerchia/iam-shrink/issues/93)) ([8795af0](https://github.com/fabiocicerchia/iam-shrink/commit/8795af0aa1aac084ef5ab2d1c50389baa631d727))

## [0.3.0](https://github.com/fabiocicerchia/iam-shrink/compare/v0.2.2...v0.3.0) (2026-09-10)


### Features

* **packaging:** ship a man page with the wheel ([#86](https://github.com/fabiocicerchia/iam-shrink/issues/86)) ([6d1da46](https://github.com/fabiocicerchia/iam-shrink/commit/6d1da4698e83e2a921961fe1a7c6ac1ac0f5a310))


### Bug Fixes

* **release:** grant id-token on the job that calls the signing workflow ([#90](https://github.com/fabiocicerchia/iam-shrink/issues/90)) ([4fbfa6c](https://github.com/fabiocicerchia/iam-shrink/commit/4fbfa6c66beb3e7e310a782aa038b03b3b83d15d))

## [0.2.2](https://github.com/fabiocicerchia/iam-shrink/compare/v0.2.1...v0.2.2) (2026-09-08)


### Bug Fixes

* **ci:** pin the editorconfig-checker binary version ([#67](https://github.com/fabiocicerchia/iam-shrink/issues/67)) ([989594c](https://github.com/fabiocicerchia/iam-shrink/commit/989594c6e190dc332a470700990d76f316f3be78))

## [0.2.1](https://github.com/fabiocicerchia/iam-shrink/compare/v0.2.0...v0.2.1) (2026-08-29)

### Bug Fixes

- unblock quality and clear the Scorecard pinned-dependencies finding ([#52](https://github.com/fabiocicerchia/iam-shrink/issues/52)) ([809672e](https://github.com/fabiocicerchia/iam-shrink/commit/809672ed68439841be4cc0203cf5fca8eec6f27f))

## [0.2.0](https://github.com/fabiocicerchia/iam-shrink/compare/v0.1.2...v0.2.0) (2026-08-25)

### Features

- **docs:** build the docs site in Actions and drop Read the Docs ([#43](https://github.com/fabiocicerchia/iam-shrink/issues/43)) ([7c43803](https://github.com/fabiocicerchia/iam-shrink/commit/7c438039f814856ff44a91e35fcfbf8392d67eb2))

### Bug Fixes

- **ci:** compute the next release PR after the draft is published ([#40](https://github.com/fabiocicerchia/iam-shrink/issues/40)) ([5923507](https://github.com/fabiocicerchia/iam-shrink/commit/5923507d1fb376a46062622851f0f549f7376b59))

## [0.1.2](https://github.com/fabiocicerchia/iam-shrink/compare/v0.1.1...v0.1.2) (2026-08-13)

### Bug Fixes

- security and code-quality findings ([#32](https://github.com/fabiocicerchia/iam-shrink/issues/32)) ([c5b4c3b](https://github.com/fabiocicerchia/iam-shrink/commit/c5b4c3b609729209bef5e29244620c742e7375f8))

## [0.1.1](https://github.com/fabiocicerchia/iam-shrink/compare/v0.1.0...v0.1.1) (2026-08-06)

### Bug Fixes

- **pre-commit:** stop check-yaml failing on Helm templates and multi-doc manifests ([8cfb199](https://github.com/fabiocicerchia/iam-shrink/commit/8cfb1995cca024ce84972d3e6009bfac1bab13a0))
- **security:** skip the SARIF upload on private repos ([091e284](https://github.com/fabiocicerchia/iam-shrink/commit/091e284ffea5cd75843f5df61bf5c78430f5c991))

## [0.1.0] - 2026-07-14

- Initial release: CloudTrail usage → minimized IAM policies as a report,
  JSON policy, or Terraform diff.
