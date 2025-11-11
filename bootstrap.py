from utils.config_loader import load_yaml
from utils.diagnostics import log_info
from kernel.kem import KernelEventMesh
from kernel.kmm import KernelMemoryModel
from kernel.isp import ISP
from kernel.kms import KernelMetaScheduler
from kernel.spm import SubjectProcessManager
from subjects.pid0 import PID0
from subjects.root import RootSubject

def spx_bootstrap():
    log_info("SPX-OS: Loading config...")
    cfg = load_yaml("config/spx_config.yaml")
    isp_rules = load_yaml("config/isp_rules.yaml")

    log_info("SPX-OS: Bootstrapping kernel...")
    kem = KernelEventMesh.init()
    kmm = KernelMemoryModel.init()
    isp = ISP.load(isp_rules)
    kms = KernelMetaScheduler.init(cfg["system"])
    spm = SubjectProcessManager.init()

    log_info("SPX-OS: Spawning PID0...")
    pid0 = spm.spawn(PID0, kem, kmm, isp)
    kms.register(pid0.subject_id)

    log_info("SPX-OS: Spawning Root...")
    root = spm.spawn(RootSubject, kem, kmm, isp)
    kms.register(root.subject_id)

    return {"cfg": cfg, "kem": kem, "kmm": kmm, "isp": isp, "kms": kms, "spm": spm}
