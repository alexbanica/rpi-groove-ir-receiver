# PLAN: Emitter publish-credentials alignment

Status: Approved

Spec: `specs/SPEC-emitter-publish-credentials-alignment.md`

## Affected files

- `.github/workflows/publish-forgejo.yml`
- `scripts/publish_forgejo.py`
- `tests/test_github_workflows.py`
- `tests/test_publish_forgejo.py`
- `README.md`
- `specs/SPEC-emitter-publish-credentials-alignment.md`
- `specs/PLAN-emitter-publish-credentials-alignment.md`

## Implementation performed

1. Compared the receiver publishing flow with the emitter's post-release
   credential-source fix.
2. Added the username secret to the receiver's step-scoped publish environment.
3. Required the username in the publisher and mapped it only to Twine's upload
   environment.
4. Extended deterministic workflow and publisher credential-boundary tests.
5. Updated maintainer secret setup documentation.

## Validation

- `python3 -m unittest tests.test_publish_forgejo tests.test_github_workflows`
  passed: 25 tests.
- `python3 -m unittest discover -s tests -p 'test_*.py'` passed: 48 tests.
- `git diff --check` passed.

## Validation skipped

- Ruff could not run: neither the system Python nor the available Python 3.11
  environment has the `ruff` module installed.
- Hosted GitHub Actions and a live Forgejo upload/download were not run.

## QA and review

Skipped by the requested `super-agent` workflow.

## Staging and delivery

All accepted paths are staged after validation. No commit or push is performed
unless separately requested.

## Residual risk

GitHub Actions secret configuration and the live Forgejo upload/download round
trip require a trusted tagged workflow run.
