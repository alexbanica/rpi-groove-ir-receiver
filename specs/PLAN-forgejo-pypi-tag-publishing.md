# Plan: Forgejo PyPI Tag Publishing and GitHub CI Gates

## Metadata

- Plan ID: `PLAN-FORGEJO-PYPI-TAG-PUBLISHING`
- Status: Approved
- Authoring Date: `2026-08-16`
- Approved Spec: `specs/SPEC-forgejo-pypi-tag-publishing.md`
- Expected Base Branch: `main`
- Expected Base Commit: `881331787cea8927ed2b06fceccd1f1c84b98851`
- Implementation Delivery Branch: `feature/forgejo-pypi-tag-publishing`
- Worktree Task Slug: `forgejo-pypi-tag-publishing`
- Implementation Worktree:
  `~/.herdr/worktrees/rpi-groove-ir-receiver/forgejo-pypi-tag-publishing`

## 1. Objective

Implement the approved Forgejo PyPI tag-publishing and GitHub CI contract without
changing IR receiver product behavior. Use the current
`homebridge-simple-ir-fan` release implementation as a safety-pattern reference,
while implementing Python-native packaging, Twine authentication, PEP 440 beta
versions, and pip-based public verification.

## 2. Implementation Constraints

- Implementation must begin only through `$implement` after its clean-context
  gate is satisfied.
- Implementation must ingest only applicable instructions, this approved plan,
  the approved spec, named files, and minimal local edit patterns. It must not
  repeat product, architecture, or planning research.
- Work must stay within the approved spec and this plan.
- If implementation reveals a material spec mismatch or missing behavior, stop
  and request a spec/plan amendment.
- Preserve all unrelated user changes.
- Workers must not create or manage worktrees or branches, commit, or push.
- Test-focused assignments must use the `test-writer` agent definition.
- Production and follow-up fix assignments must use the `developer` agent
  definition.
- Review assignments must use clean-context `code-reviewer` agents and must not
  implement fixes.
- The main agent owns worktree/branch handling, integration, QA, documentation
  acceptance, staging, commit, and push.

## 3. Branch and Worktree Procedure

1. In the invoking checkout, verify:
   - repository root name is `rpi-groove-ir-receiver`;
   - `main` and `origin/main` both resolve to expected base commit
     `881331787cea8927ed2b06fceccd1f1c84b98851`;
   - `feature/forgejo-pypi-tag-publishing` does not already conflict locally or
     on `origin`;
   - the only known task changes are the approved spec and plan artifacts;
   - no unrelated state would be overwritten.
2. Create `~/.herdr/worktrees/rpi-groove-ir-receiver` when absent.
3. Verify the task path exactly matches the repository name and task slug.
4. Create or reuse the planned worktree in detached-HEAD state at the expected
   base. Stop on identity, cleanliness, base, or path conflict.
5. Materialize the exact approved spec and plan in the detached worktree before
   other task edits. Preserve their approved contents and statuses.
6. Do not create the delivery branch until implementation has reached either
   DRAFT delivery or the Definition of Done.
7. At delivery, create exactly
   `feature/forgejo-pypi-tag-publishing` from the detached worktree.
8. After the artifacts are committed in the planned worktree, compare the
   invoking-checkout copies byte-for-byte with the committed copies. Remove only
   the duplicate task-created untracked copies from the invoking checkout; do
   not touch unrelated paths.

## 4. Intended Files and Ownership Boundaries

### Approved Artifacts

- `specs/SPEC-forgejo-pypi-tag-publishing.md`
- `specs/PLAN-forgejo-pypi-tag-publishing.md`

### Packaging and Tooling

- `setup.py`
  - accept an explicitly supplied, already-validated release version for an
    ephemeral tagged build;
  - retain the current local/default package version when no release override is
    supplied;
  - retain package name, dependencies, package discovery, and Python requirement.
- `pyproject.toml`
  - define the setuptools build backend;
  - define the repository Ruff configuration and lint scope.
- `requirements-dev.txt`
  - pin the CI/release tools required by the plan, including Ruff, build, and
    Twine;
  - keep hardware/runtime dependencies out of ordinary CI unless needed by a
    deterministic test.

### Release Support

- `scripts/__init__.py`
- `scripts/release_version.py`
  - exact stable/beta tag parsing;
  - PEP 440 conversion;
  - deterministic rejection errors.
