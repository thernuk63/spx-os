from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any
from time import monotonic

class EventType(Enum):
    SYSTEM = "SystemEvent"
    PERCEPTION = "PerceptionEvent"
    INTENTION = "IntentionEvent"
    ACTION = "ActionEvent"
    MEMORY = "MemoryEvent"

@dataclass(frozen=True)
class Event:
    id: str
    type: EventType
    payload: Dict[str, Any]
    origin: str  # subject_id або 'KERNEL'
    salience: float
    credibility: float
    context: Dict[str, Any]
    ts_T0: float = field(default_factory=monotonic)
    valid: bool = True

    def __post_init__(self):
        if not (0.0 <= self.salience <= 1.0):
            raise ValueError("Invalid salience")
        if not (0.0 <= self.credibility <= 1.0):
            raise ValueError("Invalid credibility")
