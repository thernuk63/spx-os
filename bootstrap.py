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
    kem = KernelEventMesh.init(dual_queue=True)
    kmm = KernelMemoryModel.init()
    isp = ISP.load(isp_rules)
    kms = KernelMetaScheduler.init(cfg["system"])
    spm = SubjectProcessManager.init()

    kem.publish_kernel_event(Event(
        id="kernel-boot",
        type=EventType.SYSTEM,
        payload={"phase": "init"},
        origin="KERNEL",
        subject_id=None,
        salience=1.0,
        credibility=1.0,
        channel=EventChannel.KERNEL,
        context={}
    ))

    log_info("SPX-OS: Spawning PID0...")
    pid0 = spm.spawn(PID0, kem, kmm, isp, cfg["subjects"].get("PID0", {}))
    kms.register(pid0)

    log_info("SPX-OS: Spawning Root...")
    root = spm.spawn(RootSubject, kem, kmm, isp, cfg["subjects"].get("Root", {}))
    kms.register(root)

    kem.publish_kernel_event(Event(
        id="subjects-init",
        type=EventType.SYSTEM,
        payload={"count": 2},
        origin="KERNEL",
        subject_id=None,
        salience=1.0,
        credibility=1.0,
        channel=EventChannel.KERNEL,
        context={}
    ))

    return {"cfg": cfg, "kem": kem, "kmm": kmm, "isp": isp, "kms": kms, "spm": spm, "pid0": pid0, "root": root}
