"""Release tag validation and mapping helpers."""

from dataclasses import dataclass
import re


class ReleaseVersionError(ValueError):
    pass


@dataclass(frozen=True)
class ReleaseTag:
    tag: str
    distribution_version: str


_TAG_PATTERN = re.compile(
    r"^(?P<major>0|[1-9][0-9]*)\.(?P<minor>0|[1-9][0-9]*)\.(?P<patch>0|[1-9][0-9]*)(?:-beta(?P<beta>[1-9][0-9]*))?$"
)


def parse_release_tag(tag: object) -> ReleaseTag:
    if tag is None or tag == "":
        raise ReleaseVersionError("release tag is required")

    if not isinstance(tag, str):
        raise ReleaseVersionError(f"unsupported release tag: {tag}")

    match = _TAG_PATTERN.fullmatch(tag)
    if not match:
        raise ReleaseVersionError(f"unsupported release tag: {tag}")

    beta = match.group("beta")
    if beta is None:
        return ReleaseTag(tag=tag, distribution_version=tag)

    base = f"{match.group('major')}.{match.group('minor')}.{match.group('patch')}"
    return ReleaseTag(tag=tag, distribution_version=f"{base}b{beta}")
