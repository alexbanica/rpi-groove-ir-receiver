import io
import tarfile
import tempfile
import unittest
import zipfile
from pathlib import Path

from scripts.package_artifacts import validate_artifacts
from scripts.publish_forgejo import DISALLOWED_DISTRIBUTION_PATHS


PACKAGE_NAME = "rpi-groove-ir-receiver"
PACKAGE_VERSION = "1.2.3b1"
REQUIRED_PATHS = ("ir_receiver/__init__.py",)


class PackageArtifactsTest(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.artifact_dir = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def _write_wheel(
        self,
        name=PACKAGE_NAME,
        version=PACKAGE_VERSION,
        extra_files=(),
        build_tag="",
    ):
        filename = (
            f"{name.replace('-', '_')}-{version}-"
            f"{build_tag + '-' if build_tag else ''}py3-none-any.whl"
        )
        dist_info = f"{name.replace('-', '_')}-{version}.dist-info"
        files = {
            "ir_receiver/__init__.py": "",
            f"{dist_info}/METADATA": (
                "Metadata-Version: 2.1\n"
                f"Name: {name}\n"
                f"Version: {version}\n"
            ),
        }
        files.update(dict.fromkeys(extra_files, "synthetic fixture"))

        with zipfile.ZipFile(self.artifact_dir / filename, "w") as archive:
            for path, content in files.items():
                archive.writestr(path, content)

        return self.artifact_dir / filename

    def _write_sdist(
        self,
        name=PACKAGE_NAME,
        version=PACKAGE_VERSION,
        extra_files=(),
        suffix="",
    ):
        root = f"{name}-{version}"
        filename = f"{root}{suffix}.tar.gz"
        files = {
            f"{root}/ir_receiver/__init__.py": "",
            f"{root}/PKG-INFO": (
                "Metadata-Version: 2.1\n"
                f"Name: {name}\n"
                f"Version: {version}\n"
            ),
        }
        files.update({f"{root}/{path}": "synthetic fixture" for path in extra_files})

        with tarfile.open(self.artifact_dir / filename, "w:gz") as archive:
            for path, content in files.items():
                data = content.encode("utf-8")
                info = tarfile.TarInfo(path)
                info.size = len(data)
                archive.addfile(info, io.BytesIO(data))

        return self.artifact_dir / filename

    def _validate(
        self,
        required_paths=REQUIRED_PATHS,
        disallowed_paths=(),
        require_wheel=True,
        require_sdist=True,
    ):
        return validate_artifacts(
            self.artifact_dir,
            expected_name=PACKAGE_NAME,
            expected_version=PACKAGE_VERSION,
            required_paths=required_paths,
            disallowed_paths=disallowed_paths,
            require_wheel=require_wheel,
            require_sdist=require_sdist,
        )

    def test_discovers_one_wheel_and_one_sdist_with_exact_metadata(self):
        self._write_wheel()
        self._write_sdist()
        artifacts = self._validate()
        self.assertEqual(2, len(artifacts))
        self.assertEqual({"wheel", "sdist"}, {artifact.kind for artifact in artifacts})

    def test_rejects_disallowed_name_version_mismatches(self):
        self._write_wheel(name="wrong-name")
        self._write_sdist(version="9.9.9")
        with self.assertRaises(ValueError):
            self._validate()

    def test_rejects_missing_wheel_or_sdist(self):
        self._write_wheel()
        with self.assertRaises(ValueError):
            self._validate()

        self.artifact_dir.joinpath(next(self.artifact_dir.iterdir()).name).unlink()
        self._write_sdist()
        with self.assertRaises(ValueError):
            self._validate()

    def test_rejects_duplicate_wheels_or_sdists(self):
        self._write_wheel()
        self._write_sdist()
        self._write_wheel(build_tag="1")
        with self.assertRaises(ValueError):
            self._validate()

        self.artifact_dir.joinpath(
            f"{PACKAGE_NAME.replace('-', '_')}-{PACKAGE_VERSION}-1-py3-none-any.whl"
        ).unlink()
        self._write_sdist(suffix="-2")
        with self.assertRaises(ValueError):
            self._validate()

    def test_requires_declared_package_content_in_both_artifacts(self):
        self._write_wheel()
        self._write_sdist()
        with self.assertRaises(ValueError):
            self._validate(required_paths=("ir_receiver/missing.py",))

    def test_rejects_credentials_and_generated_runtime_content(self):
        disallowed = (
            ".env",
            "nested/.env",
            ".pypirc",
            "nested/.pypirc",
            "private.pem",
            "private.key",
            "secrets/key.pem",
            "secrets/keypair.key",
            ".github/workflows/ci.yml",
            ".git/objects/obj",
            "__pycache__/module.pyc",
            "nested/__pycache__/module.pyc",
            "module.pyc",
        )
        for forbidden in disallowed:
            with self.subTest(forbidden=forbidden):
                self._write_wheel(extra_files=(forbidden,))
                self._write_sdist(extra_files=(forbidden,))
                with self.assertRaises(ValueError):
                    self._validate(disallowed_paths=DISALLOWED_DISTRIBUTION_PATHS)

    def test_allows_single_wheel_downloaded_artifact_validation(self):
        self._write_wheel()
        result = self._validate(require_wheel=True, require_sdist=False)
        self.assertEqual(1, len(result))
        self.assertEqual("wheel", result[0].kind)

    def test_normalized_package_name_validation(self):
        self._write_wheel(name="rpi_groove_ir_receiver")
        self._write_sdist(name="rpi_groove_ir_receiver")
        artifacts = self._validate()
        self.assertEqual(2, len(artifacts))


if __name__ == "__main__":
    unittest.main()
