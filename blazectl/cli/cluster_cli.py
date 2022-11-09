import typer

from blazectl.cluster.cluster import ClusterManager, ClusterConfig, HeadConfig, WorkersGroupConfig

app = typer.Typer(no_args_is_help=True)


@app.command(no_args_is_help=True)
def create(name: str = typer.Option(..., prompt=True),
           ns: str = typer.Option(..., "--namespace", "-n", prompt=True),
           head_instance_type: str = typer.Option(None),
           default_workers_instance_type: str = typer.Option(None),
           default_workers_count: int = typer.Option(0)):
    # build cluster config
    cluster_config = ClusterConfig(name,
                                   ns,
                                   head=HeadConfig(instance_type=head_instance_type),
                                   worker_groups=[WorkersGroupConfig(instance_type=default_workers_instance_type,
                                                                     count=default_workers_count)])
    manager = ClusterManager(cluster_config)
    manager.create_cluster()

    manager.save_config()


@app.command(no_args_is_help=True)
def stop(name: str = typer.Option(..., prompt=True),
         ns: str = typer.Option(..., "--namespace", "-n", prompt=True)):
    manager = ClusterManager.load(name, ns)
    manager.stop_cluster(stop_head=False)


@app.command(no_args_is_help=True)
def terminate(name: str = typer.Option(..., prompt=True),
              ns: str = typer.Option(..., "--namespace", "-n", prompt=True)):
    manager = ClusterManager.load(name, ns)
    manager.stop_cluster(stop_head=True)


@app.command(no_args_is_help=True)
def delete(name: str = typer.Option(..., prompt=True),
           ns: str = typer.Option(..., "--namespace", "-n", prompt=True)):
    manager = ClusterManager.load(name, ns)
    manager.delete_cluster()

    manager.soft_delete_config()


@app.command(no_args_is_help=True)
def restart(name: str = typer.Option(..., prompt=True),
            ns: str = typer.Option(..., "--namespace", "-n", prompt=True),
            restart_head: bool = typer.Option(False)):
    manager = ClusterManager.load(name, ns)

    manager.restart_cluster(restart_head)