- `scripts/package_artifacts.py`
  - wheel/sdist discovery and metadata/content inspection;
  - exact package-name/version assertions;
  - required/disallowed content assertions.
- `scripts/publish_forgejo.py`
  - release orchestration and command sequencing;
  - lint, test, build, Twine validation, upload, cleanup, and public download
    verification;
  - token isolation to the Twine upload subprocess.

### GitHub Actions

- `.github/workflows/ci.yml`
  - pull-request-to-`main` and push-to-`main` triggers;
  - `actions/checkout@v7`, `actions/setup-python@v6`, explicit supported Python
    versions, dependency setup, separately named Ruff and unit-test steps;
  - read-only contents permission and no Forgejo secret reference.
- `.github/workflows/publish-forgejo.yml`
  - coarse numeric tag trigger followed by exact script validation;
  - tagged-ref checkout, read-only contents permission, per-ref non-canceling
    concurrency, supported Python setup, release-tool installation, and publisher
    invocation;
  - `RELEASE_TAG` from `github.ref_name`;
  - only the upload operation receives
    `secrets.FORGEJO_PACKAGE_TOKEN` through the publisher boundary.

### Tests

- `tests/test_release_version.py`
- `tests/test_package_artifacts.py`
- `tests/test_publish_forgejo.py`
- `tests/test_github_workflows.py`

### Documentation

- `README.md`
  - CI behavior, supported release tags, PEP 440 beta mapping, token setup,
    public Forgejo install endpoint, trusted release procedure, duplicate-version
    behavior, troubleshooting, and live-validation boundary.

### Files Expected to Remain Unchanged

- `requirements.txt`
- all existing `ir_receiver/**` product files;
- all existing product-behavior tests except for mechanical lint corrections if
  Ruff identifies an in-scope baseline violation.

Any required path outside this list is a plan conflict unless it is a generated,
ignored validation artifact that is removed before delivery.

## 5. Test-First and Development Execution Graph

Each subagent assignment below is bounded to no more than five minutes of active
work. The main agent must supervise elapsed time, stop a timed-out assignment,
record completed/partial work, changed files, validation, blockers, and remaining
work, then split the remainder before reassignment. A timed-out assignment must
not be retried at the same size.

### Unit T-VER — Release Version Contract Tests

- Type: test-first, `test-writer`.
- Boundary: stable/beta tag parsing, PEP 440 mapping, and malformed-tag
  rejection.
- Owned file: `tests/test_release_version.py`.
- Dependencies: none.
- Acceptance:
  - covers exact `X.Y.Z` and `X.Y.Z-betaT` acceptance;
  - covers `betaT` to `bT` mapping;
  - covers every rejected form named by the approved spec;
  - proves deterministic errors and no external commands.
- Validation:
  `python -m unittest tests.test_release_version`.
- Assignment: one clean-context test-writer, maximum five minutes.

### Unit T-ART — Distribution Inspection Tests

- Type: test-first, `test-writer`.
- Boundary: wheel/sdist discovery, metadata checks, and content allow/deny rules.
- Owned file: `tests/test_package_artifacts.py`.
- Dependencies: none.
- Acceptance:
  - uses temporary synthetic wheel/sdist fixtures;
  - covers missing/duplicate artifact, wrong name/version, required-content, and
    disallowed-content failures;
  - performs no package build or network call.
- Validation:
  `python -m unittest tests.test_package_artifacts`.
- Assignment: one clean-context test-writer, maximum five minutes.

### Unit T-PUB — Publisher Orchestration Tests

- Type: test-first, `test-writer`.
- Boundary: release gate ordering, subprocess environment isolation, cleanup,
  upload, failure propagation, and public verification.
- Owned file: `tests/test_publish_forgejo.py`.
- Dependencies: none; fake command/process fixtures must remain local to this
  file.
- Acceptance:
  - covers missing tag/token, gate ordering, each subprocess failure, secret
    scoping, cleanup, duplicate upload failure, and unauthenticated exact-version
    verification;
  - never performs a live upload or exposes a token.
- Validation:
  `python -m unittest tests.test_publish_forgejo`.
- Assignment: one clean-context test-writer, maximum five minutes.

### Unit T-WF — Workflow Contract Tests

