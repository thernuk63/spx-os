# kernel/kem.py
from collections import deque
from typing import Deque, Optional, Iterable, Callable
from dataclasses import asdict

from spx_types.event import Event, EventChannel
from utils.time_utils import get_T0
from utils.diagnostics import log_info

class KEM:
    """
    Dual-queue Kernel Event Manager:
      - kernel_queue: пріоритет №1 (внутрішні події ядра)
      - subject_queue: пріоритет №2 (події суб'єктів)
    Гарантії:
      - FIFO усередині кожної черги
      - kernel_queue завжди випереджає subject_queue
    """

    def __init__(self) -> None:
        self.kernel_queue: Deque[Event] = deque()
        self.subject_queue: Deque[Event] = deque()
        log_info("KEM: online (Dual-Queue, kernel-first).")

    # ---- Publish API ----
    def publish(self, event: Event) -> None:
        if event.t0 is None:
            event.t0 = get_T0()
        if event.is_kernel():
            self.kernel_queue.append(event)
        else:
            self.subject_queue.append(event)

    def publish_kernel(self, type_: str, payload: dict | None = None) -> None:
        self.publish(Event(
            type=type_,
            payload=payload or {},
            channel=EventChannel.KERNEL
        ))

    def publish_subject(self, type_: str, subject_id: str, payload: dict | None = None) -> None:
        self.publish(Event(
            type=type_,
            subject_id=subject_id,
            payload=payload or {},
            channel=EventChannel.SUBJECT
        ))

    # ---- Consume API ----
    def next_event(self) -> Optional[Event]:
        if self.kernel_queue:
            return self.kernel_queue.popleft()
        if self.subject_queue:
            return self.subject_queue.popleft()
        return None

    def drain(self, limit: int | None = None) -> Iterable[Event]:
        """Знімає події у порядку пріоритетів до limit (або всі)."""
        count = 0
        while True:
            ev = self.next_event()
            if ev is None:
                break
            yield ev
            count += 1
            if limit is not None and count >= limit:
                break

    def drain_for(self, predicate: Callable[[Event], bool], limit: int | None = None) -> list[Event]:
        """
        Вибіркова вибірка подій, що задовольняють predicate.
        Інші події повертаємо назад у свої черги без зміни порядку.
        """
        res: list[Event] = []
        buf_kernel: Deque[Event] = deque()
        buf_subject: Deque[Event] = deque()

        # Переносимо тимчасово всі події в буфери, відфільтровуючи потрібні
        while self.kernel_queue:
            e = self.kernel_queue.popleft()
            if predicate(e) and (limit is None or len(res) < limit):
                res.append(e)
            else:
                buf_kernel.append(e)

        while self.subject_queue:
            e = self.subject_queue.popleft()
            if predicate(e) and (limit is None or len(res) < limit):
                res.append(e)
            else:
                buf_subject.append(e)

        # Повертаємо назад у початковому порядку
        self.kernel_queue.extendleft(reversed(buf_kernel))
        self.subject_queue.extendleft(reversed(buf_subject))
        return res

    # ---- Admin/Diag ----
    def size(self) -> tuple[int, int]:
        return len(self.kernel_queue), len(self.subject_queue)

    def clear(self) -> None:
        self.kernel_queue.clear()
        self.subject_queue.clear()

    def snapshot(self) -> dict:
        def _qdump(q: Deque[Event]) -> list[dict]:
            return [asdict(e) for e in q]
        return {
            "kernel_queue": _qdump(self.kernel_queue),
            "subject_queue": _qdump(self.subject_queue),
        }
