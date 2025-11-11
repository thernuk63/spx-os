from dataclasses import dataclass, field
from enum import Enum
from typing import Dict
from time import monotonic

class IntentionStatus(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

@dataclass(frozen=True)
class Intention:
    id: str
    goal: str
    params: Dict
    expected_effect: Dict
    risk: float
    cost: float
    priority: float
    source_event: str
    origin: str
    stop_criteria: Dict
    status: IntentionStatus = IntentionStatus.PENDING
    ts_T1: float = field(default_factory=monotonic)
    valid: bool = True

    def __post_init__(self):
        if not (0 <= self.priority <= 1):
            raise ValueError("Invalid priority")
        if not (0 <= self.risk <= 1):
            raise ValueError("Invalid risk")
