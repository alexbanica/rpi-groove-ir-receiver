import io
import os
import tarfile
import tempfile
import unittest
import zipfile
from pathlib import Path
from typing import Dict, List, Optional
from unittest.mock import patch

from scripts.publish_forgejo import (
    FORGEJO_PUBLIC_INDEX_URL,
    PACKAGE_NAME,
    validate_artifacts,
    publish_release,
)


PACKAGE_VERSION = "1.2.3b1"


def _write_build_artifacts(directory: Path, version: str, bad_metadata: bool = False):
    directory.mkdir(parents=True, exist_ok=True)
    wheel_name = f"rpi_groove_ir_receiver-{version}-py3-none-any.whl"
    wheel_dist_info = f"rpi_groove_ir_receiver-{version}.dist-info"
    with zipfile.ZipFile(directory / wheel_name, "w") as archive:
        archive.writestr("ir_receiver/__init__.py", "")
        archive.writestr(
            f"{wheel_dist_info}/METADATA",
            "Metadata-Version: 2.1\n"
            f"Name: {PACKAGE_NAME}\n"
            f"Version: {version}\n",
        )

    sdist_version = "0.0.0" if bad_metadata else version
    sdist_name = f"{PACKAGE_NAME}-{sdist_version}.tar.gz"
    sdist_root = f"{PACKAGE_NAME}-{sdist_version}"
    metadata = (
        "Metadata-Version: 2.1\n"
        f"Name: {PACKAGE_NAME}\n"
        f"Version: {sdist_version}\n"
    )
    with tarfile.open(directory / sdist_name, "w:gz") as archive:
        for member_path, content in (
            (f"{sdist_root}/ir_receiver/__init__.py", b""),
            (f"{sdist_root}/PKG-INFO", metadata.encode("utf-8")),
        ):
            info = tarfile.TarInfo(member_path)
            info.size = len(content)
            archive.addfile(info, io.BytesIO(content))


def _write_download_wheel(destination: Path, version: str):
    destination.mkdir(parents=True, exist_ok=True)
    wheel_name = f"rpi_groove_ir_receiver-{version}-py3-none-any.whl"
    wheel_dist_info = f"rpi_groove_ir_receiver-{version}.dist-info"
    with zipfile.ZipFile(destination / wheel_name, "w") as archive:
        archive.writestr("ir_receiver/__init__.py", "")
        archive.writestr(
            f"{wheel_dist_info}/METADATA",
            "Metadata-Version: 2.1\n"
            f"Name: {PACKAGE_NAME}\n"
            f"Version: {version}\n",
        )


class FakeRunner:
    def __init__(
        self,
        fail_on: Optional[str] = None,
        bad_build: bool = False,
        events: Optional[List[str]] = None,
    ):
        self.calls: List[tuple] = []
        self.fail_on = fail_on
        self.bad_build = bad_build
        self.events = events

    def __call__(self, command, env=None, cwd=None):
        command = list(command)
        self.calls.append((tuple(command), dict(env or {}), Path(cwd) if cwd else None))
        if self.events is not None:
            self.events.append(" ".join(command))

        joined = " ".join(command)
        if "python -m build" in joined or "-m build" in joined:
            release_dir = Path(command[command.index("--outdir") + 1])
            release_version = (env or {}).get("RELEASE_VERSION", PACKAGE_VERSION)
            _write_build_artifacts(
                release_dir, release_version, bad_metadata=self.bad_build
            )

        if self.fail_on is not None and self.fail_on in joined:
            raise RuntimeError("fake command failure")

        return ""


class FakeDownload:
    def __init__(self, wrong_metadata: bool = False):
        self.calls: List[tuple] = []
        self.wrong_metadata = wrong_metadata
        self.events: Optional[List[str]] = None

    def __call__(self, command, env=None, cwd=None):
        command = list(command)
        self.calls.append((tuple(command), dict(env or {}), Path(cwd) if cwd else None))
        if self.events is not None:
            self.events.append(" ".join(command))
        version = command[-1].split("==", 1)[1]
        if self.wrong_metadata:
            version = "9.9.9"
        destination = Path(command[command.index("--dest") + 1])
        _write_download_wheel(destination, version)
        return ""

    def with_events(self, events: List[str]):
        self.events = events
        return self


class FakeArtifactValidator:
    def __init__(self, events: Optional[List[str]] = None):
        self.events = events

    def __call__(self, *args, **kwargs):
        if self.events is not None:
            self.events.append("validate_artifacts")
        return validate_artifacts(*args, **kwargs)


