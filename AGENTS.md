# AGENTS

## Domain-only test policy

- Automated tests of any kind, including unit, integration, contract, snapshot,
  workflow, and configuration tests, may be created or maintained only for
  deterministic domain source logic in this project.
- Do not create or maintain tests for anything outside domain source logic,
  including application orchestration, infrastructure and adapters,
  presentation, UI and controllers, Docker or container files, GitHub Actions
  or other CI/CD workflows, deployment and configuration, packaging and release
  scripts, tooling, or other operational code.
- Validate non-domain changes with appropriate static, syntax, lint, type,
  structural, build, dry-run, smoke, runtime, or operator checks instead of
  automated tests.
- If this project has no domain source logic, automated testing and test-first
  work are not applicable.
- This policy supersedes any more general testing or validation wording
  elsewhere in this file.

## Project implementation status

The codebase is aligned to a DDD + Onion style layout.

### Layers

- `domains`: entities, DTOs, and interfaces.
- `applications`: business services and orchestration.
- `infrastructures`: pigpio and filesystem adapters.
- `controllers`: CLI request/response and coordination.
- `shared/constants`: centralized static strings and numeric thresholds.

Dependencies point inward. `controllers` and `infrastructures` may depend on application/domain contracts, while `domains` must stay independent of CLI parsing, filesystem persistence, pigpio, GPIO, and process-runtime concerns.

### Project-specific architecture

- `ir_receiver/domains/entities`: raw pulse, normalized pulse, and burst model objects.
- `ir_receiver/domains/dtos`: datastore-free transfer objects for captured output.
- `ir_receiver/domains/interfaces`: domain-facing contracts; every interface must use the `Interface` suffix.
- `ir_receiver/applications/services`: capture, burst selection, normalization, and persistence orchestration.
- `ir_receiver/infrastructures/gpio`: pigpio/GPIO boundary implementations.
- `ir_receiver/infrastructures/recorders`: concrete pulse capture adapters.
- `ir_receiver/infrastructures/persistences`: JSON pulse file writing adapters.
- `ir_receiver/controllers/requests` and `ir_receiver/controllers/responses`: CLI DTOs.
- `ir_receiver/shared/constants`: default GPIO, gap, timeout, burst, and threshold values.

### Naming standards

- Interfaces are suffixed with `Interface`.
- Abstract classes are prefixed with `Abstract`.
- Implementations of abstract classes remove the `Abstract` prefix and keep the remaining name.
- Service implementations match interface names without suffix.

### Invariants

The following behavior must remain stable unless a new approved spec changes it:

1. CLI flags and defaults:
   - `--in-gpio=16`
   - `--out-file` required
   - `--timeout=10.0`
   - `--gap=0.15`
   - `--bursts=1`
2. JSON output shape:
   - `{ "gpio_in": <int>, "pulse_us": <list[int]> }`
3. Pulse normalization behavior and repeat-removal placeholder semantics.

### Testing

- Unit tests live in `tests/`.
- Run with:

```bash
python -m unittest discover -s tests -p 'test_*.py'
```

### API docs scope

No HTTP API exists. OpenAPI and `.http` artifacts are not applicable for the current project scope.

## Packaging and release invariants

- The package is named `rpi-groove-ir-receiver`, supports Python 3.9 and newer,
  and is published to the public Forgejo organization through
  `https://forgejo.alexlab.nl/api/packages/public/pypi`.
- Release versions come exclusively from exact pushed tags. Stable tags use
  `X.Y.Z`; beta tags use `X.Y.Z-betaT` with `T >= 1` and map to the PEP 440
  version `X.Y.ZbT`. A leading `v`, whitespace, leading zeroes, missing version
  components, `beta0`, dotted beta numbers, arbitrary prerelease suffixes, and
  build metadata are invalid.
- A release-time version override is ephemeral. Release automation must not
  edit or push repository version files, create tags, or overwrite an existing
  package version.
- Before upload, the publisher must validate the tag, lint, run the maintained
  domain test suite, build a wheel and source distribution, run Twine checks,
  and inspect artifact identity, version, required content, and disallowed
  credential or generated content. Any failed gate prevents upload.
- `FORGEJO_PACKAGE_USERNAME` and `FORGEJO_PACKAGE_TOKEN` are tag-publish secrets.
  They must not be available to pull-request or branch CI. Child processes are
  credential-clean except for the Twine upload process, which receives the
  values as `TWINE_USERNAME` and `TWINE_PASSWORD`.
- Temporary release material must be removed after success or failure without
  hiding the original failure. After upload, the exact version must install
  anonymously from Forgejo, with public PyPI used only to resolve third-party
  dependencies, and the downloaded Forgejo wheel must pass metadata and content
  validation.
- Non-domain release and workflow behavior is validated with static, syntax,
  build, hosted, live-registry, and operator checks rather than automated tests,
  in accordance with the domain-only test policy.
