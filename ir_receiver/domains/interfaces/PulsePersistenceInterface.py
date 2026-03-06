from abc import ABC, abstractmethod

from ir_receiver.domains.entities.IrPulseCapture import IrPulseCapture


class PulsePersistenceInterface(ABC):
    @abstractmethod
    def save(self, filename: str, capture: IrPulseCapture) -> None:
        pass
