from typing import Dict, Any
from spx_types.event import Event, EventType
from utils.time_utils import get_T0

class MessageEffector:
    name = "MessageEffector"
    def __init__(self, kem):
        self.kem = kem

    def execute(self, params: Dict[str, Any]) -> None:
        evt = Event(
            id=params.get("id","msg_evt"),
            type=EventType.SYSTEM,
            payload=params.get("payload",{}),
            origin=params.get("origin","UNKNOWN"),
            salience=params.get("salience",0.1),
            credibility=1.0,
            context=params.get("context",{}),
        )
        self.kem.publish(evt)
