"""
Kernel Event Mesh (KEM) — SPX-OS v0.2
Dual-Queue Event Manager with kernel-first priority.

This module implements the event routing layer of SPX-OS.
KEM guarantees:
- strict FIFO per queue
- kernel queue always has priority
- event channel separation (KERNEL vs SUBJECT)
- minimal diagnostics and snapshot API
"""

from collections import deque
from typing import Optional, Dict, List
from spx_types.event import Event, EventChannel


class KernelEventMesh:
    """
    Dual-queue event manager.
    Kernel events have strict priority over subject events.

    Public API:
    - publish(event)
    - publish_kernel_event(event)
    - publish_subject_event(event)
    - next_event()
    - drain_kernel()
    - drain_subject()
    - drain_all()
    - count()
    - empty()
    - debug_snapshot()
    """

    def __init__(self):
        # Two independent FIFO queues
        self.kernel_queue: deque[Event] = deque()
        self.subject_queue: deque[Event] = deque()

    @classmethod
    def init(cls, dual_queue: bool = True):
        """
        Static initializer used by bootstrap.
        In v0.2 dual_queue is always True — placeholder for future modes.
        """
        return cls()

    # ----------------------------------------------------------------------
    # PUBLISH METHODS
    # ----------------------------------------------------------------------

    def publish(self, event: Event) -> None:
        """
        General publish method.
        Routes event into appropriate queue based on event.channel.
        """
        if event.channel == EventChannel.KERNEL:
            self.kernel_queue.append(event)
        else:
            self.subject_queue.append(event)

    def publish_kernel_event(self, event: Event) -> None:
        """
        Shortcut for kernel-originated events.
        Ensures channel correctness.
        """
        object.__setattr__(event, "channel", EventChannel.KERNEL)
        self.kernel_queue.append(event)

    def publish_subject_event(self, event: Event) -> None:
        """
        Shortcut for subject-originated events.
        """
        object.__setattr__(event, "channel", EventChannel.SUBJECT)
        self.subject_queue.append(event)

    # ----------------------------------------------------------------------
    # EVENT CONSUMPTION
    # ----------------------------------------------------------------------

    def next_event(self) -> Optional[Event]:
        """
        Returns next event in priority order:
        1. kernel queue
        2. subject queue
        Returns None if both queues empty.
        """
        if self.kernel_queue:
            return self.kernel_queue.popleft()
        if self.subject_queue:
            return self.subject_queue.popleft()
        return None

    def drain_kernel(self) -> List[Event]:
        """
        Returns all kernel events in FIFO order and clears kernel queue.
        """
        items = list(self.kernel_queue)
        self.kernel_queue.clear()
        return items

    def drain_subject(self) -> List[Event]:
        """
        Returns all subject events in FIFO order and clears subject queue.
        """
        items = list(self.subject_queue)
        self.subject_queue.clear()
        return items

    def drain_all(self) -> Dict[str, List[Event]]:
        """
        Drain both queues and return dictionary:
        {
            "kernel": [...],
            "subject": [...]
        }
        """
        return {
            "kernel": self.drain_kernel(),
            "subject": self.drain_subject()
        }

    # ----------------------------------------------------------------------
    # DIAGNOSTICS
    # ----------------------------------------------------------------------

    def count(self) -> Dict[str, int]:
        """
        Returns count of queued events.
        Useful for scheduler & monitoring.
        """
        return {
            "kernel": len(self.kernel_queue),
            "subject": len(self.subject_queue)
        }

    def empty(self) -> bool:
        """
        Returns True if both queues are empty.
        """
        return not self.kernel_queue and not self.subject_queue

    def debug_snapshot(self) -> Dict[str, List[str]]:
        """
        Returns lightweight snapshot for diagnostics.
        Contains only event IDs.
        """
        return {
            "kernel_queue": [ev.id for ev in self.kernel_queue],
            "subject_queue": [ev.id for ev in self.subject_queue],
        }
