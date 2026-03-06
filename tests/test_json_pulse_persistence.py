import json
import os
import tempfile
import unittest

from ir_receiver.domains.entities.IrPulseCapture import IrPulseCapture
from ir_receiver.infrastructures.persistences.JsonPulsePersistence import JsonPulsePersistence
from ir_receiver.shared.constants.JsonKeys import JsonKeys


class JsonPulsePersistenceTest(unittest.TestCase):
    def test_saves_expected_json_shape(self):
        persistence = JsonPulsePersistence()
        capture = IrPulseCapture(gpio_in=16, pulse_us=[1000, 500, 1500])

        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            file_path = tmp_file.name

        try:
            persistence.save(file_path, capture)

            with open(file_path, "r", encoding="utf-8") as result_file:
                saved = json.load(result_file)

            self.assertEqual({JsonKeys.GPIO_IN, JsonKeys.PULSE_US}, set(saved.keys()))
            self.assertEqual(16, saved[JsonKeys.GPIO_IN])
            self.assertEqual([1000, 500, 1500], saved[JsonKeys.PULSE_US])
        finally:
            os.unlink(file_path)


if __name__ == "__main__":
    unittest.main()
