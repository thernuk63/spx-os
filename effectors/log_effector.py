from typing import Dict, Any
from utils.diagnostics import log_info

class LogEffector:
    name = "LogEffector"

    def execute(self, params: Dict[str, Any]) -> None:
        msg = params.get("msg", "")
        log_info(f"[LogEffector] {msg}")
