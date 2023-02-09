from .config import ProvisionerKind, NamespaceConfig
from ..commons.utils import Utils

# TODO: allow gpu instances
# TODO: allow instance-category to be configurable
# TODO: allow instance-generation to be configurable
# TODO: allow instance-size exclude to be configurable
# TODO: allow instance-size include to be configurable
ALLOWED_CAPACITY_TYPES = ["on-demand"]
GPU_INSTANCE_FAMILIES = ["p4d", "p4de", "p3", "p3dn", "p2", "dl1", "trn1", "inf1", "g5", "g5g", "g4dn", "g4ad", "g3", "f1", "vt1"]
ALLOWED_INSTANCE_FAMILIES = ["c6a", "m6a", "r6a", "c5a", "m5a", "r5a"]
# ALLOWED_INSTANCE_GENERATIONS = {"5", "6"}
EXCLUDED_INSTANCE_SIZES = ["nano", "micro", "small"]


# INCLUDED_INSTANCE_SIZES = {}


class ProvisionerManager:
    def __init__(self, namespace_config: NamespaceConfig):
        self.namespace_config = namespace_config

    def create_provisioner(self, kind: ProvisionerKind):
        config = self.get_kubectl_config(kind)
        for c in config:
            Utils.kubectl_apply(c)

    def delete_provisioner(self, kind: ProvisionerKind):
        config = self.get_kubectl_config(kind)
        for c in config:
            Utils.kubectl_delete(c)

    def get_kubectl_config(self, kind: ProvisionerKind):
        allowed_instance_families = ALLOWED_INSTANCE_FAMILIES
        if self.namespace_config.gpu_enabled and kind == ProvisionerKind.WORKER:
            allowed_instance_families = allowed_instance_families + GPU_INSTANCE_FAMILIES

        return [
            {
                "apiVersion": "karpenter.sh/v1alpha5",
                "kind": "Provisioner",
                "metadata": {
                    "name": f"blaze-cluster-{self.namespace_config.name}-{kind.value}"
                },
                "spec": {
                    "labels": {
                        "intent": f"blaze-cluster-{kind.value}-node",
                        "provisioner/type": "karpenter",
                        "provisioner/name": f"blaze-cluster-{self.namespace_config.name}-{kind.value}",
                        "blaze-cluster/namespace": self.namespace_config.name,
                        "blaze-cluster/node-type": kind.value
                    },
                    "requirements": [
                        {
                            "key": "karpenter.sh/capacity-type",
                            "operator": "In",
                            "values": ALLOWED_CAPACITY_TYPES
                        },
                        {
                            "key": "karpenter.k8s.aws/instance-family",
                            "operator": "In",
                            "values": allowed_instance_families
                        },
                        # {
                        #     "key": "karpenter.k8s.aws/instance-category",
                        #     "operator": "In",
                        #     "values": [value for value in ALLOWED_INSTANCE_CATEGORIES]
                        # },
                        # {
                        #     "key": "karpenter.k8s.aws/instance-generation",
                        #     "operator": "In",
                        #     "values": [value for value in ALLOWED_INSTANCE_GENERATIONS]
                        # },
                        {
                            "key": "karpenter.k8s.aws/instance-size",
                            "operator": "NotIn",
                            "values": EXCLUDED_INSTANCE_SIZES

                        }
                    ],
                    "limits": {
                        "resources": {
                            "cpu": 6000,
                            "memory": "20000Gi"
                        }
                    },
                    "ttlSecondsUntilExpired": 2592000,
                    "ttlSecondsAfterEmpty": 20,
                    "providerRef": {
                        "name": f"blaze-cluster-{self.namespace_config.name}-{kind.value}"
                    }
                }
            },
            {
                "apiVersion": "karpenter.k8s.aws/v1alpha1",
                "kind": "AWSNodeTemplate",
                "metadata": {
                    "name": f"blaze-cluster-{self.namespace_config.name}-{kind.value}"
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
                        "intent": f"blaze-cluster-{kind.value}-node",
                        "provisioner/type": "karpenter",
                        "provisioner/name": f"blaze-cluster-{self.namespace_config.name}-{kind.value}",
                        "blaze-cluster/namespace": self.namespace_config.name,
                        "blaze-cluster/node-type": kind.value,

                        # tags enforced by infra team
                        "resource": "compute",
                        "service": "ml_training",
                        "owner": self.namespace_config.name,
                        "role": self.namespace_config.name,
                        "env": "prod",
                        "createdby": self.namespace_config.name,
                        "bu": "josh",
                        "cloud": "aws"
                    }
                }
            }
        ]
