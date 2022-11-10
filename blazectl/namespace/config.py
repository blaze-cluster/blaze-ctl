import enum
from dataclasses import dataclass, field
from typing import Optional


class ProvisionerKind(str, enum.Enum):
    WORKER = "worker"
    HEAD = "head"


@dataclass
class WorkerBlockDeviceConfig:
    volume_size_in_gb: int = 120
    volume_type: str = "gp3"


@dataclass
class FsxVolumeConfig:
    volume_name: str
    volume_size_in_gb: int
    volume_handle: str
    volume_dns: str
    volume_mount_name: str


@dataclass
class NamespaceConfig:
    name: str
    eks_cluster: str
    block_device: WorkerBlockDeviceConfig = WorkerBlockDeviceConfig()
    fsx_volumes: list[FsxVolumeConfig] = field(default_factory=list[FsxVolumeConfig])
    sa_policy_arn: Optional[str] = None
    gpu_enabled: bool = False
    __deleted__: bool = False
