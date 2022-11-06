import enum
from dataclasses import dataclass


class Kind(enum.Enum):
    WORKER = "worker"
    HEAD = "head"


@dataclass
class WorkerBlockDeviceConfig:
    volume_size_in_gb: int = 120
    volume_type: str = "gp3"


def create_provisioner(ns: str,
                       eks_cluster: str,
                       kind: Kind,
                       block_device: WorkerBlockDeviceConfig):
    # envsubst < ~/icloud/ws/cluster_config/eks/ray/cluster/karpenter_head_provisioner-ns.yaml | kubectl apply -f -
    config = get_config(ns, eks_cluster, kind, block_device)
    pass


def delete_provisioner(ns: str,
                       eks_cluster: str,
                       kind: Kind,
                       block_device: WorkerBlockDeviceConfig):
    # envsubst < ~/icloud/ws/cluster_config/eks/ray/cluster/karpenter_head_provisioner-ns.yaml | kubectl delete -f -
    config = get_config(ns, eks_cluster, kind, block_device)
    pass


# TODO: allow volume size to be configurable
# TODO: allow gpu instances
# TODO: allow instance-category to be configurable
# TODO: allow instance-generation to be configurable
# TODO: allow instance-size exclude to be configurable
# TODO: allow instance-size include to be configurable
def get_config(ns: str, eks_cluster: str, kind: Kind, block_device: WorkerBlockDeviceConfig):
    config = [
        {
            "apiVersion": "karpenter.sh/v1alpha5",
            "kind": "Provisioner",
            "metadata": {
                "name": f"blaze-cluster-{ns}-{kind.name}"
            },
            "spec": {
                "labels": {
                    "intent": f"blaze-cluster-{kind.name}-node",
                    "provisioner/type": "karpenter",
                    "provisioner/name": f"blaze-cluster-{ns}-{kind.name}",
                    "blaze-cluster/namespace": ns,
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
                    "name": f"blaze-cluster-{ns}-{kind.name}"
                }
            }
        },
        {
            "apiVersion": "karpenter.k8s.aws/v1alpha1",
            "kind": "AWSNodeTemplate",
            "metadata": {
                "name": f"blaze-cluster-{ns}-{kind.name}"
            },
            "spec": {
                "blockDeviceMappings": [
                    {
                        "deviceName": "/dev/xvda",
                        "ebs": {
                            "volumeSize": f"{block_device.volume_size_in_gb}Gi",
                            "volumeType": block_device.volume_type
                        }
                    }
                ],
                "subnetSelector": {
                    "alpha.eksctl.io/cluster-name": eks_cluster
                },
                "securityGroupSelector": {
                    "alpha.eksctl.io/cluster-name": eks_cluster
                },
                "tags": {
                    "intent": f"blaze-cluster-{kind.name}-node",
                    "provisioner/type": "karpenter",
                    "provisioner/name": f"blaze-cluster-{ns}-{kind.name}",
                    "blaze-cluster/namespace": ns,
                    "blaze-cluster/node-type": kind.name
                }
            }
        }
    ]

    return config
