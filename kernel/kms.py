# kernel/kms.py
from __future__ import annotations
from dataclasses import dataclass
from time import monotonic
from typing import List, Dict, Any, Union, Optional
from utils.diagnostics import log_info

@dataclass
class _KMSCfg:
    hb_period: float = 0.15
    rf_trigger_debt: int = 4
    rf_max_cycles: int = 2
    kernel_overload_threshold: int = 6
    fairness_decay: float = 0.85

class KernelMetaScheduler:
    """
    KMS v0.2 (Hybrid):
      - HB: round-robin hb_cycle()
      - RF: вікно суб'єктів з найбільшим debt; rf_cycle(); fairness decay
      - Тригери входу в RF: debt ≥ rf_trigger_debt або kernel_overload
      - Вікно RF обмежене rf_max_cycles; після — повернення у HB
    """

    def __init__(self, cfg: _KMSCfg):
        self.cfg = cfg
        self._subjects: List[str] = []
        self._rr_idx: int = 0

        self._phase: str = "HB"         # "HB" | "RF"
        self._rf_started_at: Optional[float] = None
        self._rf_cycles_left: int = 0
        self._rf_window: List[str] = []

        # прості метрики
        self._hb_processed: Dict[str, int] = {}   # к-ть циклів HB суб'єкта
        self._last_debt: Dict[str, float] = {}    # відслідковуємо debt

    @classmethod
    def init(cls, system_cfg: Dict[str, Any]) -> "KernelMetaScheduler":
        # зберігаємо зворотну сумісність (старі ключі можуть бути у system_cfg)
        sched = (system_cfg or {}).get("scheduler", {}) or {}
        cfg = _KMSCfg(
            hb_period=float(system_cfg.get("hb_period", 0.15)),
            rf_trigger_debt=int(sched.get("rf_trigger_debt", 4)),
            rf_max_cycles=int(sched.get("rf_max_cycles", 2)),
            kernel_overload_threshold=int(sched.get("kernel_overload_threshold", 6)),
            fairness_decay=float(sched.get("fairness_decay", 0.85)),
        )
        return cls(cfg)

    # ----------------- Registration -----------------

    def register(self, subject_or_id: Union[str, Any]) -> None:
        sid = subject_or_id if isinstance(subject_or_id, str) else getattr(subject_or_id, "subject_id", None)
        if not sid:
            raise ValueError("KMS.register: subject id not provided")
        if sid not in self._subjects:
            self._subjects.append(sid)
            self._hb_processed.setdefault(sid, 0)
            self._last_debt.setdefault(sid, 0.0)

    # ----------------- Debt model -----------------

    def _compute_debt(self, kem) -> Dict[str, float]:
        debt: Dict[str, float] = {}
        for sid in self._subjects:
            qlen = kem.subject_len(sid)
            hb = self._hb_processed.get(sid, 0)
            debt[sid] = max(0.0, float(qlen - hb))
        return debt

    def _kernel_overloaded(self, kem) -> bool:
        try:
            return kem.kernel_len() >= self.cfg.kernel_overload_threshold
        except Exception:
            return False

    # ----------------- Phase control -----------------

    def phase(self) -> str:
        return self._phase

    def on_cycle_begin(self, kem, kmm) -> None:
        # Переоцінюємо debt перед кожним зовнішнім тактом
        debt = self._compute_debt(kem)

        if self._phase == "HB":
            # Тригери входу в RF
            if any(v >= self.cfg.rf_trigger_debt for v in debt.values()) or self._kernel_overloaded(kem):
                # Вибір RF window: суб'єкти з найбільшим debt (стабільне сортування)
                ranked = sorted(self._subjects, key=lambda s: debt.get(s, 0.0), reverse=True)
                self._rf_window = [s for s in ranked if debt.get(s, 0.0) > 0.0]
                if self._rf_window:
                    self._enter_rf()
        else:
            # У RF працюємо обмежену к-сть циклів
            if self._rf_cycles_left <= 0:
                self._exit_rf()
            else:
                self._rf_cycles_left -= 1
                # fairness decay: зменшуємо debt (модель "рухи вперед")
                for s in self._rf_window:
                    self._last_debt[s] = max(0.0, self._last_debt.get(s, 0.0) * self.cfg.fairness_decay)

        # зберігаємо останню оцінку debt для діагностики
        self._last_debt = debt

    def on_cycle_end(self) -> None:
        pass

    def _enter_rf(self) -> None:
        self._phase = "RF"
        self._rf_started_at = monotonic()
        self._rf_cycles_left = self.cfg.rf_max_cycles
        log_info(f"KMS: entering RF (window={self._rf_window})")

    def _exit_rf(self) -> None:
        self._phase = "HB"
        self._rf_started_at = None
        self._rf_cycles_left = 0
        self._rf_window = []
        log_info("KMS: exiting RF → HB")

    # ----------------- Scheduling order -----------------

    def schedule_cycle_order(self) -> List[str]:
        if not self._subjects:
            return []
        if self._phase == "RF":
            # PID0 → ROOT → інші з RF window у такому ж порядку
            pid0_first = [s for s in self._rf_window if s.upper() == "PID0"]
            root_second = [s for s in self._rf_window if s.upper() == "ROOT"]
            others = [s for s in self._rf_window if s.upper() not in ("PID0", "ROOT")]
            order = pid0_first + root_second + others
            return order if order else self._subjects[:]  # fallback
        # HB: round-robin
        order = self._subjects[self._rr_idx:] + self._subjects[:self._rr_idx]
        self._rr_idx = (self._rr_idx + 1) % len(self._subjects)
        return order

    # ----------------- Bookkeeping API -----------------

    def notify_hb_processed(self, subject_id: str) -> None:
        self._hb_processed[subject_id] = self._hb_processed.get(subject_id, 0) + 1

    # для діагностики
    def snapshot(self) -> Dict[str, Any]:
        return {
            "phase": self._phase,
            "subjects": self._subjects[:],
            "hb_processed": dict(self._hb_processed),
            "last_debt": dict(self._last_debt),
            "rf_window": self._rf_window[:],
            "rf_cycles_left": self._rf_cycles_left,
        }
