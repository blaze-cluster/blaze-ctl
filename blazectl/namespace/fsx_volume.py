from dataclasses import dataclass


@dataclass
class FsxVolumeConfig:
    volume_name: str
    volume_size_in_gb: int
    volume_handle: str
    volume_dns: str
    volume_mount_name: str


def create_fsx_volume(ns: str, config: FsxVolumeConfig):
    # envsubst < ~/icloud/ws/cluster_config/eks/ray/cluster/karpenter_head_provisioner-ns.yaml | kubectl apply -f -
    config = get_config(ns, config)


def delete_fsx_volume(ns: str, config: FsxVolumeConfig):
    # envsubst < ~/icloud/ws/cluster_config/eks/ray/cluster/karpenter_head_provisioner-ns.yaml | kubectl delete -f -
    config = get_config(ns, config)


def get_config(ns: str, config: FsxVolumeConfig):
    config = [
        {
            "apiVersion": "v1",
            "kind": "PersistentVolume",
            "metadata": {
                "name": f"{ns}-{config.volume_name}-fsx-pv"
            },
            "spec": {
                "capacity": {
                    "storage": f"{config.volume_size_in_gb}Gi"
                },
                "volumeMode": "Filesystem",
                "accessModes": [
                    "ReadWriteMany"
                ],
                "mountOptions": [
                    "flock"
                ],
                "persistentVolumeReclaimPolicy": "Recycle",
                "csi": {
                    "driver": "fsx.csi.aws.com",
                    "volumeHandle": config.volume_handle,
                    "volumeAttributes": {
                        "dnsname": config.volume_dns,
                        "mountname": config.volume_mount_name
                    }
                }
            }
        },
        {
            "apiVersion": "v1",
            "kind": "PersistentVolumeClaim",
            "metadata": {
                "name": f"{config.volume_name}-fsx-claim",
                "namespace": ns
            },
            "spec": {
                "accessModes": [
                    "ReadWriteMany"
                ],
                "storageClassName": "",
                "resources": {
                    "requests": {
                        "storage": f"{config.volume_size_in_gb}Gi"
                    }
                },
                "volumeName": f"{ns}-{config.volume_name}-fsx-pv"
            }
        }
    ]

    return config
