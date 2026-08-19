# Forgejo install dependency resolution

Status: Approved

## Purpose

Ensure the published `rpi-groove-ir-receiver` wheel can be installed
anonymously from Forgejo together with its public Python dependencies.

## Requested behavior

The public installation command must retrieve `rpi-groove-ir-receiver` from
the Forgejo package index and allow pip to retrieve dependencies unavailable
there from public PyPI. Release verification must exercise that same
dependency-resolving installation path rather than treating a dependency-free
wheel download as proof that the package can be installed.

This spec supersedes the Forgejo-only install instruction and the
dependency-free post-publish verification behavior in
`specs/SPEC-forgejo-pypi-tag-publishing.md`. All other approved release
behavior remains unchanged.

## Scope

- Correct the public Forgejo installation command in `README.md`.
- Strengthen post-publication verification in `scripts/publish_forgejo.py`.
- Retain the existing exact wheel metadata verification.

## Out of scope

- Publishing third-party dependencies to Forgejo.
- Changing package dependencies or versions.
- Changing Forgejo credentials, visibility, or upload behavior.
- Adding or maintaining automated release-script tests, which the repository's
  domain-only test policy forbids.

## Inputs and constraints

- Forgejo remains the primary index for `rpi-groove-ir-receiver`.
- Public PyPI is an additional index for dependencies absent from Forgejo.
- Anonymous installation must select the published project wheel and must not
  reuse pip's cache.
- The existing credential-free wheel download and metadata validation remain
  after the install check.

## Deterministic behavior delivered

The documented command supplies both the Forgejo package index and public
PyPI. After upload, the release publisher installs the exact published version
into an isolated temporary target, requires a wheel for
`rpi-groove-ir-receiver`, resolves its dependencies through public PyPI,
disables pip's cache, and supplies no credentials. It then retains the existing
credential-free project-wheel download and name/version/content validation.

## Assumptions

`rpi-groove-ir-receiver` is published only in the configured Forgejo index,
while its third-party dependencies are available from public PyPI. The
GitHub-hosted runner can reach both indexes and build any dependency that does
not provide a compatible wheel.

## Impact

Operators no longer receive dependency-resolution failures solely because the
Forgejo-only install command replaced pip's public PyPI index. A release fails
its post-publish check when the project wheel is downloadable but its declared
dependencies cannot be resolved and installed.

## Validation performed

- Compiled `scripts/publish_forgejo.py` with Python 3.12.
- Inspected the public-install command structure and credential-clean subprocess
  environment statically.
- Parsed `.github/workflows/publish.yml` as YAML.
- Ran `git diff --check`.

## Validation skipped

- Live installation from Forgejo and public PyPI.
- Hosted GitHub Actions execution and package publication.
- Ruff, because it is not installed in the available Python environments.
- Automated tests, code review, and QA.

## Documentation changes

`README.md` now documents the dependency index and why it is required, and it
describes the strengthened post-publication verification.
