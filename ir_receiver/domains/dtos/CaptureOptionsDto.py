from dataclasses import dataclass


@dataclass(frozen=True)
class CaptureOptionsDto:
    timeout: float
    gap: float
    bursts: int
