# Spec: Forgejo PyPI Tag Publishing and GitHub CI Gates

## Metadata

- Spec ID: `SPEC-FORGEJO-PYPI-TAG-PUBLISHING`
- Status: Approved
- Authoring Date: `2026-08-16`

## 1. Purpose

Add deterministic GitHub Actions checks for pull requests and updates to `main`,
and publish tagged Python package releases to the public Forgejo PyPI registry
only after all release validation succeeds.

## 2. Problem

The repository currently has no GitHub Actions workflows, no configured linter,
and no automated package publishing path. Unit tests are documented, but pull
requests and updates to `main` are not checked automatically. Creating a Git tag
does not build, validate, publish, or verify a Python distribution.

## 3. Scope

### In Scope

- GitHub Actions CI for pull requests targeting `main`.
- GitHub Actions CI for pushes to `main`, including merged pull requests and
  direct pushes.
- Deterministic Ruff linting and the existing unit-test suite as mandatory CI
  gates.
- A separate GitHub Actions release path triggered by supported numeric Git
  tags.
- Tag validation, tag-to-Python-version mapping, package build and validation,
  authenticated Forgejo upload, and unauthenticated post-publish verification.
- Automated tests for the release contract and workflow structure.
- Maintainer documentation for CI, supported tags, credentials, publishing, and
  public installation.

### Out of Scope

- Publishing to pypi.org or any registry other than the Forgejo PyPI registry.
- npm package behavior, npm dist-tags, or npm registry configuration from the
  reference `homebridge-simple-ir-fan` project.
- Publishing on pull requests or branch pushes.
- Automatically creating Git tags or GitHub/Forgejo releases.
- Committing a release-time version change back to the repository.
- Changing IR capture, normalization, persistence, CLI, or JSON behavior.
- Configuring GitHub branch-protection rules outside the repository.
- Changing Forgejo organization membership, instance-wide visibility, package
  cleanup, or retention settings.

## 4. Definitions

- **CI workflow:** The non-publishing GitHub Actions workflow that validates
  pull requests and pushes to `main`.
- **Release workflow:** The GitHub Actions workflow that validates and publishes
  a supported pushed tag.
- **Stable tag:** `X.Y.Z`, where each component is a non-negative decimal
  integer without unnecessary leading zeroes.
- **Beta tag:** `X.Y.Z-betaT`, where `T` is a positive decimal integer without
  leading zeroes and begins at `1`.
- **Release tag:** A stable tag or beta tag accepted by this specification.
- **Distribution version:** The PEP 440 version stored in the built Python
  package and Forgejo PyPI registry.
- **Public registry owner:** The public Forgejo organization named `public`.

## 5. Fixed Package and Registry Contract

- Package name: `rpi-groove-ir-receiver`.
- Forgejo base URL: `https://forgejo.alexlab.nl`.
- Upload repository URL:
  `https://forgejo.alexlab.nl/api/packages/public/pypi`.
- Public package index URL:
  `https://forgejo.alexlab.nl/api/packages/public/pypi/simple`.
- Publishing identity: Forgejo user `alexbanica`, publishing to the `public`
  organization.
- GitHub Actions upload secret: `FORGEJO_PACKAGE_TOKEN`.
- The secret must contain a Forgejo token authorized to write packages owned by
  the `public` organization.
- Package read access must remain anonymous. Public readability depends on the
  `public` organization remaining public and the Forgejo instance allowing
  anonymous viewing.

## 6. Supported Release Tags and Versions

1. Stable tags must match `X.Y.Z` exactly and publish distribution version
   `X.Y.Z`.
2. Beta tags must match `X.Y.Z-betaT` exactly and publish the PEP 440 canonical
   distribution version `X.Y.ZbT`.
3. The Git tag is the authoritative release-version input. Release builds must
   not depend on the static version currently present in `setup.py` matching the
   tag.
4. Release-time version substitution may affect only the ephemeral runner
   checkout/build environment. It must not modify or push repository history.
5. Unsupported tags must fail before package build or authentication is used.
6. Unsupported forms include:
   - a leading `v`;
   - whitespace;
   - missing version components;
   - leading zeroes such as `01.2.3`;
   - `beta0` or a beta number with leading zeroes;
   - dotted prereleases such as `1.2.3-beta.1`;
   - arbitrary prerelease suffixes;
   - build metadata such as `1.2.3+build.1`.
7. Republishing an existing package name and distribution version must fail. No
   overwrite or delete-and-retry behavior is allowed.

## 7. CI Behavior

1. The CI workflow must run for:
   - pull requests whose base branch is `main`;
   - pushes to `main`.
2. CI must use a supported Python version compatible with the package's declared
   `python_requires >= 3.9` contract.
3. CI must install the deterministic development dependencies required for
   linting and tests without requiring Raspberry Pi hardware or `pigpiod`.
4. The lint gate must run Ruff against the maintained Python source, tests, and
   release-support code with zero lint errors allowed.
5. The test gate must run:
   `python -m unittest discover -s tests -p 'test_*.py'`.
6. A workflow run must fail if dependency installation, linting, or tests fail.
7. Lint and tests must be separately named steps so their outcome is visible in
   GitHub Actions.
8. CI must not receive or reference `FORGEJO_PACKAGE_TOKEN`.

## 8. Release Behavior

1. The release workflow must run only for pushed tags that may match the stable
   or beta numeric forms. Exact acceptance must still be enforced by release
   validation before any publish operation.
