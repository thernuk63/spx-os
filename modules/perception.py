from typing import List
from spx_types.event import Event

class PerceptionBus:
    def normalize(self, events: List[Event]) -> List[Event]:
        # v0.1: passthrough
        return events
