from time import sleep
from bootstrap import spx_bootstrap
from utils.diagnostics import log_info

def main():
    ctx = spx_bootstrap()
    kms = ctx["kms"]
    spm = ctx["spm"]
    # run a short cooperative loop showcasing HB for PID0 and Root
    for _ in range(6):
        for sid in kms.schedule_cycle_order():
            subj = spm.get(sid)
            if subj:
                subj.hb_cycle()
        sleep(kms.cfg.hb_period)
    log_info("SPX-OS: demo loop finished.")

if __name__ == "__main__":
    main()