2. The workflow must check out the tagged commit, not the current tip of `main`.
3. Only one publish run for the same Git ref may execute at a time, and a newer
   run must not cancel an in-progress upload for that ref.
4. Before authentication or upload, the release path must, in order:
   - validate the tag and derive the distribution version;
   - run the same Ruff lint gate as CI;
   - run the complete unit-test suite;
   - build both a wheel and source distribution from the tagged source;
   - validate both distributions with Twine;
   - verify the distribution name, canonical version, required package content,
     and absence of credentials or unintended runtime/generated files.
5. Any failed pre-publish gate must prevent upload.
6. Upload must use Twine and the fixed Forgejo upload repository URL.
7. `FORGEJO_PACKAGE_TOKEN` must be exposed only to the upload operation as the
   Twine password. It must not be written to the repository, build artifacts,
   logs, command arguments, or persistent authentication files.
8. The Twine username must be `alexbanica`; the registry owner remains `public`.
9. Temporary distributions and authentication material must be removed after
   success or failure without hiding the original failure.
10. After upload, the release path must use the public index without credentials
    to download the exact canonical distribution version into a temporary
    location and verify its name and version metadata.
11. Publication succeeds only when unauthenticated post-publish verification
    succeeds.

## 9. Security and Trust Boundaries

- Pull-request code must never receive the package token.
- Branch CI must never receive the package token.
- Only the tag-triggered upload operation may receive the package token.
- The workflow must not disable TLS certificate verification, configure an
  insecure registry, or add a custom trust bypass.
- Public verification must not include credentials in URLs or process output.
- The workflow must use read-only repository-content permissions unless a more
  permissive scope is explicitly required and approved later.

## 10. Automated Test Requirements

Deterministic tests must cover at least:

- stable-tag acceptance and exact stable distribution-version derivation;
- beta-tag acceptance and PEP 440 `bT` distribution-version derivation;
- rejection of every unsupported tag class listed in section 6;
- missing tag and missing token failures;
- validation ordering, proving lint and tests precede build and upload;
- failure propagation for lint, tests, build, distribution validation, upload,
  and public verification;
- package-name and distribution-version mismatches;
- required and disallowed distribution contents;
- secret scoping to the upload operation;
- cleanup on success and failure;
- CI triggers for pull requests to `main` and pushes to `main`;
- release trigger isolation from pull requests and branch pushes;
- tag checkout, concurrency, least-privilege permissions, and expected secret
  mapping in the release workflow.

Tests must not perform a real package upload or require a real Forgejo token.

## 11. Regression Impact

- CLI flags and defaults remain unchanged.
- JSON output remains `{ "gpio_in": <int>, "pulse_us": <list[int]> }`.
- Pulse normalization and repeat-removal placeholder behavior remain unchanged.
- Runtime dependencies remain appropriate for supported Linux SBC platforms.
- CI and release tests must not require GPIO hardware, `pigpiod`, or network
  access to device services.

## 12. Validation Plan

Validation must include:

- the complete unit-test suite;
- Ruff linting;
- deterministic release-contract and workflow-structure tests;
- local wheel and source-distribution builds;
- Twine validation of both distributions;
- inspection of built package names, versions, and contents;
- GitHub Actions workflow syntax/structure validation;
- `git diff --check`;
- one trusted beta or stable tag exercising the hosted GitHub Actions release
  path;
- authenticated upload to Forgejo followed by unauthenticated exact-version
  download and metadata verification.

If the hosted tag run or live Forgejo round trip is not performed successfully,
delivery must remain DRAFT even when deterministic local validation passes.

## 13. Documentation Requirements

The README must document:

- CI events and required lint/test gates;
- stable and beta tag formats with examples;
- the beta tag to PEP 440 mapping, for example `1.2.3-beta1` to `1.2.3b1`;
- the public Forgejo index and package installation commands;
- the `public` organization ownership model;
- creation and GitHub configuration of `FORGEJO_PACKAGE_TOKEN` without exposing
  its value;
- the trusted-maintainer release procedure;
- duplicate-version behavior and release troubleshooting;
- the live-validation boundary for claiming final delivery.

## 14. Assumptions

- GitHub remains the source repository and GitHub Actions remains the workflow
  executor.
- `main` remains the default integration branch.
- Forgejo remains reachable at `forgejo.alexlab.nl` with valid public TLS.
- The `public` Forgejo organization remains public.
- The `alexbanica` Forgejo user retains package-write access to the `public`
  organization.
- The reference npm implementation supplies the release safety pattern only;
  Python packaging uses Python-native build, Twine, PEP 440, and pip semantics.

## 15. Acceptance Criteria

- Pull requests to `main` and pushes to `main` visibly run lint and tests, and a
  failure in either causes CI failure.
- No PR or branch workflow can access the Forgejo package token.
- Only exact stable and beta release tags are accepted.
- A supported tag builds the expected wheel and source distribution from the
  tagged commit with the specified canonical Python version.
- Upload targets the `public` organization at the fixed Forgejo PyPI endpoint
  using `FORGEJO_PACKAGE_TOKEN`.
- Failed lint, tests, build, package validation, or upload prevents a successful
  release result.
- The published exact version is downloadable without authentication and its
  package metadata matches the expected name and canonical version.
- Automated tests cover the CI and release contracts without live publication.
- Documentation accurately describes setup, release, install, and validation.
- Existing IR receiver behavior and architecture invariants remain unchanged.
