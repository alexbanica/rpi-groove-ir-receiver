# Forgejo install dependency resolution plan

Status: Approved

## Spec reference

`specs/SPEC-forgejo-install-dependency-resolution.md`

## Affected files

- `README.md`
- `scripts/publish_forgejo.py`
- `specs/SPEC-forgejo-install-dependency-resolution.md`
- `specs/PLAN-forgejo-install-dependency-resolution.md`

## Implementation performed

1. Added public PyPI as the documented extra dependency index while retaining
   Forgejo as the project package index.
2. Explained the separation between the Forgejo-hosted project and its public
   dependencies.
3. Added an exact-version anonymous install into an isolated temporary target
   after upload.
4. Required a wheel for `rpi-groove-ir-receiver`, disabled pip's cache, resolved
   dependencies from public PyPI, and used the existing credential-clean child
   environment.
5. Retained the separate exact Forgejo wheel download and metadata/content
   validation.
6. Recorded the delivered behavior in this approved spec and plan.

## Validation run

- Python 3.12 compilation for `scripts/publish_forgejo.py`.
- YAML parsing for `.github/workflows/publish.yml`.
- Static inspection of the modified pip commands, index ordering, and clean
  environment boundary.
- `git diff --check`.

## Validation skipped

- Live Forgejo/PyPI installation, hosted Actions, and publication.
- Ruff because it is not installed in the available Python environments.
- Automated tests because release tooling is outside deterministic domain source
  logic under the repository test policy.

## QA and code review

QA and code review were skipped as required by `$super-agent`.

## Documentation updates

The README public installation example, dependency-index explanation, and
post-publication verification description were updated.

## Staging and delivery status

All accepted in-scope paths are staged before delivery. The user requested the
complete staged set be committed directly on `main` and pushed to `origin/main`.

## Residual risk

Live index availability, platform dependency compatibility, and hosted workflow
behavior remain unverified until the corrected installation path runs against
Forgejo and public PyPI.
