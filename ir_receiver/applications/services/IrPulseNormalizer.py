from ir_receiver.domains.interfaces.PulseNormalizerInterface import PulseNormalizerInterface
from ir_receiver.shared.constants.NormalizationRules import NormalizationRules


class IrPulseNormalizer(PulseNormalizerInterface):
    def normalize(self, pulses: list[int], is_with_repeats: bool = True) -> list[int]:
        if not pulses:
            return []

        sanitized = [int(item) for item in pulses]
        merged: list[int] = []
        for duration in sanitized:
            if merged and duration < NormalizationRules.MERGE_THRESHOLD_US:
                merged[-1] += duration
            else:
                merged.append(duration)

        while merged and merged[-1] > NormalizationRules.TRAILING_GAP_THRESHOLD_US:
            merged.pop()

        if not merged:
            return []

        if len(merged) >= 2 and self._is_short(merged[0]) and self._is_long(merged[1]):
            merged = merged[1:]

        if not is_with_repeats:
            merged = self.remove_repeats(merged)

        return [int(item) for item in merged]

    def remove_repeats(self, pulses: list[int]) -> list[int]:
        # Placeholder to preserve current behavior.
        return pulses

    def _is_short(self, value: int) -> bool:
        return value < NormalizationRules.SHORT_THRESHOLD_US

    def _is_long(self, value: int) -> bool:
        return value >= NormalizationRules.LONG_THRESHOLD_US
