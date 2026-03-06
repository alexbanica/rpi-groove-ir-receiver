from abc import ABC, abstractmethod


class PulseRecorderInterface(ABC):
    @abstractmethod
    def record_single(self, timeout: float, gap: float) -> list[int]:
        pass
