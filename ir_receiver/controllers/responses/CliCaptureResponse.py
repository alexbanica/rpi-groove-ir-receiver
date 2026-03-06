from dataclasses import dataclass


@dataclass(frozen=True)
class CliCaptureResponse:
    success: bool
    message: str
