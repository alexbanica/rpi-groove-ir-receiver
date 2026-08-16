"""Helpers for validating built Python distribution artifacts."""

import fnmatch
import tarfile
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Tuple


@dataclass(frozen=True)
class Artifact:
    """Represents a validated distribution artifact."""

    kind: str
    path: Path
    name: str
    version: str


def validate_artifacts(
    artifact_dir: Path,
    expected_name: str,
    expected_version: str,
    required_paths: Iterable[str] = (),
    disallowed_paths: Iterable[str] = (),
    require_wheel: bool = True,
    require_sdist: bool = True,
) -> Tuple[Artifact, ...]:
    """Validate build artifacts in ``artifact_dir``.

    Requirements:
        * exactly one wheel and one source distribution by default
        * each artifact must contain matching package name and version metadata
        * both artifacts must contain every path in ``required_paths``
        * neither artifact contains a path matching ``disallowed_paths``
    """

    artifact_dir = Path(artifact_dir)
    candidates = list(artifact_dir.iterdir())

    wheels = [path for path in candidates if path.suffix == ".whl"]
    sdists = [path for path in candidates if path.name.endswith((".tar.gz", ".zip"))]

    if require_wheel and len(wheels) != 1:
        raise ValueError(f"expected exactly one wheel artifact, found {len(wheels)}")
    if not require_wheel and len(wheels) > 1:
        raise ValueError(f"expected zero or one wheel artifact, found {len(wheels)}")

    if require_sdist and len(sdists) != 1:
        raise ValueError(
            f"expected exactly one source distribution artifact, found {len(sdists)}"
        )
    if not require_sdist and len(sdists) > 1:
        raise ValueError(
            f"expected zero or one source distribution artifact, found {len(sdists)}"
        )

    required_paths = tuple(required_paths)
    disallowed_paths = tuple(disallowed_paths)

    artifacts = []
    if wheels:
        artifacts.append(
            _validate_wheel(
                wheels[0],
                expected_name,
                expected_version,
                required_paths,
                disallowed_paths,
            )
        )
    if sdists:
        artifacts.append(
            _validate_sdist(
                sdists[0],
                expected_name,
                expected_version,
                required_paths,
                disallowed_paths,
            )
        )

    return tuple(artifacts)


def _normalize_name(value):
    return value.strip().replace("_", "-").lower()


def _parse_metadata(content):
    name = None
    version = None

    for line in content.splitlines():
        if ":" not in line:
            continue

        key, value = line.split(":", 1)
        key = key.strip().lower()
        value = value.strip()

        if key == "name":
            name = value
        elif key == "version":
            version = value

        if name is not None and version is not None:
            break

    if name is None or version is None:
        raise ValueError("missing metadata name/version")

    return name, version


def _require_paths(
    member_paths,
    artifact,
    required_paths,
):
    for required in required_paths:
        if required not in member_paths:
            raise ValueError(
                "artifact missing required path: " f"{artifact.kind}/{required}"
            )


def _forbid_paths(member_paths, artifact, disallowed_paths):
    for forbidden in disallowed_paths:
        for member in member_paths:
            if (
                fnmatch.fnmatch(member, forbidden)
                or _match_glob_path(member, forbidden)
            ):
                raise ValueError(
                    "artifact contains disallowed path: "
                    f"{artifact.kind}/{forbidden}"
                )


def _match_glob_path(path, pattern):
    normalized = path.replace("\\", "/")
    return Path(normalized).match(pattern)


def _validate_wheel(
    path,
    expected_name,
    expected_version,
    required_paths,
    disallowed_paths,
):
    with zipfile.ZipFile(path) as archive:
        names = set(archive.namelist())
        _forbid_paths(names, Artifact("wheel", path, "", ""), disallowed_paths)

        metadata_name = None
        for name in names:
            if name.endswith(".dist-info/METADATA"):
                metadata_name = name
                break

        if metadata_name is None:
            raise ValueError("wheel artifact missing METADATA")

        metadata_bytes = archive.read(metadata_name)

    metadata = _parse_metadata(metadata_bytes.decode("utf-8"))
    metadata_name_value = metadata[0]
    metadata_version = metadata[1]

    if _normalize_name(metadata_name_value) != _normalize_name(expected_name):
        raise ValueError(
            f"wheel metadata name mismatch: {metadata_name_value} != "
            f"{expected_name}"
        )
    if metadata_version != expected_version:
        raise ValueError(
            f"wheel metadata version mismatch: {metadata_version} != "
            f"{expected_version}"
        )

    artifact = Artifact("wheel", path, metadata_name_value, metadata_version)
    _require_paths(names, artifact, required_paths)
    _forbid_paths(names, artifact, disallowed_paths)

    return artifact


def _validate_sdist(
    path,
    expected_name,
    expected_version,
    required_paths,
    disallowed_paths,
):
    with tarfile.open(path) as archive:
        names = archive.getnames()
        flattened = {
            _strip_sdist_root(name) for name in names if not name.endswith("/")
        }
        _forbid_paths(flattened, Artifact("sdist", path, "", ""), disallowed_paths)

        metadata_name = next(
            (
                name
                for name in names
                if name.endswith("/PKG-INFO") or name == "PKG-INFO"
            ),
            None,
        )
        if metadata_name is None:
            raise ValueError("sdist artifact missing PKG-INFO")

        metadata_member = archive.getmember(metadata_name)
        file_obj = archive.extractfile(metadata_member)
        if file_obj is None:
            raise ValueError("sdist artifact missing PKG-INFO file")
        metadata_data = file_obj.read().decode("utf-8")

    metadata = _parse_metadata(metadata_data)
    metadata_name_value = metadata[0]
    metadata_version = metadata[1]

    if _normalize_name(metadata_name_value) != _normalize_name(expected_name):
        raise ValueError(
            f"sdist metadata name mismatch: {metadata_name_value} != "
            f"{expected_name}"
        )
    if metadata_version != expected_version:
        raise ValueError(
            f"sdist metadata version mismatch: {metadata_version} != "
            f"{expected_version}"
        )

    artifact = Artifact("sdist", path, metadata_name_value, metadata_version)
    _require_paths(flattened, artifact, required_paths)
    _forbid_paths(flattened, artifact, disallowed_paths)

    return artifact


def _strip_sdist_root(name):
    parts = [segment for segment in name.split("/") if segment]
    if len(parts) <= 1:
        return "" if not parts else parts[0]

    return "/".join(parts[1:])
