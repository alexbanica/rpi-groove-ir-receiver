# Spec: Remove the Python 3.9 CI Check

## Metadata

- Spec ID: `SPEC-REMOVE-PYTHON-3-9-CI-CHECK`
- Status: Approved
- Delivery Mode: Super Agent, auto-approved after implementation
- Authoring Date: `2026-08-17`

## Purpose

Remove the redundant Python 3.9 job from the GitHub Actions CI matrix while
retaining the package's declared Python 3.9 runtime compatibility.

## Requested Behavior

- Pull requests to `main` and pushes to `main` run CI on Python 3.10 and 3.11.
- CI does not create a Python 3.9 matrix job.
- The package continues to declare `python_requires >= 3.9`.

## Scope

- `.github/workflows/ci.yml`
- `tests/test_github_workflows.py`
- `README.md`
- Post-change spec and plan artifacts for this direct execution

## Out of Scope

- Changing `setup.py` package compatibility metadata or classifiers.
- Changing Ruff's Python target.
- Changing the Forgejo publishing workflow or release package behavior.
- Running a hosted GitHub Actions workflow or publishing a package.

## Inputs and Constraints

- The existing pull-request delivery branch and linked implementation worktree
  are reused as explicitly requested.
- Existing IR receiver behavior and architecture invariants remain unchanged.
- Validation is limited to commands expected to complete within ten seconds.
- QA and independent code review are skipped by the `super-agent` workflow.

## Deterministic Behavior Delivered

- The CI matrix contains exactly Python 3.10 and Python 3.11.
- A workflow contract test asserts that Python 3.9 is absent.
- Maintainer documentation names the final two-version CI matrix.

## Assumptions

- "No need for 3.9 check" refers to the GitHub CI matrix only, not to dropping
  Python 3.9 package compatibility.

## Impact

- Each CI event runs two matrix jobs instead of three.
- Package installation and runtime compatibility declarations are unchanged.

## Validation Performed

- `python3 -m unittest tests.test_github_workflows` passed with 12 tests.
- `git diff --check` passed.

## Validation Skipped

- Full unit-test suite.
- Ruff lint across the repository.
- Hosted GitHub Actions execution.
- Live Forgejo publication and anonymous package download.
- QA phase and independent code review.

## Documentation Changes

- `README.md` now documents Python 3.10 and 3.11 as the CI matrix.
