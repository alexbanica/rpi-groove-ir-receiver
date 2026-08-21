# Raspberry Pi Grove IR Receiver

Python library and CLI for recording and processing raw IR pulse/space timings from Grove-style IR receivers connected to Linux SBCs through `pigpio`.

## Features

- Capture raw pulse durations in microseconds from a GPIO input.
- Normalize captured pulses with deterministic threshold logic.
- Save pulses to JSON for replay or analysis.
- Capture one or multiple bursts and select the burst to persist.
- Layered architecture aligned to DDD and Onion principles.

## Requirements

- Python 3.9+
- Linux SBC (Raspberry Pi, Hobot, or Jetson)
- `pigpiod` daemon running

Install dependencies:

```bash
pip install -r requirements.txt
```

Install and enable `pigpiod`:

```bash
sudo apt-get update
sudo apt-get install -y python3-pigpio pigpio
sudo systemctl enable pigpiod
sudo systemctl start pigpiod
```

## Platform-specific dependency policy

`requirements.txt` includes marker-based platform-specific packages:

- Raspberry Pi: `RPi.GPIO`, `spidev`
- Hobot: `Hobot.GPIO`
- Jetson: `Jetson.GPIO`
- Common: `pigpio`

## Project structure

```text
ir_receiver/
  applications/services/
  controllers/
    requests/
    responses/
  domains/
    dtos/
    entities/
    interfaces/
  infrastructures/
    gpio/
    persistences/
    recorders/
  shared/constants/
```

## CLI usage

Capture one burst and save to JSON:

```bash
python -m ir_receiver --out-file remote_pulse.json --in-gpio 16 --timeout 10 --gap 0.15 --bursts 1
```

Arguments and defaults:

- `--in-gpio` (default: `16`)
- `--out-file` (required)
- `--timeout` (default: `10.0`)
- `--gap` (default: `0.15`)
- `--bursts` (default: `1`)

Output JSON schema remains:

```json
{
  "gpio_in": 16,
  "pulse_us": [9000, 4500, 560]
}
```

## Development

The package declares Python 3.9+ runtime compatibility. Repository CI currently
runs on Python 3.10 and 3.11.

Automated tests are intentionally limited to deterministic pulse normalization
and burst-selection domain behavior. Run the maintained suite with:

```bash
python -m unittest discover -s tests -p 'test_*.py'
```

## Troubleshooting

- Cannot import `pigpio`:
  - `pip install pigpio`
- Cannot connect to daemon:
  - `sudo systemctl start pigpiod`
- No capture detected:
  - Validate wiring and BCM pin.
  - Increase `--timeout` or adjust `--gap`.

## Maintainer release and publishing workflow

This repository includes two GitHub workflows:

- `.github/workflows/ci.yml`
  - Runs on `pull_request` targeting `main`.
  - Runs on `push` to `main`.
  - Installs Python 3.10 and 3.11.
  - Runs `ruff check ir_receiver scripts tests setup.py`.
  - Runs `python -m unittest discover -s tests -p 'test_*.py'`.
  - Uses immutable SHA pins for `actions/checkout@v7.0.1` and
    `actions/setup-python@v7.0.0`, with a pip cache keyed by the requirement files.
  - Checkout credentials are not persisted.
  - Does not receive or expose the publish token.
- `.github/workflows/publish.yml`
  - Runs only for pushed tags matching:
    - `X.Y.Z`
    - `X.Y.Z-betaT` where `T >= 1`
  - Uses coarse tag globs `"[0-9]*.[0-9]*.[0-9]*"` and
    `"[0-9]*.[0-9]*.[0-9]*-beta[1-9][0-9]*"` to start the publish path, then
    applies exact release validation in `scripts.release_version`.
  - Uses a per-workflow/per-ref non-canceling concurrency group.
  - Checks out `${{ github.ref }}` through an immutable `actions/checkout@v7.0.1`
    pin, passes it in `with.ref`, and does not persist checkout credentials.
  - Uses an immutable `actions/setup-python@v7.0.0` pin, installs
    `requirements-dev.txt`, then runs `python -m scripts.publish_forgejo`.
  - Provides `RELEASE_TAG` from `${{ github.ref_name }}` plus the
    `FORGEJO_PACKAGE_USERNAME` and `FORGEJO_PACKAGE_TOKEN` secrets only in the
    publish step environment.

