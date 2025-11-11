# subjects/root.py
from types.event import Event, EventType, EventChannel
from utils.diagnostics import log_info

class RootSubject:
    def __init__(self, subject_id, kem, kmm, isp, cfg):
        self.subject_id = subject_id
        self.kem = kem
        self.kmm = kmm
        self.isp = isp
        self.cfg = cfg

    def heartbeat_step(self):
        analysis = {"relevance": 0.5, "anomaly": False}
        log_info(f"{self.subject_id}: HB analysis {analysis}")

        self.kem.publish_subject_event(Event(
            id=f"hb-{self.subject_id}",
            type=EventType.SYSTEM,
            payload={"phase": "HB", "analysis": analysis},
            origin=self.subject_id,
            subject_id=self.subject_id,
            salience=0.5,
            credibility=1.0,
            channel=EventChannel.SUBJECT,
            context={}
        ))
