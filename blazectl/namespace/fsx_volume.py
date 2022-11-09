from .config import FsxVolumeConfig, NamespaceConfig
from ..commons.utils import Utils


class FsxVolumeManager:
    def __init__(self, namespace_config: NamespaceConfig):
        self.namespace_config = namespace_config

    def create_fsx_volume(self, fsx_volume_config: FsxVolumeConfig):
        config = self.get_kubectl_config(fsx_volume_config)
        for c in config:
            Utils.kubectl_apply(c)

    def delete_fsx_volume(self, fsx_volume_config: FsxVolumeConfig):
        config = self.get_kubectl_config(fsx_volume_config)
        for c in config:
            Utils.kubectl_delete(c)

    def get_kubectl_config(self, fsx_volume_config: FsxVolumeConfig):
        return [
            {
                "apiVersion": "v1",
                "kind": "PersistentVolume",
                "metadata": {
                    "name": f"{self.namespace_config.name}-{fsx_volume_config.volume_name}-fsx-pv"
                },
                "spec": {
                    "capacity": {
                        "storage": f"{fsx_volume_config.volume_size_in_gb}Gi"
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
                        "volumeHandle": fsx_volume_config.volume_handle,
                        "volumeAttributes": {
                            "dnsname": fsx_volume_config.volume_dns,
                            "mountname": fsx_volume_config.volume_mount_name
                        }
                    }
                }
            },
            {
                "apiVersion": "v1",
                "kind": "PersistentVolumeClaim",
                "metadata": {
                    "name": f"{fsx_volume_config.volume_name}-fsx-claim",
                    "namespace": self.namespace_config.name
                },
                "spec": {
                    "accessModes": [
                        "ReadWriteMany"
                    ],
                    "storageClassName": "",
                    "resources": {
                        "requests": {
                            "storage": f"{fsx_volume_config.volume_size_in_gb}Gi"
                        }
                    },
                    "volumeName": f"{self.namespace_config.name}-{fsx_volume_config.volume_name}-fsx-pv"
                }
            }
        ]
