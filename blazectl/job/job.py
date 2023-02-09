import asyncio
import enum
import time
import webbrowser

import dns.resolver
from kubernetes import client as kube_client, config as kube_config
from ray.dashboard.modules.job.common import JobStatus
from ray.job_submission import JobSubmissionClient

from blazectl.cluster.cluster import ClusterManager


class ClusterStateOnJobRun(str, enum.Enum):
    STOP_THEN_START = "stop-and-start"
    TERMINATE_THEN_START = "terminate-then-start"
    NOTHING = "nothing"


class ClusterStateOnJobEnd(str, enum.Enum):
    STOP = "stop"
    TERMINATE = "terminate"
    NOTHING = "nothing"


JobEndStatuses = {JobStatus.SUCCEEDED, JobStatus.STOPPED, JobStatus.FAILED}


class JobManager:
    def __init__(self, cluster_name: str, cluster_ns: str):
        self.cluster_name = cluster_name
        self.cluster_ns = cluster_ns

    def get_job_client(self):
        svc_addr = JobManager.get_svc_addr(self.cluster_ns, self.cluster_name)
        svc_addr = f"http://{svc_addr}:8265"
        return svc_addr, JobSubmissionClient(svc_addr)

    def run_job(self,
                entrypoint: str,
                working_dir: str = "./",
                pip: list[str] = None,
                # conda: list[str] = None,
                on_job_run: ClusterStateOnJobRun = ClusterStateOnJobRun.NOTHING,
                on_job_success: ClusterStateOnJobEnd = ClusterStateOnJobEnd.NOTHING,
                on_job_failure: ClusterStateOnJobEnd = ClusterStateOnJobEnd.NOTHING,
                wait_for_job_end: bool = True):

        self.set_cluster_state_on_job_run(on_job_run)

        svc_addr, job_client = self.get_job_client()
        job_id = job_client.submit_job(
            entrypoint=entrypoint,
            runtime_env={
                "working_dir": working_dir,
                "pip": pip,
                # "conda": conda
            }
        )
        print(f"JOB_ID:{job_id} is submitted on {svc_addr}")

        # open dashboard in new tab
        webbrowser.open(svc_addr, new=2)

        if wait_for_job_end:
            self.wait_until_job_end(job_id,
                                    on_job_success=on_job_success,
                                    on_job_failure=on_job_failure)

    def stop_job(self,
                 job_id,
                 on_job_stop: ClusterStateOnJobEnd = ClusterStateOnJobEnd.NOTHING,
                 on_job_failure: ClusterStateOnJobEnd = ClusterStateOnJobEnd.NOTHING):
        svc_addr, job_client = self.get_job_client()
        status = job_client.stop_job(job_id=job_id)
        print(f"Stopped job={job_id} with status={status}")

        self.wait_until_job_end(job_id,
                                on_job_success=on_job_stop,
                                on_job_failure=on_job_failure)

    def tail_job_logs(self, job_id):
        asyncio.run(self._tail_job_logs(job_id))

    async def _tail_job_logs(self, job_id):
        svc_addr, job_client = self.get_job_client()
        async for lines in job_client.tail_job_logs(job_id):
            print(lines, end="")

    def job_logs(self, job_id):
        svc_addr, job_client = self.get_job_client()
        logs = job_client.get_job_logs(job_id)
        print(logs)

    def wait_until_job_end(self,
                           job_id,
                           timeout_seconds=3600 * 24,  # wait for 24 hours
                           on_job_success: ClusterStateOnJobEnd = ClusterStateOnJobEnd.STOP,
                           on_job_failure: ClusterStateOnJobEnd = ClusterStateOnJobEnd.STOP):
        svc_addr, job_client = self.get_job_client()
        start = time.time()
        while time.time() - start <= timeout_seconds:
            status = job_client.get_job_status(job_id)
            print(f"{job_id} is {status}")
            if status in JobEndStatuses:
                if status == JobStatus.SUCCEEDED or status == JobStatus.STOPPED:
                    self.set_cluster_state_on_job_end(on_job_success)
                elif status == JobStatus.FAILED:
                    self.set_cluster_state_on_job_end(on_job_failure)

                break

            time.sleep(1)

    def set_cluster_state_on_job_run(self, cluster_state: ClusterStateOnJobRun):
        if cluster_state == ClusterStateOnJobRun.NOTHING:
            return

        cluster_manager = ClusterManager.load(self.cluster_name, self.cluster_ns)
        if cluster_state == ClusterStateOnJobRun.STOP_THEN_START:
            cluster_manager.restart_cluster()
        elif cluster_state == ClusterStateOnJobRun.TERMINATE_THEN_START:
            cluster_manager.restart_cluster(restart_head=True)

    def set_cluster_state_on_job_end(self, cluster_state: ClusterStateOnJobEnd):
        if cluster_state == ClusterStateOnJobEnd.NOTHING:
            return

        cluster_manager = ClusterManager.load(self.cluster_name, self.cluster_ns)
        if cluster_state == ClusterStateOnJobEnd.STOP:
            cluster_manager.stop_cluster()
        elif cluster_state == ClusterStateOnJobEnd.TERMINATE:
            cluster_manager.terminate_cluster()

    def job_status(self, job_id):
        svc_addr, job_client = self.get_job_client()
        status = job_client.get_job_status(job_id)
        print(f"{job_id} is {status}")

    @staticmethod
    def get_svc_addr(cluster_ns: str, cluster_name: str):
        kube_config.load_config()
        v1_api = kube_client.CoreV1Api()
        result = v1_api.read_namespaced_service(name=f"{cluster_name}-head-svc", namespace=cluster_ns)

        svc_addr = result.status.load_balancer.ingress[0].hostname

        # we will try resolve svc addr and wait till it is resolved
        dns_resolved = False
        while not dns_resolved:
            try:
                answers = dns.resolver.resolve(svc_addr, 'A')
                # print(f"Answers for {svc_addr} = ", answers)
                dns_resolved = True
            except dns.resolver.NoAnswer:
                time.sleep(2)

        return svc_addr
