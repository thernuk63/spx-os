from dataclasses import dataclass, field
from typing import List, Dict
from time import monotonic

@dataclass(frozen=True)
class StateSnapshot:
    id: str
    scene_id: str
    entities: List
    relations: List
    recency: float
    salience_map: Dict[str, float]
    origin: str
    ts_T1: float = field(default_factory=monotonic)
    valid: bool = True

    def __post_init__(self):
        if not (0.0 <= self.recency <= 1.0):
            raise ValueError("Invalid recency value")
