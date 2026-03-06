import unittest

from ir_receiver.applications.services.IrPulseNormalizer import IrPulseNormalizer


class IrPulseNormalizerTest(unittest.TestCase):
    def setUp(self):
        self.normalizer = IrPulseNormalizer()

    def test_returns_empty_for_empty_input(self):
        self.assertEqual([], self.normalizer.normalize([]))

    def test_merges_tiny_durations_and_keeps_header_trim_behavior(self):
        pulses = [900, 20, 25, 1500]
        self.assertEqual([1500], self.normalizer.normalize(pulses))

    def test_trims_trailing_long_gap(self):
        pulses = [900, 1600, 21000]
        self.assertEqual([1600], self.normalizer.normalize(pulses))

    def test_drops_short_then_long_header_pattern(self):
        pulses = [500, 1600, 600, 700]
        self.assertEqual([1600, 600, 700], self.normalizer.normalize(pulses))

    def test_remove_repeats_is_noop(self):
        pulses = [100, 200, 300]
        self.assertEqual(pulses, self.normalizer.normalize(pulses, is_with_repeats=False))


if __name__ == "__main__":
    unittest.main()
