from typing import Dict, Any, Optional, Type
from utils.diagnostics import log_info

class SubjectProcessManager:
    def __init__(self):
        self.registry: Dict[str, Any] = {}

    @classmethod
    def init(cls) -> "SubjectProcessManager":
        spm = cls()
        log_info("SPM: ready.")
        return spm

    def spawn(self, subject_cls: Type, *args, **kwargs):
        subj = subject_cls(*args, **kwargs)
        self.registry[subj.subject_id] = subj
        log_info(f"SPM: spawned subject {subj.subject_id}.")
        return subj

    def get(self, subject_id: str):
        return self.registry.get(subject_id)
