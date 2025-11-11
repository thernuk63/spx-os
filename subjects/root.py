from subjects.base import BaseSubject
from effectors.log_effector import LogEffector
from effectors.state_effector import StateEffector
from effectors.message_effector import MessageEffector

class RootSubject(BaseSubject):
    def __init__(self, kem, kmm, isp):
        super().__init__("Root", kem, kmm, isp)
        self.ae.registry = {
            "LogEffector": LogEffector(),
            "StateEffector": StateEffector(self.state),
            "MessageEffector": MessageEffector(self.kem),
        }
