from typing import List, Dict, Any
from modules.perception import PerceptionBus
from modules.cognition import CognitionCore
from modules.intention import IntentionManager
from modules.action import ActionExecutor
from kernel.kmm import KernelMemoryModel
from kernel.kem import KernelEventMesh
from kernel.isp import ISP
from utils.diagnostics import log_info

class BaseSubject:
    def __init__(self, subject_id: str, kem: KernelEventMesh, kmm: KernelMemoryModel, isp: ISP):
        self.subject_id = subject_id
        self.perception = PerceptionBus()
        self.cognition = CognitionCore()
        self.intention = IntentionManager()
        self.ae = ActionExecutor(isp, registry={})  # effectors bound by child
        self.kem = kem
        self.kmm = kmm
        self.state: Dict[str, Any] = {}

    def hb_cycle(self):
        # minimal HB skeleton
        events = self.kem.fetch_for(self.subject_id)
        norm = self.perception.normalize(events)
        analysis = self.cognition.analyze(norm)
        # v0.1: just log
        log_info(f"{self.subject_id}: HB analysis {analysis}")

    def rf_cycle(self):
        log_info(f"{self.subject_id}: entering RF (freeze AE).")
        # v0.1: no-op consolidation
        log_info(f"{self.subject_id}: leaving RF → HB.")
