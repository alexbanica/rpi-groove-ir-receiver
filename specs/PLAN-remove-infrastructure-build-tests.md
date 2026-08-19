# Remove infrastructure and build tests plan

Status: Approved

## Spec reference

`specs/SPEC-remove-infrastructure-build-tests.md`

## Affected files

- `requirements-dev.txt`
- `tests/test_github_workflows.py` (deleted)
- `tests/test_json_pulse_persistence.py` (deleted)
- `tests/test_package_artifacts.py` (deleted)
- `tests/test_publish_forgejo.py` (deleted)
- `tests/test_release_version.py` (deleted)
- `specs/SPEC-remove-infrastructure-build-tests.md`
- `specs/PLAN-remove-infrastructure-build-tests.md`

## Implementation performed

1. Classified every existing test by its production ownership boundary.
2. Deleted the infrastructure persistence test.
3. Deleted the GitHub Actions workflow/configuration test.
4. Deleted package artifact, release-version, and Forgejo publication tests.
5. Preserved deterministic pulse normalization and burst-selection tests.
6. Removed `PyYAML` from development requirements because no active source uses
   it after deleting the workflow test.
7. Recorded the delivered cleanup in approved completed-work artifacts.

## Validation run

- Remaining test-file inventory.
- Remaining discovered unittest suite with Python 3.12.
- Structural search for removed test module names under `tests/`.
- `git diff --check`.

## Validation skipped

- The deleted non-domain tests.
- Production build and live infrastructure/release validation because production
  behavior was not changed.

## QA and code review

QA and independent code review were skipped as required by `$super-agent`.

## Documentation updates

Added this completed-work plan and its matching approved spec. Historical specs
and plans remain unchanged as records of their original deliveries.

## Staging and delivery status

All accepted in-scope changes are staged. Commit and push were not requested for
this invocation, so the staged set remains uncommitted and unpushed.

## Residual risk

Infrastructure, workflow, packaging, and release regressions no longer have
repository automated-test coverage. Future changes in those areas depend on the
static, syntax, build, smoke, hosted, live, or operator validation appropriate
to their boundary.
