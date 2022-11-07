from .config import NamespaceConfig
from ..commons.utils import Utils


class ServiceAccountManager:
    def __init__(self, namespace_config: NamespaceConfig):
        self.namespace_config = namespace_config

    def create_service_account(self):
        command = f'''eksctl create iamserviceaccount \
          --name {self.namespace_config.name}-isra \
          --namespace {self.namespace_config.name} \
          --cluster {self.namespace_config.eks_cluster} \
          --attach-policy-arn {self.namespace_config.sa_policy_arn} \
          --approve'''
        Utils.run_command(command)

    def delete_service_account(self):
        command = f'''eksctl delete iamserviceaccount \
          --name {self.namespace_config.name}-isra \
          --namespace {self.namespace_config.name} \
          --cluster {self.namespace_config.eks_cluster} \
          --approve'''
        Utils.run_command(command)
