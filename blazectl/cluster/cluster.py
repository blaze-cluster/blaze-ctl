from __future__ import annotations

import dataclasses
import json
from copy import deepcopy
from dataclasses import dataclass

import dacite

from blazectl.commons.utils import Utils
from blazectl.namespace.namespace import NamespaceManager


@dataclass
class ClusterSpec:
    ray_version: str = "2.0.0"
    ray_image: str = "514352861371.dkr.ecr.ap-south-1.amazonaws.com/recsys/ray-ml:2.0.1"
    busybox_image: str = "514352861371.dkr.ecr.ap-south-1.amazonaws.com/recsys/busybox:latest"
    aws_cli_image: str = "514352861371.dkr.ecr.ap-south-1.amazonaws.com/recsys/aws-app:latest"


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
    ns: str
    head: HeadConfig
    workers: list[WorkerConfig]
    autoscaler: AutoscalerSpec = AutoscalerSpec()
    spec: ClusterSpec = ClusterSpec()
    __deleted__: bool = False


class ClusterManager:
    def __init__(self, cluster_config: ClusterConfig):
        self.cluster_config = cluster_config

        self.ns = NamespaceManager.load_config(cluster_config.ns)

        with open("aws_instance_types.json") as file:
            self.instance_types_map = json.load(file)

    def create_cluster(self):
        Utils.kubectl_apply(self.get_kubectl_config())

    def stop_cluster(self, stop_head: bool = False):
        if stop_head:
            Utils.kubectl_delete(self.get_kubectl_config())
        else:
            # we only remove workers by setting their count to zero
            cluster_config = deepcopy(self.cluster_config)
            for worker in cluster_config.workers:
                worker.count = 0

            temp_cluster_mgr = ClusterManager(cluster_config)
            Utils.kubectl_apply(temp_cluster_mgr.get_kubectl_config())

    def delete_cluster(self):
        Utils.kubectl_delete(self.get_kubectl_config())

    def restart_cluster(self, restart_head: bool = False):
        self.stop_cluster(stop_head=restart_head)
        self.create_cluster()

    def config_as_dict(self):
        return dataclasses.asdict(self.cluster_config)

    @staticmethod
    def config_name(name: str, ns: str):
        return f"cluster/{ns}/{name}"

    def save_config(self):
        Utils.save_config(ClusterManager.config_name(self.cluster_config.name, self.ns.name),
                          self.config_as_dict())

    def soft_delete_config(self):
        self.cluster_config.__deleted__ = True
        self.save_config()

    def delete_config(self):
        Utils.delete_config(ClusterManager.config_name(self.cluster_config.name, self.ns.name))

    @staticmethod
    def load_config(name: str, ns: str) -> ClusterConfig:
        config = Utils.load_config(ClusterManager.config_name(name, ns))
        return dacite.from_dict(data_class=ClusterConfig, data=config)

    @staticmethod
    def load(name: str, ns: str) -> ClusterManager:
        config = ClusterManager.load_config(name, ns)
        return ClusterManager(config)

    def get_kubectl_config(self):
        return {
            "apiVersion": "ray.io/v1alpha1",
            "kind": "RayCluster",
            "metadata": {
                "labels": {
                    "controller-tools.k8s.io": "1.0"
                },
                "name": self.cluster_config.name,
                "namespace": self.ns.name
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
                                "ray-cluster/namespace": self.ns.name,
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
                                    "name": "aws-app",
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
                        "ray-cluster/namespace": self.ns.name,
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
                            "name": "aws-app",
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
        if self.ns.sa_policy_arn is not None:
            service_account = f"{self.ns.name}-isra"
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

        for fsx in self.ns.fsx_volumes:
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

        for fsx in self.ns.fsx_volumes:
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
