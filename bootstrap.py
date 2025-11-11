from utils.config_loader import load_yaml
from utils.diagnostics import log_info
from kernel.kem import KernelEventMesh
from kernel.kmm import KernelMemoryModel
from kernel.isp import ISP
from kernel.kms import KernelMetaScheduler
from kernel.spm import SubjectProcessManager
from subjects.pid0 import PID0
from subjects.root import RootSubject
from types.event import Event, EventType, EventChannel


def spx_bootstrap():
    log_info("SPX-OS: Loading config...")
    cfg = load_yaml("config/spx_config.yaml")
    isp_rules = load_yaml("config/isp_rules.yaml")

    log_info("SPX-OS: Bootstrapping kernel...")

    # Dual queue KEM
    kem = KernelEventMesh.init(dual_queue=True)

    # Single T-TPG memory (WM/EM views)
    kmm = KernelMemoryModel.init()

    # Intention Safety
    isp = ISP.load(isp_rules)

    # Scheduler
    kms = KernelMetaScheduler.init(cfg["system"])

    # Subject Process Manager
    spm = SubjectProcessManager.init()

    # --- Spawn PID0 ---
    log_info("SPX-OS: Spawning PID0...")
    pid0 = spm.spawn(PID0, kem, kmm, isp, cfg["subjects"]["PID0"])
    kms.register(pid0)

    # KERNEL EVENT: subject spawned
    kem.publish(Event(
        id="ev_spawn_pid0",
        type=EventType.SYSTEM,
        payload={"event": "SUBJECT_SPAWNED", "subject_id": pid0.subject_id},
        origin="KERNEL",
        subject_id=None,
        salience=1.0,
        credibility=1.0,
        channel=EventChannel.KERNEL,
        context={}
    ))

    # --- Spawn Root ---
    log_info("SPX-OS: Spawning Root...")
    root = spm.spawn(RootSubject, kem, kmm, isp, cfg["subjects"]["Root"])
    kms.register(root)

    kem.publish(Event(
        id="ev_spawn_root",
        type=EventType.SYSTEM,
        payload={"event": "SUBJECT_SPAWNED", "subject_id": root.subject_id},
        origin="KERNEL",
        subject_id=None,
        salience=1.0,
        credibility=1.0,
        channel=EventChannel.KERNEL,
        context={}
    ))

    return {
        "cfg": cfg,
        "kem": kem,
        "kmm": kmm,
        "isp": isp,
        "kms": kms,
        "spm": spm,
        "pid0": pid0,
        "root": root,
    }
