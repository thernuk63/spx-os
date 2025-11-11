from typing import List, Dict, Any

class ISP:
    def __init__(self, rules: List[Dict[str, str]]):
        self.allow = {r["allow"] for r in rules if "allow" in r}
        self.deny  = {r["deny"]  for r in rules if "deny" in r}

    @classmethod
    def load(cls, rules_cfg: Dict[str, Any]) -> "ISP":
        rules = rules_cfg.get("rules", [])
        return cls(rules)

    def is_allowed_effector(self, name: str) -> bool:
        if name in self.deny: return False
        if name in self.allow: return True
        return False   # default deny
