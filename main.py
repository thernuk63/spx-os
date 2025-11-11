from time import sleep
from bootstrap import spx_bootstrap
from utils.diagnostics import log_info

def main():
    ctx = spx_bootstrap()

    kem = ctx["kem"]
    kms = ctx["kms"]
    spm = ctx["spm"]

    log_info("SPX-OS: entering demo loop...")

    for _ in range(6):

        # === 1. Kernel has priority: drain up to N kernel events per cycle ===
        for _ in range(4):  # невелика «квота» на такт
            ev = kem.next_event()
            if not ev:
                break
            # На цьому етапі ми ще не реалізували розподілення.
            # Потім тут буде KernelRouter.
            log_info(f"KEM: dispatched kernel event {ev.id}")

        # === 2. Subject-level scheduling (HB-cycle) ===
        for sid in kms.schedule_cycle_order():
            subj = spm.get(sid)
            if subj:
                subj.hb_cycle()

        sleep(kms.cfg.hb_period)

    log_inf_

