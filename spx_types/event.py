from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict, Any, Optional
from time import monotonic


class EventType(Enum):
    SYSTEM = "SystemEvent"
    PERCEPTION = "PerceptionEvent"
    INTENTION = "IntentionEvent"
    ACTION = "ActionEvent"
    MEMORY = "MemoryEvent"


class EventChannel(Enum):
    KERNEL = auto()
    SUBJECT = auto()


@dataclass(frozen=True)
class Event:
    id: str
    type: EventType
    payload: Dict[str, Any]
    origin: str                    # "KERNEL" або ім’я суб’єкта
    subject_id: Optional[str]      # може бути None для kernel
    salience: float                # 0.0–1.0
    credibility: float             # 0.0–1.0
    context: Dict[str, Any] = field(default_factory=dict)

    # Times
    ts_T0: float = field(default_factory=monotonic)
    ts_T1: Optional[float] = None   # у v0.1 дорівнює T0

    # Channel for KEM dual-queue
    channel: EventChannel = EventChannel.SUBJECT

    valid: bool = True

    def __post_init__(self):
        if not (0.0 <= self.salience <= 1.0):
            raise ValueError("Invalid salience")
        if not (0.0 <= self.credibility <= 1.0):
            raise ValueError("Invalid credibility")
