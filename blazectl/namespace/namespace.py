from . import provisioner
from .config import NamespaceConfig
from .provisioner import ProvisionerManager
from .fsx_volume import FsxVolumeManager
from .service_account import ServiceAccountManager
from ..commons.utils import Utils


class NamespaceManager:
    def __init__(self, namespace_config: NamespaceConfig):
        self.namespace_config = namespace_config
        self.provisioner_manager = ProvisionerManager(self.namespace_config)
        self.fsx_volume_manager = FsxVolumeManager(self.namespace_config)
        self.service_account_manager = ServiceAccountManager(self.namespace_config)

    def create_ns(self):
        command = f"kubectl create namespace {self.namespace_config.name}"
        Utils.run_command(command)

        # create head node provisioner
        self.provisioner_manager.create_provisioner(provisioner.ProvisionerKind.HEAD)

        # create worker node provisioner
        self.provisioner_manager.create_provisioner(provisioner.ProvisionerKind.WORKER)

        # create persistent volumes
        for fsx in self.namespace_config.fsx_volumes:
            self.fsx_volume_manager.create_fsx_volume(fsx)

        # create service accounts
        if self.namespace_config.sa_policy_arn is not None:
            self.service_account_manager.create_service_account()

    def delete_ns(self):
        # delete service accounts
        if self.namespace_config.sa_policy_arn is not None:
            self.service_account_manager.delete_service_account()

        # delete persistent volumes
        for fsx in self.namespace_config.fsx_volumes:
            self.fsx_volume_manager.delete_fsx_volume(fsx)

        provisioner_manager = ProvisionerManager(self.namespace_config)

        # delete head node provisioner
        provisioner_manager.delete_provisioner(provisioner.ProvisionerKind.HEAD)

        # delete worker node provisioner
        provisioner_manager.delete_provisioner(provisioner.ProvisionerKind.WORKER)

        command = f"kubectl delete namespace {self.namespace_config.name}"
        Utils.run_command(command)
