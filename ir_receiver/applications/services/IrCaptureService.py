import time

from ir_receiver.domains.dtos.CaptureOptionsDto import CaptureOptionsDto
from ir_receiver.domains.interfaces.PulseRecorderInterface import PulseRecorderInterface


class IrCaptureService:
    def __init__(self, pulse_recorder: PulseRecorderInterface):
        self._pulse_recorder = pulse_recorder

    def capture_bursts(self, options: CaptureOptionsDto) -> list[list[int]]:
        captured: list[list[int]] = []
        bursts_to_capture = max(1, options.bursts)

        for _ in range(bursts_to_capture):
            pulses = self._pulse_recorder.record_single(timeout=options.timeout, gap=options.gap)
            if pulses:
                captured.append(pulses)
            time.sleep(0.2)

        return captured
