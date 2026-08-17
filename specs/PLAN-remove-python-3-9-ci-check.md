# Plan: Remove the Python 3.9 CI Check

## Metadata

- Plan ID: `PLAN-REMOVE-PYTHON-3-9-CI-CHECK`
- Status: Approved
- Delivery Mode: Super Agent, auto-approved after implementation
- Authoring Date: `2026-08-17`
- Approved Spec: `specs/SPEC-remove-python-3-9-ci-check.md`

## Affected Files

- `.github/workflows/ci.yml`
- `tests/test_github_workflows.py`
- `README.md`
- `specs/SPEC-remove-python-3-9-ci-check.md`
- `specs/PLAN-remove-python-3-9-ci-check.md`

## Implementation Steps Performed

1. Refreshed `origin/main` and verified the reusable linked worktree at that
   commit before returning to the existing pull-request branch.
2. Removed Python 3.9 from the CI matrix while retaining Python 3.10 and 3.11.
3. Added a parsed-workflow contract assertion for the exact final matrix and
   the absence of a Python 3.9 job.
4. Updated the README CI matrix description.
5. Created these auto-approved completed-work artifacts.
6. Reconciled and staged only the five in-scope paths.
7. Included the staged paths in one scoped commit, pushed the existing delivery
   branch, verified the remote commit, and detached the worktree at that commit.

## Validation Run

- `python3 -m unittest tests.test_github_workflows` passed with 12 tests.
- `git diff --check` passed.

## Validation Skipped

- Full unit-test suite.
- Ruff lint across the repository.
- Hosted GitHub Actions execution.
- Live Forgejo publication and anonymous package download.

## QA and Review

- QA phase: skipped by the `super-agent` workflow.
- Independent code review: skipped by the `super-agent` workflow.

## Documentation

- Updated `README.md` to list Python 3.10 and 3.11 for CI.

## Delivery Status

- Staging: all five in-scope paths included; no unrelated path included.
- Commit: one scoped commit on `feature/forgejo-pypi-tag-publishing`.
- Push: delivery commit pushed to `origin/feature/forgejo-pypi-tag-publishing`.
- Worktree: detached at the verified pushed commit after delivery.
- Invoking checkout: unchanged and clean; no spec or plan was transferred from
  it for this invocation.

## Residual Risk

- The updated matrix is structurally validated locally but is not yet confirmed
  by a hosted GitHub Actions run.
- The default Definition of Done is not fully satisfied because QA, independent
  review, and hosted validation were intentionally skipped.
