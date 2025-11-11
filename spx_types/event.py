# spx_types/event.py
from dataclasses import dataclass, field, replace
from enum import Enum, auto
from typing import Dict, Any, Optional
from time import monotonic
from uuid import uuid4


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
    origin: str                    # "KERNEL" або subject_id
    subject_id: Optional[str]      # None для kernel-подій
    salience: float
    credibility: float
    context: Dict[str, Any] = field(default_factory=dict)
    ts_T0: float = field(default_factory=monotonic)
    ts_T1: Optional[float] = None
    channel: EventChannel = EventChannel.SUBJECT
    valid: bool = True

    def __post_init__(self):
        if not (0.0 <= self.salience <= 1.0):
            raise ValueError("Invalid salience")
        if not (0.0 <= self.credibility <= 1.0):
            raise ValueError("Invalid credibility")

    # ---- helpers ----
    def is_kernel(self) -> bool:
        return self.channel == EventChannel.KERNEL

    @staticmethod
    def kernel(type_: EventType, payload: Dict[str, Any] | None = None, *, eid: Optional[str] = None) -> "Event":
        return Event(
            id=eid or f"kev-{uuid4().hex[:10]}",
            type=type_,
            payload=payload or {},
            origin="KERNEL",
            subject_id=None,
            salience=1.0,
            credibility=1.0,
            channel=EventChannel.KERNEL,
            context={}
        )

    @staticmethod
    def subject(subject_id: str, type_: EventType, payload: Dict[str, Any] | None = None, *, eid: Optional[str] = None,
                salience: float = 0.5, credibility: float = 1.0, context: Optional[Dict[str, Any]] = None) -> "Event":
        return Event(
            id=eid or f"sev-{uuid4().hex[:10]}",
            type=type_,
            payload=payload or {},
            origin=subject_id,
            subject_id=subject_id,
            salience=salience,
            credibility=credibility,
            channel=EventChannel.SUBJECT,
            context=context or {}
        )

    def with_t1(self, t1: float) -> "Event":
        return replace(self, ts_T1=t1)
