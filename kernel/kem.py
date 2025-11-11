# kernel/kem.py
"""
Kernel Event Mesh (KEM) — SPX-OS v0.2
Dual-Queue Event Manager with kernel-first priority + quotas + backpressure.
"""

from __future__ import annotations
from collections import deque
from typing import Optional, Dict, List, Callable, Deque, Tuple
from spx_types.event import Event, EventChannel


class KernelEventMesh:
    """
    Dual-queue event manager.
    Guarantees:
      - FIFO per channel
      - kernel-first on consumption
      - configurable capacities and backpressure policy

    Backpressure policy:
      - "drop_oldest": if full, drop popleft() before append()
      - "reject": if full, raise RuntimeError
    """

    def __init__(self):
        self.kernel_queue: Deque[Event] = deque()
        self.subject_queue: Deque[Event] = deque()
        # defaults (safe for MVP)
        self.kernel_max: int = 1024
        self.subject_max: int = 4096
        self.policy: str = "drop_oldest"  # or "reject"

        # simple counters
        self.dropped_kernel: int = 0
        self.dropped_subject: int = 0
        self.rejected_kernel: int = 0
        self.rejected_subject: int = 0

    @classmethod
    def init(cls, dual_queue: bool = True) -> "KernelEventMesh":
        return cls()

    # ----------------------------------------------------------------------
    # CONFIG
    # ----------------------------------------------------------------------
    def configure(self, *, kernel_max: Optional[int] = None, subject_max: Optional[int] = None,
                  policy: Optional[str] = None) -> None:
        if kernel_max is not None and kernel_max > 0:
            self.kernel_max = kernel_max
        if subject_max is not None and subject_max > 0:
            self.subject_max = subject_max
        if policy is not None:
            if policy not in ("drop_oldest", "reject"):
                raise ValueError("Invalid KEM policy")
            self.policy = policy

    # ----------------------------------------------------------------------
    # PUBLISH
    # ----------------------------------------------------------------------
    def _append_with_policy(self, q: Deque[Event], ev: Event, limit: int, counters: Tuple[str, str]) -> None:
        full = len(q) >= limit
        if not full:
            q.append(ev)
            return
        # backpressure
        if self.policy == "drop_oldest":
            q.popleft()
            q.append(ev)
            # bump drop counter
            if counters[0] == "kernel":
                self.dropped_kernel += 1
            else:
                self.dropped_subject += 1
        else:  # reject
            if counters[0] == "kernel":
                self.rejected_kernel += 1
            else:
                self.rejected_subject += 1
            raise RuntimeError(f"KEM queue full ({counters[0]})")

    def publish(self, event: Event) -> None:
        """Route by event.channel."""
        if event.channel == EventChannel.KERNEL:
            self._append_with_policy(self.kernel_queue, event, self.kernel_max, ("kernel", "kernel"))
        else:
            self._append_with_policy(self.subject_queue, event, self.subject_max, ("subject", "subject"))

    def publish_kernel_event(self, event: Event) -> None:
        object.__setattr__(event, "channel", EventChannel.KERNEL)
        self.publish(event)

    def publish_subject_event(self, event: Event) -> None:
        object.__setattr__(event, "channel", EventChannel.SUBJECT)
        self.publish(event)

    # ----------------------------------------------------------------------
    # CONSUME
    # ----------------------------------------------------------------------
    def next_event(self) -> Optional[Event]:
        if self.kernel_queue:
            return self.kernel_queue.popleft()
        if self.subject_queue:
            return self.subject_queue.popleft()
        return None

    def drain_kernel(self) -> List[Event]:
        items = list(self.kernel_queue)
        self.kernel_queue.clear()
        return items

    def drain_subject(self) -> List[Event]:
        items = list(self.subject_queue)
        self.subject_queue.clear()
        return items

    def drain_all(self) -> Dict[str, List[Event]]:
        return {"kernel": self.drain_kernel(), "subject": self.drain_subject()}

    def peek_kernel(self) -> Optional[Event]:
        return self.kernel_queue[0] if self.kernel_queue else None

    def peek_subject(self) -> Optional[Event]:
        return self.subject_queue[0] if self.subject_queue else None

    def drain_for(self, predicate: Callable[[Event], bool], limit: Optional[int] = None) -> List[Event]:
        """
        Selectively drain events that match predicate, preserving order of the rest.
        """
        res: List[Event] = []
        buf_kernel: Deque[Event] = deque()
        buf_subject: Deque[Event] = deque()

        # kernel
        while self.kernel_queue:
            e = self.kernel_queue.popleft()
            if predicate(e) and (limit is None or len(res) < limit):
                res.append(e)
            else:
                buf_kernel.append(e)

        # subject
        while self.subject_queue:
            e = self.subject_queue.popleft()
            if predicate(e) and (limit is None or len(res) < limit):
                res.append(e)
            else:
                buf_subject.append(e)

        # restore
        self.kernel_queue.extendleft(reversed(buf_kernel))
        self.subject_queue.extendleft(reversed(buf_subject))
        return res

    # ----------------------------------------------------------------------
    # DIAGNOSTICS
    # ----------------------------------------------------------------------
    def count(self) -> Dict[str, int]:
        return {"kernel": len(self.kernel_queue), "subject": len(self.subject_queue)}

    def empty(self) -> bool:
        return not self.kernel_queue and not self.subject_queue

    def metrics(self) -> Dict[str, int]:
        return {
            "kernel_len": len(self.kernel_queue),
            "subject_len": len(self.subject_queue),
            "kernel_max": self.kernel_max,
            "subject_max": self.subject_max,
            "dropped_kernel": self.dropped_kernel,
            "dropped_subject": self.dropped_subject,
            "rejected_kernel": self.rejected_kernel,
            "rejected_subject": self.rejected_subject,
        }

    def debug_snapshot(self) -> Dict[str, List[str]]:
        return {
            "kernel_queue": [ev.id for ev in self.kernel_queue],
            "subject_queue": [ev.id for ev in self.subject_queue],
        }
