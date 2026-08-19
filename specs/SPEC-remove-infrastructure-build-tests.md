# Remove infrastructure and build tests

Status: Approved

## Purpose

Align the maintained automated-test suite with the repository's approved
domain-only test policy by removing infrastructure, workflow, packaging, and
release-tool tests.

## Requested behavior

- Remove automated tests for infrastructure adapters.
- Remove automated tests for GitHub Actions workflow structure.
- Remove automated tests for package building, release-version parsing, and
  Forgejo publication orchestration.
- Preserve tests for deterministic pulse normalization and burst-selection
  business rules.

This spec completes the existing cleanup risk recorded by
`specs/SPEC-domain-only-test-policy.md` and supersedes automated non-domain test
requirements in older release and workflow specs. Historical validation records
in those artifacts remain unchanged.

## Scope

- Delete the five existing infrastructure, workflow, package, and release test
  modules under `tests/`.
- Remove the now-unused test-only `PyYAML` development dependency.
- Add completed-work spec and plan artifacts.

## Out of scope

- Production source changes.
- GitHub Actions workflow changes.
- Removing the deterministic pulse normalization and burst-selection tests.
- Rewriting historical specs or plans that accurately record work performed at
  the time.

## Definitions

Infrastructure and build tests include tests of filesystem persistence, workflow
YAML structure, distribution artifacts, release-tag parsing, and publication
orchestration. The retained tests exercise deterministic pulse and burst
business rules without filesystem, GPIO, network, workflow, or packaging
boundaries.

## Inputs and constraints

- The root `AGENTS.md` domain-only test policy is authoritative.
- Non-domain behavior remains validated through static, syntax, build, smoke,
  runtime, hosted, or operator checks appropriate to each future change.
- Existing historical specification references are records, not active test
  files, and are preserved.

## Deterministic behavior delivered

- `tests/test_json_pulse_persistence.py` is removed as an infrastructure-adapter
  test.
- `tests/test_github_workflows.py` is removed as a workflow/configuration test.
- `tests/test_package_artifacts.py`, `tests/test_publish_forgejo.py`, and
  `tests/test_release_version.py` are removed as packaging and release-tool
  tests.
- `requirements-dev.txt` no longer installs `PyYAML`, whose only active source
  consumer was the removed workflow test.
- The remaining discovered suite contains only pulse normalization and burst
  selection tests.

## Assumptions

Pulse normalization and burst selection are treated as deterministic domain
business rules even though their current implementations are located under the
application-services package. Their tests remain within the user's requested
infrastructure/build-test removal boundary.

## Impact

CI no longer maintains automated assertions for infrastructure, workflow, or
release/build tooling. Failures in those areas must be detected by the
non-automated-test validation methods required by `AGENTS.md`. Production and
release behavior are unchanged.

## Validation performed

- Enumerated the remaining `tests/test_*.py` files.
- Ran the remaining discovered unittest suite with Python 3.12.
- Confirmed removed test module names no longer exist under `tests/`.
- Ran `git diff --check`.

## Validation skipped

- Infrastructure, workflow, package, and release tests because they were the
  prohibited artifacts removed by this change.
- Production build, hosted Actions, live Forgejo publication, QA, and code
  review.

## Documentation changes

This approved completed-work spec and its matching plan record the cleanup.
Historical artifacts were not rewritten.
