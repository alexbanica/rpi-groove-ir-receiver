from ir_receiver.domains.entities.IrPulseCapture import IrPulseCapture
from ir_receiver.domains.interfaces.PulsePersistenceInterface import PulsePersistenceInterface


class PulsePersistenceService:
    def __init__(self, pulse_persistence: PulsePersistenceInterface):
        self._pulse_persistence = pulse_persistence

    def save(self, filename: str, gpio_in: int, pulses: list[int]) -> None:
        capture = IrPulseCapture(gpio_in=int(gpio_in), pulse_us=[int(item) for item in pulses])
        self._pulse_persistence.save(filename=filename, capture=capture)
