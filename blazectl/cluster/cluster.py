from __future__ import annotations

import dataclasses
import enum
import json
import os
from copy import deepcopy
from dataclasses import dataclass

import dacite
import typer
from kubernetes import client as kube_client, config as kube_config, watch as kube_watch

from blazectl.commons.utils import Utils
from blazectl.namespace.namespace import NamespaceManager


class Platform(str, enum.Enum):
    TF = "tf"
    TORCH = "torch"


@dataclass
class ClusterSpec:
    ray_version: str = "2.0.0"
    blaze_image_path: str = "514352861371.dkr.ecr.ap-south-1.amazonaws.com/recsys/blaze"
    busybox_image: str = "514352861371.dkr.ecr.ap-south-1.amazonaws.com/recsys/busybox:latest"

    def blaze_image(self, platform: str, gpu: bool):
        return f"{self.blaze_image_path}-{platform}:latest{'-gpu' if gpu else ''}"


# @dataclass
# class AutoscalerSpec:
#     enabled: bool = False,
#     idle_timeout_in_seconds: int = 300


@dataclass
class HeadConfig:
    instance_type: str


@dataclass
class WorkersGroupConfig:
    instance_type: str
    name: str = "default"
    count: int = 0
    gpu: bool = False


@dataclass
class ClusterConfig:
    name: str
    ns: str
    platform: str
    head: HeadConfig
    worker_groups: list[WorkersGroupConfig]
    # autoscaler: AutoscalerSpec = AutoscalerSpec()
    spec: ClusterSpec = ClusterSpec()
    __deleted__: bool = False


class WatchState(str, enum.Enum):
    RUNNING = "running"
    DELETED = "deleted"


