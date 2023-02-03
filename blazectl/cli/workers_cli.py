import typer

from blazectl.cluster.cluster import ClusterManager, WorkersGroupConfig

app = typer.Typer(no_args_is_help=True)


@app.command(no_args_is_help=True)
def add(name: str = typer.Option(..., prompt=True),
        cluster_name: str = typer.Option(..., "--cluster", "-c", prompt=True),
        cluster_ns: str = typer.Option(..., "--namespace", "-n", prompt=True),
        instance_type: str = typer.Option(..., prompt=True),
        count: int = typer.Option(0),
        gpu: bool = typer.Option(False)):
    cluster_manager = ClusterManager.load(cluster_name, cluster_ns)

    # worker may already be there - check for it
    for worker in cluster_manager.cluster_config.worker_groups:
        if worker.name == name:
            print(f"Duplicate workers-group is not allowed: {name}")
            raise typer.Abort()

    workers_group = WorkersGroupConfig(name=name, instance_type=instance_type, count=count, gpu=gpu)
    cluster_manager.cluster_config.worker_groups.append(workers_group)

    cluster_manager.start_cluster()
    cluster_manager.save_config()


@app.command(no_args_is_help=True)
def update(name: str = typer.Option(..., prompt=True),
           cluster_name: str = typer.Option(..., "--cluster", "-c", prompt=True),
           cluster_ns: str = typer.Option(..., "--namespace", "-n", prompt=True),
           instance_type: str = typer.Option(None, prompt=True),
           count: int = typer.Option(None),
           gpu: bool = typer.Option(None)):
    cluster_manager = ClusterManager.load(cluster_name, cluster_ns)

    # worker may not be there - check for it
    found = None
    for worker in cluster_manager.cluster_config.worker_groups:
        if worker.name == name:
            found = worker

    if found is None:
        print(f"Can not find workers-group={name}")
        raise typer.Abort()

    # if instance type or gpu support is changed - then stop cluster and then start
    if found.instance_type != instance_type or found.gpu != gpu:
        cluster_manager.stop_cluster()

    found.instance_type = instance_type
    found.gpu = gpu
    found.count = count

    cluster_manager.start_cluster()
    cluster_manager.save_config()


@app.command(no_args_is_help=True)
def delete(name: str = typer.Option(..., prompt=True),
           cluster_name: str = typer.Option(..., "--cluster", "-c", prompt=True),
           cluster_ns: str = typer.Option(..., "--namespace", "-n", prompt=True)):
    if name == "default":
        # worker may be default - which is not allowed
        print(f"Deleting `default' workers-group is not allowed")
        raise typer.Abort()

    cluster_manager = ClusterManager.load(cluster_name, cluster_ns)

    # worker may not be there - check for it
    found = -1
    for index, worker in enumerate(cluster_manager.cluster_config.worker_groups):
        if worker.name == name:
            found = index

    if found == -1:
        print(f"Can not find workers-group={name}")
        raise typer.Abort()

    del cluster_manager.cluster_config.worker_groups[found]

    cluster_manager.restart_cluster(restart_head=True)
    cluster_manager.save_config()


@app.command(no_args_is_help=True)
def set_replicas(name: str = typer.Option(..., prompt=True),
                 cluster_name: str = typer.Option(..., "--cluster", "-c", prompt=True),
                 cluster_ns: str = typer.Option(..., "--namespace", "-n", prompt=True),
                 count: int = typer.Option(..., prompt=True)):
    cluster_manager = ClusterManager.load(cluster_name, cluster_ns)

    found = None
    for worker in cluster_manager.cluster_config.worker_groups:
        if worker.name == name:
            found = worker

    if found is None:
        print(f"ERROR: Can not find workers-group={name}")
        raise typer.Abort()

    found.count = count
    cluster_manager.start_cluster()
    cluster_manager.save_config()