- Type: test-first, `test-writer`.
- Boundary: CI and publish workflow trigger/security/step structure.
- Owned file: `tests/test_github_workflows.py`.
- Dependencies: none.
- Acceptance:
  - covers PR/push `main` CI triggers and named lint/test steps;
  - rejects token references in CI;
  - covers tag-only publishing, exact tag checkout, permissions, concurrency,
    version input, secret mapping, and absence of branch/PR publish triggers.
- Validation:
  `python -m unittest tests.test_github_workflows`.
- Assignment: one clean-context test-writer, maximum five minutes.

### Unit D-TOOL — Build and Lint Tooling

- Type: configuration-only development; test-first not applicable because this
  unit defines build-tool and linter configuration rather than executable
  behavior.
- Agent: `developer`.
- Owned files: `pyproject.toml`, `requirements-dev.txt`.
- Dependencies: none.
- Acceptance:
  - setuptools backend is explicit;
  - development tools are pinned and installable on the CI Python versions;
  - Ruff covers source, scripts, and tests without weakening correctness rules to
    hide real violations.
- Validation:
  - `python -m pip install -r requirements-dev.txt` in an isolated environment;
  - `ruff check ir_receiver scripts tests setup.py` after dependent files exist.
- Assignment: one clean-context developer, maximum five minutes.

### Unit D-VER — Release Version Implementation

- Type: behavior-changing development, `developer`.
- Boundary: tag validation, canonical version mapping, and build-version input.
- Owned files: `scripts/__init__.py`, `scripts/release_version.py`, `setup.py`.
- Dependencies: T-VER completed.
- Acceptance:
  - T-VER passes;
  - tag parsing is exact and side-effect free;
  - `setup.py` consumes only an explicit validated release override and otherwise
    retains the current default version;
  - no source-history mutation is required for a release build.
- Validation:
  `python -m unittest tests.test_release_version` and `python setup.py check`.
- Assignment: one clean-context developer, maximum five minutes.

### Unit D-ART — Distribution Inspection Implementation

- Type: behavior-changing development, `developer`.
- Boundary: artifact discovery and package metadata/content verification.
- Owned file: `scripts/package_artifacts.py`.
- Dependencies: T-ART completed and D-VER completed.
- Acceptance:
  - T-ART passes;
  - exactly one wheel and one sdist are accepted;
  - name/version and required/disallowed content checks match the approved spec;
  - no network or credential handling exists in this module.
- Validation:
  `python -m unittest tests.test_package_artifacts`.
- Assignment: one clean-context developer, maximum five minutes.

### Unit D-PUB — Publisher Orchestration Implementation

- Type: behavior-changing development, `developer`.
- Boundary: release sequencing, subprocess execution, auth isolation, cleanup,
  upload, and post-publish public verification.
- Owned file: `scripts/publish_forgejo.py`.
- Dependencies: T-PUB completed, D-VER completed, D-ART completed, and D-TOOL
  completed.
- Acceptance:
  - T-PUB passes;
  - gates execute in approved order;
  - package token is supplied only as Twine's password environment variable for
    upload and is stripped from all other child environments;
  - no token appears in arguments, persistent files, or error messages;
  - exact public package download and metadata verification are credential-free;
  - temporary files are cleaned on success and failure.
- Validation:
  `python -m unittest tests.test_publish_forgejo` plus safe local dry-run/fake
  command validation.
- Assignment: one clean-context developer, maximum five minutes.

### Unit D-WF — GitHub Actions Workflows

- Type: configuration/wiring development, `developer`; test-first is supplied by
  T-WF because workflow structure is deterministic and testable.
- Boundary: CI and tag-publish workflow definitions.
- Owned files: `.github/workflows/ci.yml`,
  `.github/workflows/publish-forgejo.yml`.
- Dependencies: T-WF completed, D-TOOL completed, and D-PUB completed.
- Acceptance:
  - T-WF passes;
  - CI targets PRs and pushes to `main` and exposes separate lint/test steps;
  - release is tag-only, checks out the tag, and invokes the publisher;
  - secret, permissions, and concurrency boundaries match the approved spec.
- Validation:
  `python -m unittest tests.test_github_workflows` plus workflow syntax validation.
- Assignment: one clean-context developer, maximum five minutes.

### Unit D-DOC — Maintainer Documentation

- Type: docs-only development; test-first not applicable because it changes no
  executable behavior.
