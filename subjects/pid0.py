from subjects.base import BaseSubject
from effectors.log_effector import LogEffector
from utils.diagnostics import log_info

class PID0(BaseSubject):
    def __init__(self, kem, kmm, isp):
        super().__init__("PID0", kem, kmm, isp)
        # register effectors
        self.ae.registry = {"LogEffector": LogEffector()}

    def hb_cycle(self):
        super().hb_cycle()
        self.ae.execute("LogEffector", {"msg": "PID0 integrity check"})
        log_info("PID0: ready to spawn Root when kernel is prepared.")
