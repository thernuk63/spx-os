from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Iterable, Any, Tuple

from .memory_nodes import BaseNode, WorkingMemoryNode, EpisodicNode, SemanticNode
from .memory_edges import BaseEdge

@dataclass
class _SubjectIndex:
    last_wm_node_id: Optional[str] = None

class MemoryGraph:
    """
    Єдиний граф пам’яті (T-TPG). WM/EM — це view.
    """
    def __init__(self) -> None:
        self.nodes: Dict[str, BaseNode] = {}
        self.edges: Dict[str, BaseEdge] = {}
        self.subject_idx: Dict[str, _SubjectIndex] = {}
        self.em_links: Dict[str, str] = {}  # wm_id -> em_id

    # --- Nodes ---
    def add_node(self, node: BaseNode) -> None:
        self.nodes[node.id] = node

    def upsert_node(self, node: BaseNode) -> None:
        self.nodes[node.id] = node

    def get_node(self, node_id: str) -> Optional[BaseNode]:
        return self.nodes.get(node_id)

    def iter_all_nodes(self) -> Iterable[BaseNode]:
        return self.nodes.values()

    def iter_wm_nodes(self, subject_id: Optional[str] = None) -> Iterable[WorkingMemoryNode]:
        for n in self.nodes.values():
            if isinstance(n, WorkingMemoryNode) and (subject_id is None or n.subject_id == subject_id):
                yield n

    def iter_em_nodes(self, subject_id: Optional[str] = None) -> Iterable[EpisodicNode]:
        for n in self.nodes.values():
            if isinstance(n, EpisodicNode) and (subject_id is None or n.subject_id == subject_id):
                yield n

    # --- Edges ---
    def add_edge(self, edge: BaseEdge) -> None:
        self.edges[edge.id] = edge

    def iter_all_edges(self) -> Iterable[BaseEdge]:
        return self.edges.values()

    # --- Subject index ---
    def _idx(self, subject_id: str) -> _SubjectIndex:
        if subject_id not in self.subject_idx:
            self.subject_idx[subject_id] = _SubjectIndex()
        return self.subject_idx[subject_id]

    def set_last_wm_node(self, subject_id: str, node_id: str) -> None:
        self._idx(subject_id).last_wm_node_id = node_id

    def last_wm_node(self, subject_id: str) -> Optional[WorkingMemoryNode]:
        nid = self._idx(subject_id).last_wm_node_id
        if not nid:
            return None
        n = self.get_node(nid)
        return n if isinstance(n, WorkingMemoryNode) else None

    # --- WM→EM mapping ---
    def mark_em(self, wm_id: str, em_id: str) -> None:
        self.em_links[wm_id] = em_id

    # --- Export (snapshot) ---
    def export(self) -> Dict[str, Any]:
        return {
            "nodes": [n.as_dict() for n in self.nodes.values()],
            "edges": [e.as_dict() for e in self.edges.values()],
            "em_links": dict(self.em_links),
        }
