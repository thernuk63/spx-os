import pytest
from kernel.kmm_engine_v02 import KernelMemoryModelV02

def test_encode_and_retrieve_minimal():
    kmm = KernelMemoryModelV02.init({})
    n = kmm.encode_event("ROOT", "SystemEvent", {"x": 1}, 0.8, 0.9)
    res = kmm.retrieve("ROOT", {"kind": "SystemEvent"}, k=1)
    assert res and res[0].kind == "SystemEvent"

def test_consolidate_moves_from_wm_to_em():
    kmm = KernelMemoryModelV02.init({"min_strength_for_em": 0.5})
    kmm.encode_event("ROOT", "A", {}, 0.8, 0.8)  # score=0.64
    moved = kmm.consolidate("ROOT")
    assert moved >= 1

def test_decay_weakens_wm():
    kmm = KernelMemoryModelV02.init({})
    n = kmm.encode_event("ROOT", "A", {}, 0.5, 0.5)
    before = n.salience
    kmm.decay()
    after = kmm.retrieve("ROOT", {"kind": "A"}, k=1)[0].salience
    assert after <= before
