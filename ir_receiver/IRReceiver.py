#!/usr/bin/env python3

from ir_receiver.applications.services.IrPulseNormalizer import IrPulseNormalizer
from ir_receiver.applications.services.PulsePersistenceService import PulsePersistenceService
from ir_receiver.infrastructures.persistences.JsonPulsePersistence import JsonPulsePersistence
from ir_receiver.infrastructures.recorders.PigpioPulseRecorder import PigpioPulseRecorder


class IRReceiver:
    """
    Backward-compatible facade for raw IR pulse recording and persistence.
    """

    def __init__(self, pi, gpio_in: int, invert: bool = True):
        self.pi = pi
        self.gpio = gpio_in
        self.invert = invert
        self._recorder = PigpioPulseRecorder(pi, gpio_in)
        self._normalizer = IrPulseNormalizer()
        self._persistence_service = PulsePersistenceService(JsonPulsePersistence())

    def record_single(self, timeout: float = 10.0, gap: float = 0.15) -> list[int]:
        return self._recorder.record_single(timeout=timeout, gap=gap)

    @staticmethod
    def normalize_pulses(pulses: list[int], isWithRepeats: bool = True) -> list[int]:
        return IrPulseNormalizer().normalize(pulses, is_with_repeats=isWithRepeats)

    @staticmethod
    def remove_repeats(pulses: list[int]) -> list[int]:
        return IrPulseNormalizer().remove_repeats(pulses)

    @staticmethod
    def save_pulses(filename: str, gpio_in: int, pulses: list[int]):
        PulsePersistenceService(JsonPulsePersistence()).save(filename=filename, gpio_in=gpio_in, pulses=pulses)
