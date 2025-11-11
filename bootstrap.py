from utils.config_loader import load_yaml
from utils.diagnostics import log_info

from kernel.kem import KernelEventMesh
from kernel.kmm import KernelMemoryModel
from kernel.isp import ISP
from kernel.kms import KernelMetaScheduler
from kernel.spm import SubjectProcessManager

from subjects.pid0 import PID0
from subjects.root import RootSubject

from spx_types.event import Event, EventType


def spx_bootstrap():
    log_info("SPX-OS: Loading config...")
    cfg = load_yaml("config/spx_config.yaml")
    isp_rules = load_yaml("config/isp_rules.yaml")

    # ---------------------------------------------------------
    # Kernel boot
    # ---------------------------------------------------------
    log_info("SPX-OS: Bootstrapping kernel...")

    kem = KernelEventMesh.init(dual_queue=True)
    kmm = KernelMemoryModel.init()
    isp = ISP.load(isp_rules)
    kms = KernelMetaScheduler.init(cfg["system"])
    spm = SubjectProcessManager.init()

    # Apply KEM config (quotas, policies)
    kem_cfg = cfg.get("kem", {})
    kem.configure(
        kernel_max=kem_cfg.get("kernel_max"),
        subject_max=kem_cfg.get("subject_max"),
        policy=kem_cfg.get("policy"),
    )

    # kernel boot event
    kem.publish(Event.kernel(
        EventType.SYSTEM,
        {"phase": "kernel_init"}
    ))

    # ---------------------------------------------------------
    # Spawn subjects
    # ---------------------------------------------------------
    log_info("SPX-OS: Spawning PID0...")
    pid0 = spm.spawn(
        PID0, kem, kmm, isp,
        cfg["subjects"].get("PID0", {})
    )
    kms.register(pid0)

    log_info("SPX-OS: Spawning Root...")
    root = spm.spawn(
        RootSubject, kem, kmm, isp,
        cfg["subjects"].get("Root", {})
    )
    kms.register(root)

    kem.publish(Event.kernel(
        EventType.SYSTEM,
        {"phase": "subjects_initialized", "count": 2}
    ))

    # ---------------------------------------------------------
    # Return context
    # ---------------------------------------------------------
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
