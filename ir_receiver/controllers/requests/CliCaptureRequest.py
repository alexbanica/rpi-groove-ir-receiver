from dataclasses import dataclass


@dataclass(frozen=True)
class CliCaptureRequest:
    in_gpio: int
    out_file: str
    timeout: float
    gap: float
    bursts: int
