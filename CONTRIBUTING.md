# Contributing

Thanks for taking the time to contribute!

## Getting started

1. Fork and clone the repo.
1. Install dev tooling and hooks: `make dev && make setup`
   (`make setup` wires up pre-commit / the gitleaks pre-commit hook).
1. Create a branch: `git checkout -b feat/short-description`.

## Making changes

- Keep changes focused; one logical change per PR.
- Update `docs/` and `examples/` when behavior changes.
- Ensure `make lint` and `make test` pass; CI (`code-quality` + `security`)
  must be green.

Don't edit `CHANGELOG.md` by hand — it's generated from commit messages by
release-please (see [Releases](#releases)).

## Commit messages

Use [Conventional Commits](https://www.conventionalcommits.org/): `feat:`,
`fix:`, `docs:`, `chore:`, etc. This keeps history readable and drives the
version bump: `fix:` → patch, `feat:` → minor, `feat!:` or a
`BREAKING CHANGE:` footer → major.

## Releases

Releases are automated by [release-please](.github/workflows/release.yml);
you don't tag or edit the changelog manually.

1. Merge `feat:`/`fix:` PRs into `main` as normal — **no tag is created**.
1. release-please keeps an open **release PR** ("chore: release X.Y.Z"),
   recalculating the next version and changelog on every merge.
1. When you're ready to ship, **merge the release PR** — that (and only that)
   bumps the version in `pyproject.toml`, creates the `vX.Y.Z` tag and the
   GitHub Release, and (if `PUBLISH_TO_PYPI` is set) publishes to PyPI.

So `main` is not released per-commit: changes accumulate into the release PR,
and merging it is the deliberate release step.

## Pull requests

Fill out the PR template, link related issues, and request review. Be kind.
