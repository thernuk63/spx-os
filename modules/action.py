from typing import Dict, Any
from kernel.isp import ISP

class ActionExecutor:
    def __init__(self, isp: ISP, registry: Dict[str, Any]):
        self.isp = isp
        self.registry = registry  # effector_name -> instance

    def execute(self, effector_name: str, params: Dict[str, Any]) -> bool:
        if not self.isp.is_allowed_effector(effector_name):
            return False
        eff = self.registry.get(effector_name)
        if not eff: return False
        eff.execute(params)
        return True
