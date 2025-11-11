from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, Optional
from time import monotonic
import uuid

def _nid(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex[:10]}"

@dataclass
class BaseNode:
    id: str
    subject_id: str
    kind: str
    t0: float
    salience: float
    credibility: float
    payload: Dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["type"] = self.__class__.__name__
        return d

@dataclass
class WorkingMemoryNode(BaseNode):
    @classmethod
    def new(cls, subject_id: str, kind: str, payload: Dict[str, Any],
            salience: float, credibility: float, t0: Optional[float] = None) -> "WorkingMemoryNode":
        return cls(
            id=_nid("wm"),
            subject_id=subject_id,
            kind=kind,
            t0=t0 or monotonic(),
            salience=salience,
            credibility=credibility,
            payload=payload or {},
        )

@dataclass
class EpisodicNode(BaseNode):
    # Можна додати episode_id / arc_id у наступних версіях
    @classmethod
    def from_wm(cls, wm: WorkingMemoryNode) -> "EpisodicNode":
        return cls(
            id=_nid("em"),
            subject_id=wm.subject_id,
            kind=wm.kind,
            t0=wm.t0,
            salience=wm.salience,
            credibility=wm.credibility,
            payload=dict(wm.payload),
        )

@dataclass
class SemanticNode(BaseNode):
    # Узагальнені знання; наразі skeleton
    pass

@dataclass
class EmotionalTag:
    id: str
    node_id: str
    emotion: str
    intensity: float  # 0..1
    t0: float

    @classmethod
    def new(cls, node_id: str, emotion: str, intensity: float) -> "EmotionalTag":
        return cls(id=_nid("tag"), node_id=node_id, emotion=emotion, intensity=max(0.0, min(1.0, intensity)), t0=monotonic())

    def as_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "node_id": self.node_id,
            "emotion": self.emotion,
            "intensity": self.intensity,
            "t0": self.t0,
            "type": "EmotionalTag",
        }

@dataclass
class CognitiveContext:
    id: str
    subject_id: str
    label: str
    t0: float
    data: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def new(cls, subject_id: str, label: str, data: Optional[Dict[str, Any]] = None) -> "CognitiveContext":
        return cls(id=_nid("ctx"), subject_id=subject_id, label=label, t0=monotonic(), data=data or {})

    def as_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id, "subject_id": self.subject_id, "label": self.label, "t0": self.t0,
            "data": dict(self.data), "type": "CognitiveContext",
        }
