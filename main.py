from time import sleep
from bootstrap import spx_bootstrap
from utils.diagnostics import log_info

def main():
    ctx = spx_bootstrap()
    kem, kms, spm = ctx["kem"], ctx["kms"], ctx["spm"]

    log_info("SPX-OS: entering demo loop...")

    for _ in range(12):
        # 0) рішення по фазі
        kms.on_cycle_begin(kem, ctx["kmm"])

        # 1) ядро має пріоритет
        for _ in range(4):
            ev = kem.next_event()
            if not ev:
                break
            log_info(f"KEM: dispatched kernel event {ev.id}")

        # 2) планування суб’єктів відповідно до фази
        if kms.phase() == "HB":
            for sid in kms.schedule_cycle_order():
                subj = spm.get(sid)
                if subj:
                    subj.hb_cycle()
        else:  # RF
            # у v0.1 робимо простий RF-прохід: виклик rf_cycle() якщо є,
            # інакше — HB як заглушка.
            for sid in kms.schedule_cycle_order():
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
