import json

from ir_receiver.domains.entities.IrPulseCapture import IrPulseCapture
from ir_receiver.domains.interfaces.PulsePersistenceInterface import PulsePersistenceInterface
from ir_receiver.shared.constants.CliStrings import CliStrings
from ir_receiver.shared.constants.JsonKeys import JsonKeys


class JsonPulsePersistence(PulsePersistenceInterface):
    def save(self, filename: str, capture: IrPulseCapture) -> None:
        data = {
            JsonKeys.GPIO_IN: int(capture.gpio_in),
            JsonKeys.PULSE_US: [int(item) for item in capture.pulse_us],
        }

        with open(filename, "w", encoding="utf-8") as output_file:
            json.dump(data, output_file, indent=2)

        print(CliStrings.SAVED_FILE.format(count=len(capture.pulse_us), filename=filename))
