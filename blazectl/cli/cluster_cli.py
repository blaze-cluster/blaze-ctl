import typer

from blazectl.cluster.cluster import ClusterManager, ClusterConfig, HeadConfig, Platform, WorkersGroupConfig

app = typer.Typer(no_args_is_help=True)


@app.command(no_args_is_help=True)
def create(name: str = typer.Option(..., "--name", "-c", prompt=True),
           ns: str = typer.Option(..., "--namespace", "-n", prompt=True),
           platform: Platform = typer.Option(..., "--platform", "-p", case_sensitive=False, prompt=True),
           head_node: str = typer.Option(..., prompt=True),
           default_workers_node: str = typer.Option(..., prompt=True),
           default_workers_count: int = typer.Option(0),
           default_workers_gpu: bool = typer.Option(False)):
    # build cluster config
    cluster_config = ClusterConfig(name,
                                   ns,
                                   platform=platform,
                                   head=HeadConfig(instance_type=head_node),
                                   worker_groups=[WorkersGroupConfig(name="default",
                                                                     instance_type=default_workers_node,
                                                                     count=default_workers_count,
                                                                     gpu=default_workers_gpu)])
    manager = ClusterManager(cluster_config)
    manager.start_cluster(save_config=True)


@app.command(no_args_is_help=True)
def start(name: str = typer.Option(..., "--name", "-c", prompt=True),
          ns: str = typer.Option(..., "--namespace", "-n", prompt=True)):
    manager = ClusterManager.load(name, ns)
    manager.start_cluster()


@app.command(no_args_is_help=True)
def stop(name: str = typer.Option(..., "--name", "-c", prompt=True),
         ns: str = typer.Option(..., "--namespace", "-n", prompt=True)):
    manager = ClusterManager.load(name, ns)
    manager.stop_cluster()


@app.command(no_args_is_help=True)
def terminate(name: str = typer.Option(..., "--name", "-c", prompt=True),
              ns: str = typer.Option(..., "--namespace", "-n", prompt=True)):
    manager = ClusterManager.load(name, ns)
    manager.terminate_cluster()


@app.command(no_args_is_help=True)
def delete(name: str = typer.Option(..., "--name", "-c", prompt=True),
           ns: str = typer.Option(..., "--namespace", "-n", prompt=True)):
    manager = ClusterManager.load(name, ns)
    manager.delete_cluster()

    manager.soft_delete_config()


@app.command(no_args_is_help=True)
def restart(name: str = typer.Option(..., "--name", "-c", prompt=True),
            ns: str = typer.Option(..., "--namespace", "-n", prompt=True),
            restart_head: bool = typer.Option(False)):
    manager = ClusterManager.load(name, ns)

    manager.restart_cluster(restart_head)
