from kernel.kms import KernelMetaScheduler
from kernel.kem import KernelEventMesh
from spx_types.event import Event, EventType

def test_kms_enters_rf_when_subject_queue_high():
    kem = KernelEventMesh.init()
    kms = KernelMetaScheduler.init({
        "hb_period": 0.01, "rf_slot_max": 0.1, "rf_cooldown": 0.0,
        "rf_triggers": {"debt_threshold": 2, "entropy_threshold": 0.5}
    })

    # наповнюємо subject-чергу
    kem.publish(Event.subject("ROOT", EventType.SYSTEM, {"i": 1}))
    kem.publish(Event.subject("ROOT", EventType.SYSTEM, {"i": 2}))

    assert kms.phase() == "HB"
    kms.on_cycle_begin(kem, None)
    assert kms.phase() == "RF"
