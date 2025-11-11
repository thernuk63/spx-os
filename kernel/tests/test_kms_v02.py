from kernel.kms import KernelMetaScheduler
from kernel.kem import KernelEventMesh
from spx_types.event import Event, EventType

def _fill_subject(kem, sid: str, n: int):
    for i in range(n):
        kem.publish(Event.subject(sid, EventType.SYSTEM, {"i": i}))

def test_rf_trigger_and_order():
    kem = KernelEventMesh.init()
    kms = KernelMetaScheduler.init({
        "hb_period": 0.01,
        "scheduler": {
            "rf_trigger_debt": 2,
            "rf_max_cycles": 1,
            "kernel_overload_threshold": 999,
            "fairness_decay": 0.9
        }
    })

    kms.register("PID0")
    kms.register("ROOT")

    # debt для ROOT = 2 → має піти у RF
    _fill_subject(kem, "ROOT", 2)

    assert kms.phase() == "HB"
    kms.on_cycle_begin(kem, None)
    assert kms.phase() == "RF"

    order = kms.schedule_cycle_order()
    assert order[0] == "PID0" and order[1] == "ROOT"  # PID0 має пріоритет у RF

def test_kernel_overload_triggers_rf():
    kem = KernelEventMesh.init()
    kms = KernelMetaScheduler.init({
        "hb_period": 0.01,
        "scheduler": {"rf_trigger_debt": 999, "rf_max_cycles": 1, "kernel_overload_threshold": 2}
    })
    kms.register("PID0")
    kms.register("ROOT")

    kem.publish(Event.kernel(EventType.SYSTEM, {"k": 1}))
    kem.publish(Event.kernel(EventType.SYSTEM, {"k": 2}))

    kms.on_cycle_begin(kem, None)
    assert kms.phase() == "RF"
