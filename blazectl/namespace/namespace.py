from dataclasses import dataclass, field

from . import provisioner
from .provisioner import WorkerBlockDeviceConfig, create_provisioner, delete_provisioner
from .fsx_volume import FsxVolumeConfig, create_fsx_volume, delete_fsx_volume
from .service_account import delete_service_account, create_service_account


@dataclass
class NamespaceConfig:
    name: str
    eks_cluster: str
    block_device: WorkerBlockDeviceConfig = WorkerBlockDeviceConfig()
    fsx_volumes: list[FsxVolumeConfig] = field(default_factory=list[FsxVolumeConfig])
    sa_policy_arn: str = None


def create_ns(config: NamespaceConfig):
    # kubectl create namespace ${RAY_CLUSTER_NS}

    # create head node provisioner
    create_provisioner(config.name, config.eks_cluster, provisioner.Kind.HEAD, config.block_device)

    # create worker node provisioner
    create_provisioner(config.name, config.eks_cluster, provisioner.Kind.WORKER, config.block_device)

    # create persistent volumes
    for fsx in config.fsx_volumes:
        create_fsx_volume(config.name, fsx)

    # create service accounts
    if config.sa_policy_arn is not None:
        create_service_account(config.name, config.eks_cluster, config.sa_policy_arn)

    pass


def delete_ns(config: NamespaceConfig):
    # delete service accounts
    if config.sa_policy_arn is not None:
        delete_service_account(config.name, config.eks_cluster)

    # delete persistent volumes
    for fsx in config.fsx_volumes:
        delete_fsx_volume(config.name, fsx)

    # delete worker node provisioner
    delete_provisioner(config.name, config.eks_cluster, provisioner.Kind.WORKER)

    # delete head node provisioner
    delete_provisioner(config.name, config.eks_cluster, provisioner.Kind.HEAD)

    # kubectl delete namespace ${RAY_CLUSTER_NS}

    pass