class PublishForgejoTest(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp())
        self.parent = Path(tempfile.mkdtemp())
        self.username = "publish-user"
        self.token = "secret-that-must-not-leak"

    def tearDown(self):
        # cleanup is permissive if publish cleanup fails.
        for path in (self.root, self.parent):
            for child in path.glob("*"):
                if child.is_dir():
                    import shutil

                    shutil.rmtree(child)

    def invoke(
        self,
        tag="1.2.3",
        *,
        runner: Optional[FakeRunner] = None,
        download: Optional[FakeDownload] = None,
        artifact_validator_fn=validate_artifacts,
        project_root: Optional[Path] = None,
        temp_parent: Optional[Path] = None,
        token: Optional[str] = None,
        events: Optional[List[str]] = None,
        **env_updates,
    ) -> None:
        if runner is None:
            run = FakeRunner(events=events)
        else:
            run = runner
        if download is None:
            download = FakeDownload().with_events(events)
        elif events is not None:
            download.with_events(events)
        publish_kwargs: Dict[str, object] = {
            "run": run,
            "download": download,
            "validate_artifacts_fn": artifact_validator_fn,
        }
        if project_root is not None:
            publish_kwargs["project_root"] = project_root
        if temp_parent is not None:
            publish_kwargs["temp_parent"] = temp_parent

        env = dict(os.environ)
        env.update(env_updates)
        if token is None:
            token = env.get("FORGEJO_PACKAGE_TOKEN", self.token)
        env["FORGEJO_PACKAGE_USERNAME"] = env.get(
            "FORGEJO_PACKAGE_USERNAME", self.username
        )
        env["FORGEJO_PACKAGE_TOKEN"] = token
        with patch.dict(os.environ, env, clear=False):
            publish_release(tag, **publish_kwargs)
        return None

    def test_missing_tag_fails_before_any_command(self):
        runner = FakeRunner()
        with self.assertRaises(ValueError):
            self.invoke(tag="", runner=runner)
        self.assertEqual([], runner.calls)

    def test_missing_token_fails_before_any_command(self):
        runner = FakeRunner()
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(ValueError):
                self.invoke(tag="1.2.3", runner=runner, token="")
        self.assertEqual([], runner.calls)

    def test_missing_username_fails_before_any_command(self):
        runner = FakeRunner()
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(ValueError):
                self.invoke(
                    tag="1.2.3",
                    runner=runner,
                    FORGEJO_PACKAGE_USERNAME="",
                )
        self.assertEqual([], runner.calls)

    def test_pre_publish_gates_run_in_order_with_project_root_cwd(self):
        events: List[str] = []
        runner = FakeRunner(events=events)
        download = FakeDownload().with_events(events)
        validator = FakeArtifactValidator(events)
        self.invoke(
            runner=runner,
            download=download,
            artifact_validator_fn=validator,
            project_root=self.root,
            temp_parent=self.parent,
        )
        command_log: List[tuple] = []
        for event in events:
            if event == "validate_artifacts":
                command_log.append(("validate_artifacts", event))
            elif "python" in event and "-m pip download" in event:
                command_log.append(("download", event))
            elif "python" in event:
                command_log.append(("run", event))
            else:
                command_log.append(("download", event))
        order = [
            [
                i
                for i, (kind, command) in enumerate(command_log)
                if kind == "run" and "ruff" in command
            ][0],
            [
                i
                for i, (kind, command) in enumerate(command_log)
                if kind == "run" and "unittest" in command
            ][0],
            [
                i
                for i, (kind, command) in enumerate(command_log)
                if kind == "run" and "-m build" in command
            ][0],
            [
                i
                for i, (kind, command) in enumerate(command_log)
                if kind == "run" and "twine check" in command
            ][0],
            [
                i
                for i, (kind, command) in enumerate(command_log)
                if kind == "validate_artifacts"
            ][0],
            [
                i
                for i, (kind, command) in enumerate(command_log)
                if kind == "run" and "twine upload" in command
            ][0],
            [
                i
                for i, (kind, command) in enumerate(command_log)
                if kind == "download" and "pip download" in command
            ][0],
        ]
        self.assertEqual(order, sorted(order))
        for _, _, command_cwd in runner.calls:
            self.assertEqual(self.root, command_cwd)
        self.assertEqual(self.root, download.calls[0][2])

    def test_each_pre_publish_failure_prevents_upload_and_download(self):
        for fail in ("ruff", "unittest", "-m build", "twine check"):
            with self.subTest(fail=fail):
                runner = FakeRunner(fail_on=fail)
                download = FakeDownload()
                with self.assertRaises(RuntimeError):
                    self.invoke(
                        runner=runner,
                        download=download,
                        project_root=self.root,
                        temp_parent=self.parent,
                    )
                upload = [
                    command
                    for command, _, _ in runner.calls
                    if "twine upload" in " ".join(command)
                ]
                self.assertEqual([], upload)
                self.assertEqual([], download.calls)

    def test_real_validation_failure_propagates(self):
        runner = FakeRunner(bad_build=True)
        with self.assertRaises(ValueError):
            self.invoke(
                runner=runner,
                project_root=self.root,
                temp_parent=self.parent,
            )

    def test_upload_failure_skips_public_verification(self):
        runner = FakeRunner(fail_on="twine upload")
        download = FakeDownload()
        with self.assertRaises(RuntimeError):
            self.invoke(
                runner=runner,
                download=download,
                project_root=self.root,
                temp_parent=self.parent,
            )
        upload = [
            command
            for command, _, _ in runner.calls
            if "twine upload" in " ".join(command)
        ]
        self.assertEqual(1, len(upload))
        self.assertEqual([], download.calls)

    def test_public_verification_failure_propagates(self):
        runner = FakeRunner()
        download = FakeDownload(wrong_metadata=True)
        with self.assertRaises(ValueError):
            self.invoke(
                runner=runner,
                download=download,
                project_root=self.root,
                temp_parent=self.parent,
            )

    def test_one_shot_upload_duplicate_fails_once(self):
        runner = FakeRunner(fail_on="twine upload")
        with self.assertRaises(RuntimeError):
            self.invoke(
                runner=runner,
                project_root=self.root,
                temp_parent=self.parent,
            )
        self.assertEqual(
            1,
            len(
                [
                    command
                    for command, _, _ in runner.calls
                    if "twine upload" in " ".join(command)
                ]
            ),
        )

    def test_credentials_are_not_in_command_args_or_non_upload_env(self):
        runner = FakeRunner()
        download = FakeDownload()
        self.invoke(
            runner=runner,
            download=download,
            project_root=self.root,
            temp_parent=self.parent,
        )
        upload_calls = [
            (command, env)
            for command, env, _ in runner.calls
            if "twine upload" in " ".join(command)
        ]
        self.assertEqual(1, len(upload_calls))
        upload_env = upload_calls[0][1]
        self.assertEqual(self.username, upload_env.get("TWINE_USERNAME"))
        self.assertEqual(self.token, upload_env.get("TWINE_PASSWORD"))
        self.assertNotIn("FORGEJO_PACKAGE_USERNAME", upload_env)
        self.assertNotIn("FORGEJO_PACKAGE_TOKEN", upload_env)

        for command, env, _ in runner.calls:
            self.assertNotIn("FORGEJO_PACKAGE_USERNAME", env)
            self.assertNotIn("FORGEJO_PACKAGE_TOKEN", env)
            if "twine upload" not in " ".join(command):
                self.assertNotIn("TWINE_USERNAME", env)
                self.assertNotIn("TWINE_PASSWORD", env)
                for field in ("secret", self.username, self.token):
                    self.assertNotIn(field, " ".join(command))

    def test_public_verification_uses_downloaded_wheel_only(self):
        runner = FakeRunner()
        download = FakeDownload()
        self.invoke(
            runner=runner,
            download=download,
            project_root=self.root,
            temp_parent=self.parent,
        )
        self.assertEqual(1, len(download.calls))
        self.assertIn(FORGEJO_PUBLIC_INDEX_URL, download.calls[0][0])
        self.assertIn("--index-url", download.calls[0][0])

    def test_temp_parent_is_preserved_and_child_cleanup(self):
        marker = self.parent / "marker.txt"
        marker.write_text("keep", encoding="utf-8")
        runner = FakeRunner()
        self.invoke(
            runner=runner,
            project_root=self.root,
            temp_parent=self.parent,
        )
        self.assertTrue(marker.exists())
        release_dirs = [
            path
            for path in self.parent.iterdir()
            if path.is_dir() and path.name.startswith("forgejo-release-")
        ]
        self.assertEqual([], release_dirs)

    def test_release_cleanup_preserved_on_failure(self):
        marker = self.parent / "marker.txt"
        marker.write_text("keep", encoding="utf-8")
        runner = FakeRunner(fail_on="twine upload")
        with self.assertRaises(RuntimeError):
            self.invoke(
                runner=runner,
                project_root=self.root,
                temp_parent=self.parent,
            )
        self.assertTrue(marker.exists())
        release_dirs = [
            path
            for path in self.parent.iterdir()
            if path.is_dir() and path.name.startswith("forgejo-release-")
        ]
        self.assertEqual([], release_dirs)


if __name__ == "__main__":
    unittest.main()
