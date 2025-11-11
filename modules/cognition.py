from typing import List, Dict, Any
from spx_types.state import StateSnapshot
from spx_types.event import Event

class CognitionCore:
    def analyze(self, events: List[Event]) -> Dict[str, Any]:
        # v0.1: trivial analysis
        return {"relevance": 0.5, "anomaly": False}

    def build_snapshot(self, events: List[Event]) -> StateSnapshot:
        return StateSnapshot(
            id="ss_1", scene_id="scene", entities=[], relations=[],
            recency=1.0, salience_map={}, origin="subject"
        )