- Agent: `developer`.
- Owned file: `README.md`.
- Dependencies: D-VER, D-PUB, and D-WF completed.
- Acceptance: every documentation requirement in approved spec section 13 is
  present and matches the final commands, URLs, tag mapping, and secret name.
- Validation: link/command review and `git diff --check`.
- Assignment: one clean-context developer, maximum five minutes.

## 6. Dependency-Aware Scheduling and Concurrency

Execution graph:

```text
T-VER ──> D-VER ──> D-ART ──> D-PUB ──> D-WF ──> D-DOC
T-ART ──────────────^          ^          ^
T-PUB ─────────────────────────┘          |
T-WF ─────────────────────────────────────┘
D-TOOL ────────────────────────^──────────^
```

- Maximum active test-writer concurrency: 3. Start T-VER, T-ART, and T-PUB;
  start T-WF as soon as one slot becomes available.
- Maximum active developer concurrency: 2, only for units whose owned files and
  dependencies do not overlap. D-TOOL may run while completed test units unblock
  D-VER; D-ART, D-PUB, D-WF, and D-DOC are dependency-serialized.
- Maximum active code-reviewer concurrency: 2.
- The main agent must not allow concurrent edits to `setup.py`, publisher/helper
  imports, workflow command names, dependency pins, or README commands when those
  edits depend on unfinished upstream units.
- Shared integration points are the release environment-variable name, publisher
  command, exact URLs, secret name, artifact-validation API, and PEP 440 mapping.
  The main agent serializes and verifies these after each dependent handoff.

## 7. Integration Procedure

After each completed subtask, the main agent must:

1. Inspect the exact changed files and diff.
2. Confirm ownership was respected and no unrelated paths changed.
3. Run the unit's stated focused validation.
4. Record any blocker or approved-artifact mismatch before starting dependents.
5. Reconcile imports, command names, environment-variable names, and URLs at the
   documented shared integration points.
6. Route any implementation fix to a new clean-context developer agent with the
   specific finding and narrow ownership boundary.

The main agent may make only narrow integration corrections within a completed
unit's approved boundary while unrelated ready units are active.

## 8. Independent Review

After all development units and focused tests pass, launch two clean-context
code-reviewer units concurrently. Each is bounded to five minutes and must not
edit files.

### Review R-REL — Release and Packaging Correctness

- Scope: approved spec, approved plan, `setup.py`, `pyproject.toml`,
  `requirements-dev.txt`, `scripts/**`, and release-related tests.
- Findings sought: tag/version mismatches, PEP 440 errors, incorrect package
  contents, credential leakage, command-order bypasses, cleanup gaps, missing
  failure tests, duplicate-version behavior, and unsafe public verification.
- Output: severity-ranked findings with exact file/line evidence and missing
  validation.

### Review R-CI — Workflow, Documentation, and Regression Safety

- Scope: approved spec, approved plan, `.github/workflows/**`, `README.md`,
  workflow tests, and the complete diff for product-scope leakage.
- Findings sought: trigger mismatches, token exposure, excessive permissions,
  tag checkout/concurrency errors, CI gaps, documentation drift, unexpected
  product changes, and approved-artifact mismatches.
- Output: severity-ranked findings with exact file/line evidence and missing
  validation.

If a reviewer reaches five minutes, stop it, preserve its findings, split the
unreviewed scope, and use a clean-context reviewer for the remainder. Route every
accepted finding to a new clean-context developer assignment. Rerun affected
focused validation and obtain targeted reviewer confirmation when material.

## 9. Main-Agent QA and Validation

The main agent owns and must perform final QA. Use isolated temporary directories
and caches under `/tmp` where practical. Do not perform a real upload until the
hosted trusted-tag validation step.

### Deterministic Local Validation

1. Create/use an isolated Python environment and install
   `requirements-dev.txt`.
2. Run Ruff:
   `ruff check ir_receiver scripts tests setup.py`.
3. Run the complete tests:
   `python -m unittest discover -s tests -p 'test_*.py'`.
4. Run packaging metadata validation:
   `python setup.py check`.
5. Build a stable distribution pair with a temporary validated release-version
   override:
   `python -m build`.
6. Run:
   `python -m twine check dist/*`.
7. Inspect the wheel and sdist using the implemented artifact validator; confirm
   exact package name, expected canonical version, required contents, and no
   credential/runtime/generated leakage.
