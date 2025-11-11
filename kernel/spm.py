# kernel/spm.py
from __future__ import annotations
from typing import Type, Dict, Any
from uuid import uuid4
from utils.diagnostics import log_info
from spx_types.event import Event, EventType, EventChannel

SYSTEM_IDS = {"PID0", "ROOT"}

class SubjectProcessManager:
    def __init__(self):
        self.registry: Dict[str, Any] = {}  # subject_id -> subject ref

    @classmethod
    def init(cls) -> "SubjectProcessManager":
        return cls()

    def _make_subject_id(self, cls_: Type, cfg: Dict[str, Any] | None) -> str:
        # Статичні ID для системних суб'єктів; інші — UUID
        if cfg and "subject_id" in cfg:
            return cfg["subject_id"]
        name = getattr(cls_, "__name__", "").upper()
        if name == "PID0":
            return "PID0"
        if name in {"ROOT", "ROOTSUBJECT"}:
            return "ROOT"
        return f"SUBJ-{uuid4().hex[:8]}"

    def spawn(self, cls_: Type, kem, kmm, isp, cfg: Dict[str, Any] | None = None):
        subject_id = self._make_subject_id(cls_, cfg)
        subject = cls_(subject_id=subject_id, kem=kem, kmm=kmm, isp=isp, cfg=cfg or {})
        self.registry[subject_id] = subject
        log_info(f"SPM: spawned subject {subject_id}.")

        # Kernel-подія про спавн
        kem.publish_kernel_event(Event(
            id=f"spawn-{subject_id}",
            type=EventType.SYSTEM,
            payload={"event": "SUBJECT_SPAWNED", "subject_id": subject_id},
            origin="KERNEL",
            subject_id=None,
            salience=1.0,
            credibility=1.0,
            channel=EventChannel.KERNEL,
            context={}
        ))
        return subject

    def get(self, subject_id: str):
        return self.registry.get(subject_id)
