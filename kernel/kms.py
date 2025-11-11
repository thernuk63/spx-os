# kernel/kms.py
from __future__ import annotations
from dataclasses import dataclass
from time import monotonic
from typing import List, Dict, Any, Union
from utils.diagnostics import log_info

@dataclass
class _KMSCfg:
    hb_period: float = 0.1
    rf_slot_max: float = 1.0
    rf_cooldown: float = 0.5
    debt_threshold: int = 5
    entropy_threshold: float = 0.7

class KernelMetaScheduler:
    """
    KMS v0.1/0.2 — керує фазами HB↔RF і порядком виконання суб’єктів.
    - Single-threaded cooperative model
    - HB має пріоритет за замовчуванням
    - RF вмикається за тригерами (борг/ентропія) і працює не довше за rf_slot_max
    """

    def __init__(self, cfg: _KMSCfg):
        self.cfg = cfg
        self._subjects: List[str] = []      # round-robin
        self._rr_idx: int = 0

        self._phase: str = "HB"             # "HB" | "RF"
        self._rf_started_at: float | None = None
        self._rf_last_exit_at: float = 0.0

    @classmethod
    def init(cls, system_cfg: Dict[str, Any]) -> "KernelMetaScheduler":
        rf = system_cfg.get("rf_triggers", {}) or {}
        cfg = _KMSCfg(
            hb_period=float(system_cfg.get("hb_period", 0.1)),
            rf_slot_max=float(system_cfg.get("rf_slot_max", 1.0)),
            rf_cooldown=float(system_cfg.get("rf_cooldown", 0.5)),
            debt_threshold=int(rf.get("debt_threshold", 5)),
            entropy_threshold=float(rf.get("entropy_threshold", 0.7)),
        )
        return cls(cfg)

    # ----------------- Registration / ordering -----------------

    def register(self, subject_or_id: Union[str, Any]) -> None:
        sid = subject_or_id if isinstance(subject_or_id, str) else getattr(subject_or_id, "subject_id", None)
        if not sid:
            raise ValueError("KMS.register: subject id not provided")
        if sid not in self._subjects:
            self._subjects.append(sid)

    def schedule_cycle_order(self) -> List[str]:
        """
        Round-robin порядок для поточного такту.
        У v0.1 фаза не впливає на порядок — лише на те, ЯКИЙ цикл викликається у суб’єктів.
        """
        if not self._subjects:
            return []
        # классичний RR з обертанням індексу
        order = self._subjects[self._rr_idx:] + self._subjects[:self._rr_idx]
        self._rr_idx = (self._rr_idx + 1) % len(self._subjects)
        return order

    # ----------------- Phase control -----------------

    def phase(self) -> str:
        return self._phase

    def on_cycle_begin(self, kem, kmm) -> None:
        """
        Викликається на початку зовнішнього такту.
        Приймає рішення про вхід у RF з урахуванням cooldown.
        """
        now = monotonic()
        if self._phase == "HB":
            # cooldown перед новою RF
            if (now - self._rf_last_exit_at) >= self.cfg.rf_cooldown:
                if self.should_enter_rf(kem, kmm):
                    self.enter_rf()
        else:  # RF
            # slot guard
            if self._rf_started_at is not None and (now - self._rf_started_at) >= self.cfg.rf_slot_max:
                self.exit_rf()

    def on_cycle_end(self) -> None:
        """
        На кінець такту поки нічого не робимо (залишено під v0.2).
        """
        pass

    def should_enter_rf(self, kem, kmm) -> bool:
        """
        Спрощена логіка тригерів:
        - борг подій у KEM (subject_len) > debt_threshold
        - або оціночна "ентропія" пам’яті KMM > entropy_threshold
        У v0.1 використовуємо метрики, які вже є/можна обчислити грубо.
        """
        try:
            m = kem.metrics()  # kernel_len, subject_len, ...
            subject_len = int(m.get("subject_len", 0))
        except Exception:
            subject_len = 0

        # груба ентропія: чим більше подій / чим менше звернень → тим більша потреба в RF
        # у v0.1 беремо лише довжину subject-черги як проксі
        needs_rf = subject_len >= self.cfg.debt_threshold
        return needs_rf

    def enter_rf(self) -> None:
        if self._phase != "RF":
            self._phase = "RF"
            self._rf_started_at = monotonic()
            log_info("KMS: entering RF phase.")

    def exit_rf(self) -> None:
        if self._phase == "RF":
            self._phase = "HB"
            self._rf_last_exit_at = monotonic()
            self._rf_started_at = None
            log_info("KMS: exiting RF phase -> back to HB.")
