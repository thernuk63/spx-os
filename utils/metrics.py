def compute_cognitive_debt(pending_consolidations: int, threshold: int) -> float:
    if threshold <= 0: return 0.0
    return pending_consolidations / float(threshold)

def compute_memory_entropy(recent_access_count: int, total_nodes: int) -> float:
    denom = max(total_nodes, 1)
    ratio = min(max(recent_access_count / float(denom), 0.0), 1.0)
    return 1.0 - ratio

def compute_salience(priority: float, relevance: float) -> float:
    return max(0.0, min(1.0, priority * relevance))
