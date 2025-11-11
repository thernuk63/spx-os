from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any
from time import monotonic

class MemoryOpType(Enum):
    ENCODE = "encode"
    RETRIEVE = "retrieve"
    BIND = "bind"

@dataclass(frozen=True)
class MemoryOp:
    id: str
    op: MemoryOpType
    scope: str   # "WM" or "EM"
    indices: Dict[str, Any]
    payload: Dict[str, Any]
    origin: str
    ts_T1: float = field(default_factory=monotonic)
    valid: bool = True
