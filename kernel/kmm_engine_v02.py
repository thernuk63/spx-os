from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Optional, Iterable, Tuple, Any
from time import monotonic

from .memory_graph import MemoryGraph
from .memory_nodes import (
    BaseNode, WorkingMemoryNode, EpisodicNode, SemanticNode,
    EmotionalTag, CognitiveContext
)
from .memory_edges import TemporalEdge, CausalEdge, AssociationEdge

@dataclass
class KMMConfigV02:
    wm_capacity: int = 512
    em_capacity: int = 50_000
    decay_half_life_sec: float = 3600.0
    consolidation_batch: int = 16
    min_strength_for_em: float = 0.6
    reinforce_step: float = 0.05
    weaken_step: float = 0.02

class KernelMemoryModelV02:
    """
    KMM v0.2 — Hybrid Memory Fabric
    - Один T-TPG для всіх шарів; WM/EM — це view-фільтри.
    - encode_event() → створює WM-вузли/зв’язки.
    - consolidate() → переносить найсильніше з WM у EM.
    - decay() → зменшує вагу вузлів/ребер за часом.
    - retrieve() → повертає релевантні ланцюжки.
    - bind(), tag(), snapshot() — допоміжні операції.
    """
    def __init__(self, cfg: Optional[KMMConfigV02] = None) -> None:
        self.cfg = cfg or KMMConfigV02()
        self.graph = MemoryGraph()
        self.t0_boot = monotonic()

    @classmethod
    def init(cls, cfg: Optional[Dict[str, Any]] = None) -> "KernelMemoryModelV02":
        return cls(KMMConfigV02(**cfg)) if cfg else cls()

    # === Core API ===
    def encode_event(
        self,
        subject_id: str,
        event_type: str,
        payload: Dict[str, Any],
        salience: float,
        credibility: float,
        t0: Optional[float] = None
    ) -> WorkingMemoryNode:
        """
        Створює/оновлює вузол у WM (WorkingMemoryNode) + тимчасові зв'язки.
        Мінімальна логіка — без повного розбору payload; це skeleton.
        """
        node = WorkingMemoryNode.new(
            subject_id=subject_id,
            kind=event_type,
            payload=payload,
            salience=salience,
            credibility=credibility,
            t0=t0 or monotonic(),
        )
        self.graph.add_node(node)
        # Прив’язка до останнього WM вузла sub'кта — тимчасовий ланцюжок
        prev = self.graph.last_wm_node(subject_id)
        if prev and prev.id != node.id:
            self.graph.add_edge(TemporalEdge.new(prev.id, node.id, weight=0.5))
        self.graph.set_last_wm_node(subject_id, node.id)
        return node

    def consolidate(self, subject_id: Optional[str] = None, limit: Optional[int] = None) -> int:
        """
        Перенесення найсильніших WM-вузлів у EM.
        Спрощена логіка: відбір за salience*credibility >= min_strength_for_em.
        """
        moved = 0
        candidates = self.graph.iter_wm_nodes(subject_id)
        batch = 0
        for n in candidates:
            score = n.salience * n.credibility
            if score >= self.cfg.min_strength_for_em:
                em = EpisodicNode.from_wm(n)
                self.graph.upsert_node(em)
                self.graph.mark_em(n.id, em.id)
                moved += 1
                batch += 1
                if limit and moved >= limit:
                    break
                if batch >= self.cfg.consolidation_batch:
                    batch = 0
        return moved

    def decay(self, now_t0: Optional[float] = None) -> int:
        """
        Зменшує вагу вузлів/ребер за експоненційною моделлю (каркас).
        Поки що — плейсхолдер: слабке ослаблення всіх WM, мінімум EM.
        """
        weakened = 0
        for n in self.graph.iter_all_nodes():
            if isinstance(n, WorkingMemoryNode):
                n.salience = max(0.0, n.salience - self.cfg.weaken_step)
                weakened += 1
        for e in self.graph.iter_all_edges():
            e.weight = max(0.0, e.weight - self.cfg.weaken_step * 0.5)
            # не рахуємо поштучно — метрика не критична
        return weakened

    def retrieve(self, subject_id: str, query: Dict[str, Any], k: int = 5) -> List[BaseNode]:
        """
        Спрощений пошук: фільтр за subject_id та kind у EM, fallback у WM.
        """
        kind = query.get("kind")
        em = [n for n in self.graph.iter_em_nodes(subject_id) if (kind is None or n.kind == kind)]
        if len(em) >= k:
            return em[:k]
        wm = [n for n in self.graph.iter_wm_nodes(subject_id) if (kind is None or n.kind == kind)]
        return (em + wm)[:k]

    def bind(self, a_id: str, b_id: str, rel: str, weight: float = 0.5) -> None:
        if rel == "causal":
            self.graph.add_edge(CausalEdge.new(a_id, b_id, weight))
        else:
            self.graph.add_edge(AssociationEdge.new(a_id, b_id, weight))

    def tag(self, node_id: str, emotion: str, intensity: float = 0.5) -> EmotionalTag:
        tag = EmotionalTag.new(node_id=node_id, emotion=emotion, intensity=intensity)
        self.graph.add_tag(tag)
        return tag

    def snapshot(self) -> Dict[str, Any]:
        return self.graph.export()
