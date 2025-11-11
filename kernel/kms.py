from typing import List
from utils.diagnostics import log_info
from utils.metrics import compute_cognitive_debt
from dataclasses import dataclass

@dataclass
class SchedConfig:
    hb_period: float
    rf_slot_max: float
    debt_threshold: int
    salience_threshold: float

class KernelMetaScheduler:
    def __init__(self, cfg: SchedConfig):
        self.cfg = cfg
        self.runnable: List[str] = []  # subject ids round-robin

    @classmethod
    def init(cls, system_cfg) -> "KernelMetaScheduler":
        cfg = SchedConfig(
            hb_period=float(system_cfg["HB_period"]),
            rf_slot_max=float(system_cfg["RF_slot_max"]),
            debt_threshold=int(system_cfg["debt_threshold"]),
            salience_threshold=float(system_cfg.get("salience_threshold", 0.7)),
        )
        kms = cls(cfg)
        log_info("KMS: online (HB↔RF only).")
        return kms

    def register(self, subject_id: str):
        if subject_id not in self.runnable:
            self.runnable.append(subject_id)

    def schedule_cycle_order(self) -> List[str]:
        # v0.1: simple round-robin order
        if not self.runnable: return []
        # rotate
        sid = self.runnable.pop(0)
        self.runnable.append(sid)
        return [sid]
