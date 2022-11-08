import dataclasses
from typing import Dict

from .config import ProvisionerKind, NamespaceConfig
from ..commons.utils import Utils


class ProvisionerManager:
    def __init__(self, namespace_config: NamespaceConfig):
        self.namespace_config = namespace_config

    def create_provisioner(self, kind: ProvisionerKind):
        config = self.get_kubectl_config(kind)
        Utils.kubectl_apply(config)

    def delete_provisioner(self, kind: ProvisionerKind):
        config = self.get_kubectl_config(kind)
        Utils.kubectl_delete(config)

    # TODO: allow volume size to be configurable
    # TODO: allow gpu instances
    # TODO: allow instance-category to be configurable
    # TODO: allow instance-generation to be configurable
    # TODO: allow instance-size exclude to be configurable
    # TODO: allow instance-size include to be configurable
    def get_kubectl_config(self, kind: ProvisionerKind):
        return [
            {
                "apiVersion": "karpenter.sh/v1alpha5",
                "kind": "Provisioner",
                "metadata": {
                    "name": f"blaze-cluster-{self.namespace_config.name}-{kind.name}"
                },
                "spec": {
                    "labels": {
                        "intent": f"blaze-cluster-{kind.name}-node",
                        "provisioner/type": "karpenter",
                        "provisioner/name": f"blaze-cluster-{self.namespace_config.name}-{kind.name}",
                        "blaze-cluster/namespace": self.namespace_config.name,
                        "blaze-cluster/node-type": kind.name
                    },
                    "requirements": [
                        {
                            "key": "karpenter.sh/capacity-type",
                            "operator": "In",
                            "values": [
                                "on-demand"
                            ]
                        },
                        {
                            "key": "karpenter.k8s.aws/instance-category",
                            "operator": "In",
                            "values": [
                                "c",
                                "m",
                                "r"
                            ]
                        },
                        {
                            "key": "karpenter.k8s.aws/instance-generation",
                            "operator": "In",
                            "values": [
                                "5",
                                "6"
                            ]
                        },
                        {
                            "key": "karpenter.k8s.aws/instance-size",
                            "operator": "NotIn",
                            "values": [
                                "nano",
                                "micro",
                                "small"
                            ]
                        }
                    ],
                    "limits": {
                        "resources": {
                            "cpu": 3000,
                            "memory": "10000Gi"
                        }
                    },
                    "ttlSecondsUntilExpired": 2592000,
                    "ttlSecondsAfterEmpty": 20,
                    "providerRef": {
                        "name": f"blaze-cluster-{self.namespace_config.name}-{kind.name}"
                    }
                }
            },
            {
                "apiVersion": "karpenter.k8s.aws/v1alpha1",
                "kind": "AWSNodeTemplate",
                "metadata": {
                    "name": f"blaze-cluster-{self.namespace_config.name}-{kind.name}"
                },
                "spec": {
                    "blockDeviceMappings": [
                        {
                            "deviceName": "/dev/xvda",
                            "ebs": {
                                "volumeSize": f"{self.namespace_config.block_device.volume_size_in_gb}Gi",
                                "volumeType": self.namespace_config.block_device.volume_type
                            }
                        }
                    ],
                    "subnetSelector": {
                        "alpha.eksctl.io/cluster-name": self.namespace_config.eks_cluster
                    },
                    "securityGroupSelector": {
                        "alpha.eksctl.io/cluster-name": self.namespace_config.eks_cluster
                    },
                    "tags": {
                        "intent": f"blaze-cluster-{kind.name}-node",
                        "provisioner/type": "karpenter",
                        "provisioner/name": f"blaze-cluster-{self.namespace_config.name}-{kind.name}",
                        "blaze-cluster/namespace": self.namespace_config.name,
                        "blaze-cluster/node-type": kind.name
                    }
                }
            }
        ]
