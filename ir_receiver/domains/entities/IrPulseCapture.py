from dataclasses import dataclass


@dataclass(frozen=True)
class IrPulseCapture:
    gpio_in: int
    pulse_us: list[int]
