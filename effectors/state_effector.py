from typing import Dict, Any

class StateEffector:
    name = "StateEffector"
    def __init__(self, state_ref: Dict[str, Any]):
        self.state_ref = state_ref

    def execute(self, params: Dict[str, Any]) -> None:
        self.state_ref.update(params or {})
