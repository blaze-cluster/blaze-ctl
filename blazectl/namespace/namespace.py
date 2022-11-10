from __future__ import annotations

import dataclasses

import dacite

from . import provisioner
from .config import NamespaceConfig
from .fsx_volume import FsxVolumeManager
from .provisioner import ProvisionerManager
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

    def update_provisioner(self):
        # re-create head node provisioner
        self.provisioner_manager.create_provisioner(provisioner.ProvisionerKind.HEAD)

        # re-create worker node provisioner
        self.provisioner_manager.create_provisioner(provisioner.ProvisionerKind.WORKER)

    def config_as_dict(self):
        return dataclasses.asdict(self.namespace_config)

    @staticmethod
    def config_name(ns: str):
        return f"namespace.{ns}"

    def save_config(self):
        Utils.save_config(NamespaceManager.config_name(self.namespace_config.name),
                          self.config_as_dict())

    def soft_delete_config(self):
        self.namespace_config.__deleted__ = True
        self.save_config()

    def delete_config(self):
        Utils.delete_config(NamespaceManager.config_name(self.namespace_config.name), )

    @staticmethod
    def load_config(name: str) -> NamespaceConfig:
        config = Utils.load_config(NamespaceManager.config_name(name))
        return dacite.from_dict(data_class=NamespaceConfig, data=config)

    @staticmethod
    def load(name: str) -> NamespaceManager:
        config = NamespaceManager.load_config(name)
        return NamespaceManager(config)
