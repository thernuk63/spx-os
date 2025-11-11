from dataclasses import dataclass

@dataclass
class SubjectMetadata:
    subject_id: str
    t1_multiplier: float
    kind: str  # PID0 / Root / Other
