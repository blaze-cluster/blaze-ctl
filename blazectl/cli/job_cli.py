from typing import Optional

import typer

from blazectl.job.job import ClusterStateOnJobRun, ClusterStateOnJobEnd, JobManager

app = typer.Typer(no_args_is_help=True)


@app.command(no_args_is_help=True)
def run(cluster_name: str = typer.Option(..., "--cluster-name", "-c", prompt=True),
        cluster_ns: str = typer.Option(..., "--cluster-ns", "-n", prompt=True),
        entrypoint: str = typer.Option(..., "--entrypoint", "-e", prompt=True),
        working_dir: str = typer.Option("./"),
        pip: Optional[list[str]] = typer.Option(None),
        # conda: Optional[list[str]] = typer.Option(None),
        on_job_run: ClusterStateOnJobRun = typer.Option(ClusterStateOnJobRun.NOTHING, case_sensitive=False),
        on_job_success: ClusterStateOnJobEnd = typer.Option(ClusterStateOnJobEnd.NOTHING, case_sensitive=False),
        on_job_failure: ClusterStateOnJobEnd = typer.Option(ClusterStateOnJobEnd.NOTHING, case_sensitive=False),
        wait_for_job_end: bool = typer.Option(True)
        ):
    job_manager = JobManager(cluster_name, cluster_ns)
    job_manager.run_job(entrypoint=entrypoint,
                        working_dir=working_dir,
                        pip=pip,
                        # conda=conda,
                        on_job_run=on_job_run,
                        on_job_success=on_job_success,
                        on_job_failure=on_job_failure,
                        wait_for_job_end=wait_for_job_end)


@app.command(no_args_is_help=True)
def stop(cluster_name: str = typer.Option(..., "--cluster-name", "-c", prompt=True),
         cluster_ns: str = typer.Option(..., "--cluster-ns", "-n", prompt=True),
         job_id: str = typer.Option(..., "--job-id", "-j", prompt=True),
         on_job_stop: ClusterStateOnJobEnd = typer.Option(ClusterStateOnJobEnd.NOTHING, case_sensitive=False),
         on_job_failure: ClusterStateOnJobEnd = typer.Option(ClusterStateOnJobEnd.NOTHING, case_sensitive=False)
         ):
    job_manager = JobManager(cluster_name, cluster_ns)
    job_manager.stop_job(job_id,
                         on_job_stop=on_job_stop,
                         on_job_failure=on_job_failure)


@app.command(no_args_is_help=True)
def wait_until_job_end(cluster_name: str = typer.Option(..., "--cluster-name", "-c", prompt=True),
                       cluster_ns: str = typer.Option(..., "--cluster-ns", "-n", prompt=True),
                       job_id: str = typer.Option(..., "--job-id", "-j", prompt=True),
                       timeout_seconds=typer.Option(3600 * 24),  # wait for 24 hours
                       on_job_success: ClusterStateOnJobEnd = typer.Option(ClusterStateOnJobEnd.NOTHING, case_sensitive=False),
                       on_job_failure: ClusterStateOnJobEnd = typer.Option(ClusterStateOnJobEnd.NOTHING, case_sensitive=False)
                       ):
    job_manager = JobManager(cluster_name, cluster_ns)
    job_manager.wait_until_job_end(job_id,
                                   timeout_seconds=timeout_seconds,
                                   on_job_success=on_job_success,
                                   on_job_failure=on_job_failure)


@app.command(no_args_is_help=True)
def status(cluster_name: str = typer.Option(..., "--cluster-name", "-c", prompt=True),
           cluster_ns: str = typer.Option(..., "--cluster-ns", "-n", prompt=True),
           job_id: str = typer.Option(..., "--job-id", "-j", prompt=True)):
    job_manager = JobManager(cluster_name, cluster_ns)
    job_manager.job_status(job_id)


@app.command(no_args_is_help=True)
def tail_logs(cluster_name: str = typer.Option(..., "--cluster-name", "-c", prompt=True),
              cluster_ns: str = typer.Option(..., "--cluster-ns", "-n", prompt=True),
              job_id: str = typer.Option(..., "--job-id", "-j", prompt=True)):
    job_manager = JobManager(cluster_name, cluster_ns)
    job_manager.tail_job_logs(job_id)


@app.command(no_args_is_help=True)
def download_logs(cluster_name: str = typer.Option(..., "--cluster-name", "-c", prompt=True),
                  cluster_ns: str = typer.Option(..., "--cluster-ns", "-n", prompt=True),
                  job_id: str = typer.Option(..., "--job-id", "-j", prompt=True)):
    job_manager = JobManager(cluster_name, cluster_ns)
    job_manager.job_logs(job_id)