8. Repeat version derivation and metadata validation for a beta tag such as
   `1.2.3-beta1`, expecting package version `1.2.3b1` without uploading it.
9. Run deterministic workflow-structure tests and, when locally available, a
   Forgejo/GitHub Actions-compatible YAML validator.
10. Run `git diff --check`.

### Hosted and Live Validation

1. Confirm GitHub contains repository secret `FORGEJO_PACKAGE_TOKEN` without
   reading or exposing its value.
2. Push the implementation branch and allow GitHub PR/branch CI to demonstrate
   successful named lint and test checks.
3. Only when explicitly authorized as part of implementation delivery, create
   and push one unused trusted stable or beta tag conforming to the approved
   format.
4. Confirm the hosted publish workflow checks out that tag and passes lint,
   tests, build, Twine validation, upload, and unauthenticated public verification.
5. Confirm the exact package version can be downloaded without credentials from
   `https://forgejo.alexlab.nl/api/packages/public/pypi/simple` and inspect its
   metadata.

Creating/pushing a tag and publishing a real package version are external state
changes beyond ordinary implementation delivery. If the user has not explicitly
authorized that live release, do not perform it. Report the hosted/live validation
as not run and deliver DRAFT.

## 10. Documentation and Contract Review

- Confirm README commands use the exact `public` owner endpoints and
  `FORGEJO_PACKAGE_TOKEN` name.
- Confirm beta examples distinguish the Git tag `X.Y.Z-betaT` from Python's
  canonical package version `X.Y.ZbT`.
- Confirm install examples do not embed credentials and do not use
  `--extra-index-url`.
- Confirm the README states duplicate versions cannot be overwritten.
- Confirm no OpenAPI or `.http` artifacts are added because this repository has
  no HTTP API.

## 11. Delivery, Commit, and Push

Unless the user explicitly overrides delivery for the implementation invocation:

1. Reconcile the complete planned worktree with `git status` and classify every
   modified, added, deleted, renamed, and untracked path.
2. Preserve and report unrelated changes; stop if they cannot be separated
   safely.
3. Ensure the approved spec, approved plan, workflows, scripts, tests, tooling,
   packaging metadata, and README are all included.
4. Inspect the unstaged diff, run `git diff --check`, and complete final QA.
5. Create exactly `feature/forgejo-pypi-tag-publishing` from the detached
   worktree only after reaching DRAFT or the Definition of Done.
6. Stage every accepted in-scope path and no unrelated path.
7. Inspect `git diff --cached --name-status`, `git diff --cached --stat`, and the
   complete staged diff.
8. Commit the complete accepted set with:
   - `feature: add Forgejo PyPI tag publishing` when all required deterministic
     and authorized live validation passes; or
   - `feature: DRAFT add Forgejo PyPI tag publishing` when hosted/live publishing,
     review, QA, documentation, or another required gate remains incomplete.
9. Push the exact branch to `origin` and configure its upstream.
10. Verify the local branch is not ahead of its configured upstream.
11. Inspect final worktree `git status` and do not report completion while any
    accepted in-scope change remains outside the commit.
12. Reconcile the invoking checkout as described in section 3 so duplicate
    task-created planning artifacts do not remain untracked there.

The implementation command must not create a pull request, merge the branch,
create a Git tag, or publish a real package unless the user explicitly requests
that additional external state change.

## 12. Completion Report Requirements

The final implementation report must state:

- implemented spec summary;
- code-review and QA issues found;
- findings resolved and unresolved;
- validation run and validation not run;
- stable/beta build evidence;
- hosted CI and live Forgejo publish evidence, or the exact DRAFT gap;
- remaining risks and limitations;
- documentation changes;
- every changed path and its classification;
- commit hash, branch, push/upstream status;
- whether delivery is FINAL or DRAFT;
- skipped, blocked, incomplete, or unvalidated Definition of Done items;
- whether the full Definition of Done was satisfied;
- final main-agent acceptance result.

## 13. Expected Delivery State

- Deterministic local implementation, tests, lint, builds, Twine checks, review,
  QA, documentation, commit, and branch push are required.
- Live tag creation/package publication is not assumed authorized by this plan.
- Without an authorized successful hosted tag run and live public package round
  trip, the expected implementation delivery is DRAFT with all deterministic
  work complete and the exact live validation gap reported.
