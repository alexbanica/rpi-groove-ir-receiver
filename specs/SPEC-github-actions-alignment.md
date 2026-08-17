# GitHub Actions Alignment

Status: Approved

## Purpose

Align this Python package's automation with the shared workspace conventions
while preserving its supported Python matrix and Forgejo publisher behavior.

## Requested Behavior

- Use `.github/workflows/ci.yml` and `.github/workflows/publish.yml` with the
  common `CI` and `Publish` display names.
- Apply least-privilege permissions, immutable external-action pins,
  non-persisted checkout credentials, dependency caching, and per-workflow/per-ref
  concurrency.
- Preserve stable and beta tag publication.
- Enable grouped weekly Dependabot updates for GitHub Actions.

## Scope

- GitHub Actions and Dependabot configuration.
- Existing workflow-focused regression assertions.
- README workflow and action-version documentation.
- Completed-work artifacts.

## Out Of Scope

- Python application, package, release-script, dependency, and runtime behavior.
- Supported Python versions, Forgejo endpoints, credential names, and artifact
  verification.
- Central cross-repository reusable workflows.

## Deterministic Behavior Delivered

- CI retains Python 3.10 and 3.11 validation for `main` pull requests and pushes,
  canceling superseded runs for the same workflow/ref.
- Publication retains stable/beta tag triggers and never cancels an in-progress
  release for the same ref.
- Checkout is pinned to `v7.0.1`, setup-python to `v7.0.0`, checkout credentials
  are not persisted, and pip caches use both requirement files.
- Both workflows have read-only contents permission.
- Dependabot groups GitHub Actions updates weekly.

## Assumptions And Impact

- Exact release validation, quality gates, package build/upload, and public-index
  verification remain owned by `scripts.publish_forgejo`.
- GitHub-hosted runners satisfy the Node 24 runner requirement of the selected
  action releases.

## Validation Performed

- Parsed workflows and Dependabot configuration as YAML and ran shared
  structural assertions.
- Ran `python3 -m unittest tests.test_github_workflows`: 12 tests passed.
- Ran `git diff --check`.

## Validation Skipped

- Full tests, hosted GitHub Actions, and live Forgejo publication/download were
  not run.
- Formal QA and independent review were skipped by `super-agent`.

## Documentation Changes

- Updated README filename, action-pin, concurrency, and Dependabot guidance.
