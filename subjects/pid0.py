# subjects/pid0.py
from spx_types.event import Event, EventType, EventChannel
from utils.diagnostics import log_info

class PID0:
    subject_id = "PID0"

    def __init__(self, subject_id, kem, kmm, isp, cfg):
        self.subject_id = subject_id
        self.kem = kem
        self.kmm = kmm
        self.isp = isp
        self.cfg = cfg

    def hb_cycle(self):
        log_info(f"{self.subject_id}: HB-cycle")

    def rf_cycle(self):
        log_info(f"{self.subject_id}: RF-cycle (noop)")
