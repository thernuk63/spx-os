import networkx as nx
from typing import Any, Dict, List, Tuple
from utils.diagnostics import log_info

class KernelMemoryModel:
    def __init__(self) -> None:
        self.graph = nx.DiGraph()
        self.pending_consolidations = 0

    @classmethod
    def init(cls) -> "KernelMemoryModel":
        kmm = cls()
        log_info("KMM: initialized (WM+EM views on single T-TPG).")
        return kmm

    # Simplified operations
    def encode_wm(self, node_id: str, payload: Dict[str, Any]) -> None:
        self.graph.add_node(node_id, **payload, scope="WM")

    def encode_em(self, node_id: str, payload: Dict[str, Any]) -> None:
        self.graph.add_node(node_id, **payload, scope="EM")

    def bind(self, src: str, dst: str, rel_type: str) -> None:
        self.graph.add_edge(src, dst, rel_type=rel_type)

    def wm_load(self) -> int:
        return sum(1 for _, data in self.graph.nodes(data=True) if data.get("scope") == "WM")

    def total_nodes(self) -> int:
        return self.graph.number_of_nodes()
