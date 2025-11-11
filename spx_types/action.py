from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Optional
from time import monotonic

class AckPolicy(Enum):
    NONE = "none"
    REQUIRED = "required"

@dataclass(frozen=True)
class Action:
    id: str
    effector: str
    params: Dict
    idempotency_key: str
    ack_policy: AckPolicy
    compensation: Optional[Dict]
    origin: str
    ts_T1: float = field(default_factory=monotonic)
    valid: bool = True