class ClusterManager:
    def __init__(self, cluster_config: ClusterConfig):
        self.cluster_config = cluster_config

        self.ns = NamespaceManager.load_config(cluster_config.ns)

        with open(f"{os.path.realpath(os.path.dirname(__file__))}/aws_instance_types.json") as file:
            self.instance_types_map = json.load(file)

    def start_cluster(self, save_config=False):
        Utils.kubectl_apply(self.get_kubectl_config())

        if save_config:
            self.save_config()

        self.watch_cluster_state({"head": WatchState.RUNNING, "worker": WatchState.RUNNING})

    def terminate_cluster(self):
        Utils.kubectl_delete(self.get_kubectl_config())

        self.watch_cluster_state({"head": WatchState.DELETED, "worker": WatchState.DELETED})

    def stop_cluster(self):
        # we only remove worker_groups by setting their count to zero
        cluster_config = deepcopy(self.cluster_config)
        for worker in cluster_config.worker_groups:
            worker.count = 0

        temp_cluster_mgr = ClusterManager(cluster_config)
        Utils.kubectl_apply(temp_cluster_mgr.get_kubectl_config())

        self.watch_cluster_state({"head": WatchState.RUNNING, "worker": WatchState.DELETED})

    def watch_cluster_state(self,
                            end_states: dict[str, WatchState]):
        label_selector = f"ray.io/cluster={self.cluster_config.name}"

        # build list of pods to watch for
        # maintain a counter of how many have reached the stage
        total_workers = 0
        for worker in self.cluster_config.worker_groups:
            total_workers += worker.count

        end_counts = {"head": 1, "worker": total_workers}

        # state wise - count
        state_summary = {}

        # per pod - current state
        pods_state = {}

        current_counts = {"head": 0, "worker": 0}

        watch = kube_watch.Watch()
        kube_config.load_config()
        kube_api = kube_client.CoreV1Api()
        for event in watch.stream(func=kube_api.list_namespaced_pod,
                                  namespace=self.ns.name,
                                  label_selector=label_selector,
                                  timeout_seconds=0):
            event_object = event["object"]
            event_type = event['type']
            object_type = event_object.kind
            pod_name = event_object.metadata.name
            pod_phase = event_object.status.phase
            pod_type = event_object.metadata.labels['ray.io/node-type']

            if object_type != "Pod":
                continue

            print(f"=====> Event Type={event_type} "
                  f"Pod Type={pod_type} "
                  f"Pod Name={pod_name} "
                  f"Phase={pod_phase}")

            # print(f"Detailed Status: ", event_object.status)

            pod_end_state = end_states[pod_type]

            if pod_end_state == WatchState.DELETED and event_type == "DELETED" or pod_end_state == WatchState.RUNNING and pod_phase == "Running":
                current_counts[pod_type] += 1

            end_state_reached = True
            for pt in ["head", "worker"]:
                if current_counts[pt] != end_counts[pt]:
                    end_state_reached = False

            # print("Current counts: ", current_counts)
            # print("End counts: ", end_counts)
            # print("End state: ", end_state_reached)

            if end_state_reached:
                watch.stop()
                return

    def delete_cluster(self):
        self.terminate_cluster()

    def restart_cluster(self, restart_head: bool = False):
        if restart_head:
            self.terminate_cluster()
        else:
            self.stop_cluster()
        self.start_cluster()

    def config_as_dict(self):
        return dataclasses.asdict(self.cluster_config)

    @staticmethod
    def config_name(name: str, ns: str):
        return f"cluster.{ns}.{name}"

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
                "enableInTreeAutoscaling": False,
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
                                "blaze-cluster/namespace": self.ns.name,
                                "blaze-cluster/node-type": "head"
                            },
                            "containers": [
                                {
                                    "name": "ray-head",
                                    "image": self.cluster_config.spec.blaze_image(self.cluster_config.platform, False),
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
                                }
                            ],
                            "volumes": self.get_volumes()
                        }
                    }
                },
                "workerGroupSpecs": [self.get_worker_config(worker_config)
                                     for worker_config in self.cluster_config.worker_groups]
            }
        }

    def get_worker_config(self, worker_config: WorkersGroupConfig):
        resources = self.get_resource_limits(worker_config.instance_type, worker_config.gpu)

        return {
            "groupName": worker_config.name,
            "replicas": worker_config.count,
            "minReplicas": worker_config.count,
            "maxReplicas": worker_config.count * 10,
            "rayStartParams": {
                "block": "true",
                "num-gpus": "0" if not worker_config.gpu else resources["limits"]["nvidia.com/gpu"]
            },
            "template": {
                "spec": {
                    "serviceAccount": self.get_service_account(),
                    "nodeSelector": {
                        "node.kubernetes.io/instance-type": worker_config.instance_type,
                        "blaze-cluster/namespace": self.ns.name,
                        "blaze-cluster/node-type": "worker"
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
                            "image": self.cluster_config.spec.blaze_image(self.cluster_config.platform, worker_config.gpu),
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
                            "resources": resources,
                            "volumeMounts": self.get_volume_mounts()
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

    def get_resource_limits(self, instance_type: str, gpu: bool = False):
        data = self.instance_types_map.get(instance_type)
        if data is None:
            print(f"Invalid instance type: {instance_type} - not found")
            raise typer.Abort()

        if gpu and data.get("nvidia.com/gpu") is None:
            print(f"Invalid instance type: {instance_type} - not a gpu instance")
            raise typer.Abort()

        if not gpu and data.get("nvidia.com/gpu") is not None:
            print(f"Invalid instance type: {instance_type} - a gpu instance but gpu support is not needed")
            raise typer.Abort()

        cpu = int(data.get("cpu").rstrip("m")) // 1024
        memory = data.get("memory")

        config = {
            "limits": {
                "cpu": cpu,
                "memory": memory
            },
            "requests": {
                "cpu": cpu,
                "memory": memory
            }
        }

        if gpu:
            config["limits"]["nvidia.com/gpu"] = data.get("nvidia.com/gpu")
            config["requests"]["nvidia.com/gpu"] = data.get("nvidia.com/gpu")

        return config
