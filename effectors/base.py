from abc import ABC, abstractmethod
from typing import Dict, Any

class Effector(ABC):
    name: str

    @abstractmethod
    def execute(self, params: Dict[str, Any]) -> None:
        ...
