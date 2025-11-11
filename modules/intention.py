from typing import List
from spx_types.intention import Intention

class IntentionManager:
    def select(self, intentions: List[Intention]) -> Intention | None:
        if not intentions: return None
        return sorted(intentions, key=lambda x: x.priority, reverse=True)[0]
