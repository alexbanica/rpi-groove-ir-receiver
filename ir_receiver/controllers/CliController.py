import argparse
import sys

from ir_receiver.applications.services.BurstSelectionService import BurstSelectionService
from ir_receiver.applications.services.IrCaptureService import IrCaptureService
from ir_receiver.applications.services.IrPulseNormalizer import IrPulseNormalizer
from ir_receiver.applications.services.PulsePersistenceService import PulsePersistenceService
from ir_receiver.controllers.requests.CliCaptureRequest import CliCaptureRequest
from ir_receiver.controllers.responses.CliCaptureResponse import CliCaptureResponse
from ir_receiver.domains.dtos.CaptureOptionsDto import CaptureOptionsDto
from ir_receiver.infrastructures.gpio.PigpioConnectionFactory import PigpioConnectionFactory
from ir_receiver.infrastructures.persistences.JsonPulsePersistence import JsonPulsePersistence
from ir_receiver.infrastructures.recorders.PigpioPulseRecorder import PigpioPulseRecorder
from ir_receiver.shared.constants.CliDefaults import CliDefaults
from ir_receiver.shared.constants.CliStrings import CliStrings


class CliController:
    def __init__(self):
        self._capture_service = None
        self._normalizer = IrPulseNormalizer()
        self._selection_service = BurstSelectionService()
        self._persistence_service = PulsePersistenceService(JsonPulsePersistence())

    def parse_args(self) -> CliCaptureRequest:
        parser = argparse.ArgumentParser(description=CliStrings.DESCRIPTION)
        parser.add_argument("--in-gpio", type=int, default=CliDefaults.IN_GPIO, help=CliStrings.ARG_IN_GPIO_HELP)
        parser.add_argument("--out-file", type=str, required=True, help=CliStrings.ARG_OUT_FILE_HELP)
        parser.add_argument("--timeout", type=float, default=CliDefaults.TIMEOUT_SECONDS, help=CliStrings.ARG_TIMEOUT_HELP)
        parser.add_argument("--gap", type=float, default=CliDefaults.GAP_SECONDS, help=CliStrings.ARG_GAP_HELP)
        parser.add_argument("--bursts", type=int, default=CliDefaults.BURSTS, help=CliStrings.ARG_BURSTS_HELP)

        args = parser.parse_args()
        return CliCaptureRequest(
            in_gpio=args.in_gpio,
            out_file=args.out_file,
            timeout=args.timeout,
            gap=args.gap,
            bursts=args.bursts,
        )

    def execute(self, request: CliCaptureRequest) -> CliCaptureResponse:
        pi_connection = PigpioConnectionFactory().create_connection()
        if not pi_connection.connected:
            print(CliStrings.PIGPIO_CONNECT_ERROR)
            sys.exit(2)

        self._capture_service = IrCaptureService(PigpioPulseRecorder(pi_connection, request.in_gpio))
        print(CliStrings.WAITING_FOR_SIGNAL.format(gpio=request.in_gpio, timeout=request.timeout))

        options = CaptureOptionsDto(timeout=request.timeout, gap=request.gap, bursts=request.bursts)
        captured = self._capture_with_progress(options)

        if not captured:
            print(CliStrings.NO_BURSTS_CAPTURED)
            pi_connection.stop()
            sys.exit(1)

        selected_index = self._select_index(captured)
        selected = self._selection_service.select(captured, selected_index)
        pulses = self._normalizer.normalize(selected, is_with_repeats=False)
        self._persistence_service.save(request.out_file, request.in_gpio, pulses)
        pi_connection.stop()
        print(CliStrings.DONE)
        return CliCaptureResponse(success=True, message=CliStrings.DONE)

    def _capture_with_progress(self, options: CaptureOptionsDto) -> list[list[int]]:
        captured: list[list[int]] = []
        bursts_to_capture = max(1, options.bursts)

        for index in range(bursts_to_capture):
            print(CliStrings.CAPTURE_PROGRESS.format(index=index + 1, total=bursts_to_capture))
            pulses = self._capture_service.capture_bursts(CaptureOptionsDto(
                timeout=options.timeout,
                gap=options.gap,
                bursts=1,
            ))
            if not pulses:
                print(CliStrings.NO_SIGNAL_CAPTURED)
            else:
                first_pulse = pulses[0]
                print(CliStrings.CAPTURED_DURATIONS.format(count=len(first_pulse), first=first_pulse[:8]))
                captured.append(first_pulse)

        return captured

    def _select_index(self, captured: list[list[int]]) -> int:
        if len(captured) <= 1:
            return 0

        max_index = len(captured) - 1
        print(CliStrings.CHOOSE_PROMPT_HEADER.format(count=len(captured), max_index=max_index))
        for index, pulses in enumerate(captured):
            print(CliStrings.CHOOSE_ENTRY.format(index=index, count=len(pulses), first8=pulses[:8]))

        try:
            selected_value = input(CliStrings.CHOOSE_INDEX_PROMPT).strip()
            if selected_value == "":
                return 0
            selected = int(selected_value)
            if selected < 0 or selected > max_index:
                return 0
            return selected
        except Exception:
            return 0
