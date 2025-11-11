from __future__ import annotations
from typing import Dict, Any, Optional, List
from .kmm_engine_v02 import KernelMemoryModelV02

class MemoryOps:
    def __init__(self, kmm: KernelMemoryModelV02) -> None:
        self.kmm = kmm

    def encode_and_bind(self, subject_id: str, event_type: str, payload: Dict[str, Any],
                        salience: float, credibility: float, prev_id: Optional[str] = None) -> str:
        n = self.kmm.encode_event(subject_id, event_type, payload, salience, credibility)
        if prev_id:
            self.kmm.bind(prev_id, n.id, rel="temporal", weight=0.5)
        return n.id
