from collections import deque
from typing import Deque, List, Optional
from spx_types.event import Event
from utils.diagnostics import log_info

class KernelEventMesh:
    def __init__(self) -> None:
        self._q: Deque[Event] = deque()

    @classmethod
    def init(cls) -> "KernelEventMesh":
        kem = cls()
        log_info("KEM: online (FIFO with T0 timestamping).")
        return kem

    def publish(self, event: Event) -> None:
        self._q.append(event)

    def fetch_for(self, subject_id: str, max_items: int = 32) -> List[Event]:
        # v0.1: broadcast FIFO; subject filters are applied at consumer side if needed
        out: List[Event] = []
        while self._q and len(out) < max_items:
            out.append(self._q.popleft())
        return out
