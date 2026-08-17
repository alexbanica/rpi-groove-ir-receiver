"""Release orchestration for Forgejo package publishing."""

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Callable, Dict, Optional, Sequence, Tuple

from .package_artifacts import validate_artifacts
from .release_version import parse_release_tag


PACKAGE_NAME = "rpi-groove-ir-receiver"
FORGEJO_USERNAME_ENV = "FORGEJO_PACKAGE_USERNAME"
FORGEJO_UPLOAD_URL = "https://forgejo.alexlab.nl/api/packages/public/pypi"
FORGEJO_PUBLIC_INDEX_URL = (
    "https://forgejo.alexlab.nl/api/packages/public/pypi/simple"
)

REQUIRED_DISTRIBUTION_PATHS = ("ir_receiver/__init__.py",)
DISALLOWED_DISTRIBUTION_PATHS = (
    ".env",
    "**/.env",
    ".pypirc",
    "**/.pypirc",
    "*.key",
    "*.pem",
    "**/*.key",
    "**/*.pem",
    ".github",
    ".github/*",
    ".github/*/*",
    ".github/**/*",
    "**/.github/*",
    "**/.github/*/*",
    "**/.github/**/*",
    ".git",
    ".git/*",
    ".git/*/*",
    ".git/**/*",
    "**/.git/*",
    "**/.git/*/*",
    "**/.git/**/*",
    "__pycache__",
    "__pycache__/*",
    "__pycache__/*/*",
    "__pycache__/**/*",
    "**/__pycache__/*",
    "**/__pycache__/*/*",
    "**/__pycache__/**/*",
    "*.pyc",
    "**/*.pyc",
)


def _run_clean_env(base: Optional[Dict[str, str]] = None) -> Dict[str, str]:
    env = dict(os.environ if base is None else base)
    env.pop(FORGEJO_USERNAME_ENV, None)
    env.pop("TWINE_PASSWORD", None)
    env.pop("FORGEJO_PACKAGE_TOKEN", None)
    return env


def _run_subprocess(
    command: Sequence[str],
    env: Optional[Dict[str, str]] = None,
    cwd: Optional[Path] = None,
) -> str:
    subprocess.run(
        list(command),
        check=True,
        text=True,
        env=env,
        cwd=str(cwd) if cwd is not None else None,
    )
    return ""


def _default_download(
    command: Sequence[str],
    env: Optional[Dict[str, str]] = None,
    cwd: Optional[Path] = None,
) -> str:
    return _run_subprocess(command, env=env, cwd=cwd)


def _release_root(temp_parent: Optional[Path] = None) -> Path:
    if temp_parent is None:
        return Path(tempfile.mkdtemp(prefix="forgejo-release-"))
    return Path(tempfile.mkdtemp(prefix="forgejo-release-", dir=str(temp_parent)))


def _clean_release_dir(path: Path) -> None:
    if path.exists():
        shutil.rmtree(path)


def _discover_artifacts_for_twine(artifact_dir: Path) -> Tuple[Path, Path]:
    artifact_dir = Path(artifact_dir)
    candidates = [path for path in artifact_dir.iterdir() if path.is_file()]
    wheels = [path for path in candidates if path.suffix == ".whl"]
    sdists = [path for path in candidates if path.name.endswith((".tar.gz", ".zip"))]

    if len(wheels) != 1:
        raise ValueError(f"expected exactly one wheel artifact, found {len(wheels)}")
    if len(sdists) != 1:
        raise ValueError(
            f"expected exactly one source distribution artifact, found {len(sdists)}"
        )

    return wheels[0], sdists[0]


def publish_release(
    tag: str,
    *,
    run: Callable[..., str] = _run_subprocess,
    download: Callable[..., str] = _default_download,
    validate_artifacts_fn=validate_artifacts,
    project_root: Optional[Path] = None,
    temp_parent: Optional[Path] = None,
) -> None:
    tag_data = parse_release_tag(tag)
    username = os.environ.get(FORGEJO_USERNAME_ENV)
    token = os.environ.get("FORGEJO_PACKAGE_TOKEN")
    if not username:
        raise ValueError(f"{FORGEJO_USERNAME_ENV} is required")
    if not token:
        raise ValueError("FORGEJO_PACKAGE_TOKEN is required")

    root = Path.cwd() if project_root is None else Path(project_root)
    release_dir = _release_root(temp_parent)
    original_error: Optional[BaseException] = None

    try:
        command = [
            sys.executable,
            "-m",
            "ruff",
            "check",
            "ir_receiver",
            "scripts",
            "tests",
            "setup.py",
        ]
        run(command, env=_run_clean_env(), cwd=root)

        command = [
            sys.executable,
            "-m",
            "unittest",
            "discover",
            "-s",
            "tests",
            "-p",
            "test_*.py",
        ]
        run(command, env=_run_clean_env(), cwd=root)

        build_env = _run_clean_env()
        build_env["RELEASE_VERSION"] = tag_data.distribution_version
        build_command = [
            sys.executable,
            "-m",
            "build",
            "--outdir",
            str(release_dir),
            "--sdist",
            "--wheel",
        ]
        run(build_command, env=build_env, cwd=root)

        wheel_path, sdist_path = _discover_artifacts_for_twine(release_dir)
        twine_check_command = [
            sys.executable,
            "-m",
            "twine",
            "check",
            str(wheel_path),
            str(sdist_path),
        ]
        run(twine_check_command, env=_run_clean_env(), cwd=root)

        validate_artifacts_fn(
            release_dir,
            expected_name=PACKAGE_NAME,
            expected_version=tag_data.distribution_version,
            required_paths=REQUIRED_DISTRIBUTION_PATHS,
            disallowed_paths=DISALLOWED_DISTRIBUTION_PATHS,
        )

        upload_env = _run_clean_env()
        upload_env["TWINE_USERNAME"] = username
        upload_env["TWINE_PASSWORD"] = token
        upload_command = [
            sys.executable,
            "-m",
            "twine",
            "upload",
            "--non-interactive",
            "--repository-url",
            FORGEJO_UPLOAD_URL,
            str(wheel_path),
            str(sdist_path),
        ]
        run(upload_command, env=upload_env, cwd=root)

        download_dir = release_dir / "verify"
        download_dir.mkdir(parents=True)

        download_command = [
            sys.executable,
            "-m",
            "pip",
            "download",
            "--no-deps",
            "--dest",
            str(download_dir),
            "--index-url",
            FORGEJO_PUBLIC_INDEX_URL,
            "{}=={}".format(PACKAGE_NAME, tag_data.distribution_version),
        ]
        download(download_command, env=_run_clean_env(), cwd=root)

        validation = validate_artifacts(
            download_dir,
            expected_name=PACKAGE_NAME,
            expected_version=tag_data.distribution_version,
            required_paths=REQUIRED_DISTRIBUTION_PATHS,
            disallowed_paths=DISALLOWED_DISTRIBUTION_PATHS,
            require_wheel=True,
            require_sdist=False,
        )
        if not validation:
            raise ValueError("public verification returned no artifacts")
    except BaseException as exc:
        original_error = exc
        raise
    finally:
        if release_dir.exists():
            try:
                _clean_release_dir(release_dir)
            except BaseException:
                if original_error is None:
                    raise


def main() -> int:
    parser = argparse.ArgumentParser(description="Publish a Forgejo package release.")
    parser.parse_args()

    tag = os.environ.get("RELEASE_TAG")
    if not tag:
        raise ValueError("RELEASE_TAG is required")
    publish_release(tag)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
