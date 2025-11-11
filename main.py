from time import sleep
from bootstrap import spx_bootstrap
from utils.diagnostics import log_info
from spx_types.event import Event, EventType

def main():
    ctx = spx_bootstrap()
    kem, kms, spm = ctx["kem"], ctx["kms"], ctx["spm"]
    log_info("SPX-OS: entering demo loop...")

    for i in range(5):
        ctx["kem"].publish(Event.subject(
            subject_id="ROOT",
            type_=EventType.SYSTEM,
            payload={"n": i},
            salience=0.5,
            credibility=1.0
        ))

    for _ in range(18):
        kms.on_cycle_begin(kem, ctx["kmm"])

        # ядро: дренаж кількох kernel-подій кожен такт
        for _ in range(2):
            ev = kem.next_event()
            if not ev:
                break
            log_info(f"KEM: dispatched kernel event {ev.id}")

        order = kms.schedule_cycle_order()
        if kms.phase() == "HB":
            for sid in order:
                subj = spm.get(sid)
                if subj:
                    subj.hb_cycle()
                    kms.notify_hb_processed(subj.subject_id)
        else:
            for sid in order:
                subj = spm.get(sid)
                if subj:
                    if hasattr(subj, "rf_cycle"):
                        subj.rf_cycle()
                    else:
                        subj.hb_cycle()

        kms.on_cycle_end()
        sleep(kms.cfg.hb_period)

    log_info("SPX-OS: demo loop finished.")

if __name__ == "__main__":
    main()