The workflows use read-only repository permissions, do not persist checkout
credentials, and use per-workflow/per-ref concurrency. Superseded CI runs are
canceled; an in-progress publish for a tag is never canceled. Dependabot groups
GitHub Actions updates on a weekly schedule.

### Supported release tags and PEP 440 mapping

- Stable release tag: `X.Y.Z` -> package version `X.Y.Z`
- Beta release tag: `X.Y.Z-betaT` -> package version `X.Y.ZbT`
  Example: `1.2.3-beta1` -> `1.2.3b1`

### Routed client index and install command
Versions are derived from the tag in the ephemeral build environment; the
static version in `setup.py` does not need to match the release tag and is not
rewritten or pushed. Tags with a leading `v`, missing components, leading
zeroes, `beta0`, dotted beta numbers, other prerelease suffixes, whitespace, or
build metadata are rejected before build or authentication.

### Public Forgejo index and install command

- Client index root: `https://pypi.alexlab.nl/simple/`
- Package name: `rpi-groove-ir-receiver`
- Organization owner: `public`
- Install with no credentials:

```bash
sed -i \
  's/^include-system-site-packages = false$/include-system-site-packages = true/' \
  ~/.venv/pyvenv.cfg
```

```bash
python -m pip install \
  --index-url https://pypi.alexlab.nl/simple/ \
  rpi-groove-ir-receiver==1.2.3b1
```

The routed client index serves `rpi-groove-ir-receiver` from Forgejo and
automatically resolves third-party dependencies through its cached PyPI route.
Publish uploads remain directed to Forgejo.

### Trusted maintainer publish procedure

1. Ensure you are a trusted maintainer with control over repository Actions secrets.
2. Create the repository secrets `FORGEJO_PACKAGE_USERNAME` and
   `FORGEJO_PACKAGE_TOKEN` as GitHub Actions secrets. The username is passed
   only to Twine's upload subprocess; neither value is logged or persisted.
3. Push a supported tag from trusted maintainer account:
   - Stable: `git tag 1.2.3`
   - Beta: `git tag 1.2.3-beta1`
4. Push the tag: `git push origin <tag>`.
5. Confirm the tag-triggered `publish.yml` run completes. The workflow
   itself uses coarse tag filters and then relies on exact validation in the
   publish script.
6. The workflow validates release behavior, builds artifacts, runs Twine validation,
   uploads to `https://forgejo.alexlab.nl/api/packages/public/pypi`, and
   anonymously installs and downloads the exact package version through
   `https://pypi.alexlab.nl/simple/`, then verifies its wheel metadata without
   credentials.

`FORGEJO_PACKAGE_USERNAME` and `FORGEJO_PACKAGE_TOKEN` must remain secrets and
must not be printed in logs or written into files.

The publisher removes both Forgejo variables from child-process environments.
Only the Twine upload process receives their values, mapped to
`TWINE_USERNAME` and `TWINE_PASSWORD`. Pull-request and branch CI never receive
the publish credentials. Temporary release artifacts are removed after success
or failure without replacing the original command failure.

Dependabot groups weekly GitHub Actions updates so immutable pins can be
refreshed consistently with the other Python repositories.

### Duplicate version behavior and troubleshooting

- The public package index enforces unique package+version combinations.
- Republishing an existing distribution version is expected to fail.
- If publish fails at upload for duplicate/version-conflict reasons, create a new
  tag with a new supported release version before retrying.
- If publish fails earlier, use the workflow logs to identify the failed gate:
  - lint
  - tests
  - build
  - Twine validation
  - upload
  - public verification

### Release live-validation boundary

The CI and release workflows, exact tag parser, build and artifact checks,
credential isolation, Forgejo upload, anonymous dependency-resolving install,
and exact wheel verification are implemented. Non-domain workflow, packaging,
and release-tool tests were intentionally removed under the repository's
domain-only automated-test policy; those areas require static, build, hosted,
live-registry, and operator validation.

Hosted GitHub Actions execution and a live authenticated Forgejo upload followed
by anonymous install/download are not claimed as verified by the documentation
cleanup. Treat release readiness as unverified until a trusted supported tag run
completes those checks successfully.

## License

See [LICENSE](LICENSE).
