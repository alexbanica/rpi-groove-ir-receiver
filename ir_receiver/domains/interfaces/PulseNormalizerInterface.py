from abc import ABC, abstractmethod


class PulseNormalizerInterface(ABC):
    @abstractmethod
    def normalize(self, pulses: list[int], is_with_repeats: bool = True) -> list[int]:
        pass

    @abstractmethod
    def remove_repeats(self, pulses: list[int]) -> list[int]:
        pass
