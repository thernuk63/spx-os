from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Dict
import uuid

def _eid(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex[:10]}"

@dataclass
class BaseEdge:
    id: str
    src: str
    dst: str
    weight: float  # 0..1

    def as_dict(self) -> Dict:
        d = asdict(self)
        d["type"] = self.__class__.__name__
        return d

@dataclass
class TemporalEdge(BaseEdge):
    @classmethod
    def new(cls, src: str, dst: str, weight: float = 0.5) -> "TemporalEdge":
        return cls(id=_eid("te"), src=src, dst=dst, weight=max(0.0, min(1.0, weight)))

@dataclass
class CausalEdge(BaseEdge):
    @classmethod
    def new(cls, src: str, dst: str, weight: float = 0.5) -> "CausalEdge":
        return cls(id=_eid("ce"), src=src, dst=dst, weight=max(0.0, min(1.0, weight)))

@dataclass
class AssociationEdge(BaseEdge):
    @classmethod
    def new(cls, src: str, dst: str, weight: float = 0.5) -> "AssociationEdge":
        return cls(id=_eid("ae"), src=src, dst=dst, weight=max(0.0, min(1.0, weight)))
