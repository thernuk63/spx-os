from __future__ import annotations
from typing import Dict, Any, Optional

from .kmm_engine_v02 import KernelMemoryModelV02, KMMConfigV02

class KernelMemoryModel:
    """
    Обгортка для поточного інтерфейсу ядра (сумісність).
    """
    def __init__(self, inner: KernelMemoryModelV02) -> None:
        self._inner = inner

    @classmethod
    def init(cls, cfg: Optional[Dict[str, Any]] = None) -> "KernelMemoryModel":
        return cls(KernelMemoryModelV02.init(cfg))

    # Проксі-методи (мінімум, що потрібно ядру прямо зараз):
    def encode_event(self, *a, **kw):
        return self._inner.encode_event(*a, **kw)

    def consolidate(self, *a, **kw):
        return self._inner.consolidate(*a, **kw)

    def decay(self, *a, **kw):
        return self._inner.decay(*a, **kw)

    def retrieve(self, *a, **kw):
        return self._inner.retrieve(*a, **kw)

    def bind(self, *a, **kw):
        return self._inner.bind(*a, **kw)

    def tag(self, *a, **kw):
        return self._inner.tag(*a, **kw)

    def snapshot(self):
        return self._inner.snapshot()
