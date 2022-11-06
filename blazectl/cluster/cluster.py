
import json
from dataclasses import dataclass

from blazectl.commons.manage_base import ManagerBase
from blazectl.namespace.namespace import NamespaceConfig


@dataclass
class ClusterSpec:
    ray_version: str = "2.0.0"
    ray_image: str = "514352861371.dkr.ecr.ap-south-1.amazonaws.com/recsys/ray-ml:2.0.1"
    busybox_image: str = "514352861371.dkr.ecr.ap-south-1.amazonaws.com/recsys/busybox:latest"
    aws_cli_image: str = "514352861371.dkr.ecr.ap-south-1.amazonaws.com/recsys/aws-cli:latest"


@dataclass
class AutoscalerSpec:
    enabled: bool = False,
    idle_timeout_in_seconds: int = 300


@dataclass
class HeadConfig:
    instance_type: str


@dataclass
class WorkerConfig:
    instance_type: str
    name: str = "default"
    count: int = 0


@dataclass
class ClusterConfig:
    name: str
    ns: NamespaceConfig
    head: HeadConfig
    workers: list[WorkerConfig]
    autoscaler: AutoscalerSpec = AutoscalerSpec()
    spec: ClusterSpec = ClusterSpec()


class ClusterManger(ManagerBase):
    def __init__(self, cluster_config: ClusterConfig):
        super().__init__()

        self.cluster_config = cluster_config

        with open("aws_instance_types.json") as file:
            self.instance_types_map = json.load(file)

    def create_cluster(self):
        config = self.get_cluster_config()
        self.kubectl_apply(config)

    def delete_cluster(self):
        config = self.get_cluster_config()
        self.kubectl_delete(config)

    def restart_cluster(self):
        self.delete_cluster()
        self.create_cluster()

    def print_config(self):
        config = self.get_cluster_config()
        ManagerBase.print_data(config)

    def get_cluster_config(self):
        return {
            "apiVersion": "ray.io/v1alpha1",
            "kind": "RayCluster",
            "metadata": {
                "labels": {
                    "controller-tools.k8s.io": "1.0"
                },
                "name": self.cluster_config.name,
                "namespace": self.cluster_config.ns.name
            },
            "spec": {
                "rayVersion": self.cluster_config.spec.ray_version,
                "enableInTreeAutoscaling": self.cluster_config.autoscaler.enabled,
                # "autoscalerOptions": {
                #     "upscalingMode": "Default",
                #     "idleTimeoutSeconds": cluster_config.autoscaler.idle_timeout_in_seconds,
                #     "imagePullPolicy": "Always",
                #     "resources": {
                #         "limits": {
                #             "cpu": "1",
                #             "memory": "2Gi"
                #         },
                #         "requests": {
                #             "cpu": "1",
                #             "memory": "2Gi"
                #         }
                #     }
                # },
                "headGroupSpec": {
                    "serviceType": "LoadBalancer",
                    "enableIngress": True,
                    "rayStartParams": {
                        "dashboard-host": "0.0.0.0",
                        "block": "true",
                        "num-cpus": "0"
                    },
                    "template": {
                        "spec": {
                            "serviceAccountName": self.get_service_account(),
                            "nodeSelector": {
                                "node.kubernetes.io/instance-type": self.cluster_config.head.instance_type,
                                "ray-cluster/namespace": self.cluster_config.ns.name,
                                "ray-cluster/node-type": "head"
                            },
                            "containers": [
                                {
                                    "name": "ray-head",
                                    "image": self.cluster_config.spec.ray_image,
                                    "imagePullPolicy": "Always",
                                    "ports": [
                                        {
                                            "containerPort": 6379,
                                            "name": "gcs"
                                        },
                                        {
                                            "containerPort": 8265,
                                            "name": "dashboard"
                                        },
                                        {
                                            "containerPort": 10001,
                                            "name": "client"
                                        }
                                    ],
                                    "lifecycle": {
                                        "preStop": {
                                            "exec": {
                                                "command": [
                                                    "/bin/sh",
                                                    "-c",
                                                    "ray stop --force"
                                                ]
                                            }
                                        }
                                    },
                                    "resources": self.get_resource_limits(self.cluster_config.head.instance_type),
                                    "volumeMounts": self.get_volume_mounts()
                                },
                                {
                                    "name": "aws-cli",
                                    "image": self.cluster_config.spec.aws_cli_image,
                                    "imagePullPolicy": "IfNotPresent",
                                    "command": [
                                        "sleep",
                                        "3600"
                                    ]
                                }
                            ],
                            "volumes": self.get_volumes()
                        }
                    }
                },
                "workerGroupSpecs": [self.get_worker_config(worker_config)
                                     for worker_config in self.cluster_config.workers]
            }
        }

    def get_worker_config(self, worker_config: WorkerConfig):
        return {
            "groupName": worker_config.name,
            "replicas": worker_config.count,
            "minReplicas": worker_config.count,
            "maxReplicas": worker_config.count * 10,
            "rayStartParams": {
                "block": "true"
            },
            "template": {
                "spec": {
                    "serviceAccount": self.get_service_account(),
                    "nodeSelector": {
                        "node.kubernetes.io/instance-type": worker_config.instance_type,
                        "ray-cluster/namespace": self.cluster_config.ns.name,
                        "ray-cluster/node-type": "worker"
                    },
                    "volumes": self.get_volumes(),
                    "initContainers": [
                        {
                            "name": "init-myservice",
                            "image": self.cluster_config.spec.busybox_image,
                            "command": [
                                "sh",
                                "-c",
                                "until nslookup "
                                f"{self.cluster_config.name}-head-svc."
                                "$(cat /var/run/secrets/kubernetes.io/serviceaccount/namespace)."
                                "svc.cluster.local; "
                                "do echo waiting for myservice; sleep 2; done"
                            ]
                        }
                    ],
                    "containers": [
                        {
                            "name": "worker",
                            "image": self.cluster_config.spec.ray_image,
                            "imagePullPolicy": "Always",
                            "lifecycle": {
                                "preStop": {
                                    "exec": {
                                        "command": [
                                            "/bin/sh",
                                            "-c",
                                            "ray stop --force"
                                        ]
                                    }
                                }
                            },
                            "resources": self.get_resource_limits(worker_config.instance_type),
                            "volumeMounts": self.get_volume_mounts()
                        },
                        {
                            "name": "aws-cli",
                            "image": self.cluster_config.spec.aws_cli_image,
                            "imagePullPolicy": "IfNotPresent",
                            "command": [
                                "sleep",
                                "3600"
                            ]
                        }
                    ]
                }
            }
        }

    def get_service_account(self):
        service_account = None
        if self.cluster_config.ns.sa_policy_arn is not None:
            service_account = f"{self.cluster_config.ns.name}-isra"
        return service_account

    def get_volumes(self):
        volumes = [
            {
                "name": "ray-logs",
                "emptyDir": {}
            },
            {
                "name": "ray-data",
                "emptyDir": {}
            }
        ]

        for fsx in self.cluster_config.ns.fsx_volumes:
            volumes.append({
                "name": f"{fsx.volume_name}-store",
                "persistentVolumeClaim": {
                    "claimName": f"{fsx.volume_name}-fsx-claim"
                }
            })

        return volumes

    def get_volume_mounts(self):
        mounts = [
            {
                "mountPath": "/tmp/ray",
                "name": "ray-logs"
            },
            {
                "mountPath": "/data",
                "name": "ray-data"
            }
        ]

        for fsx in self.cluster_config.ns.fsx_volumes:
            mounts.append({
                "mountPath": f"/mnt/{fsx.volume_name}",
                "name": f"{fsx.volume_name}-store"
            })

        return mounts

    # TODO: support gpu workers
    def get_resource_limits(self, instance_type: str):
        data = self.instance_types_map.get(instance_type)
        if data is None:
            raise ValueError(f"Invalid instance type: {instance_type}")

        cpu = data.get("cpu")
        memory = data.get("memory")
        return {
            "limits": {
                "cpu": cpu,
                "memory": memory
            },
            "requests": {
                "cpu": cpu,
                "memory": memory
            }
        }
