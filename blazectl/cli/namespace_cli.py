import typer

from blazectl.namespace.config import NamespaceConfig, WorkerBlockDeviceConfig, FsxVolumeConfig
from blazectl.namespace.namespace import NamespaceManager, load_ns

app = typer.Typer(no_args_is_help=True)


@app.command(no_args_is_help=True)
def create(ns: str = typer.Option(..., "--namespace", "-n", prompt=True),
           eks_cluster: str = typer.Option(..., "--eks-cluster", "-eks", prompt=True),
           volume_size_in_gb: int = typer.Option(120),
           sa_policy_arn: str = typer.Option(None),
           gpu_enabled: bool = typer.Option(False)):
    namespace_config = NamespaceConfig(ns,
                                       eks_cluster,
                                       block_device=WorkerBlockDeviceConfig(volume_size_in_gb=volume_size_in_gb),
                                       sa_policy_arn=sa_policy_arn,
                                       gpu_enabled=gpu_enabled)
    manager = NamespaceManager(namespace_config)
    manager.create_ns()


@app.command(no_args_is_help=True)
def delete(ns: str = typer.Option(..., "--namespace", "-n", prompt=True)):
    manager = load_ns(ns)
    manager.delete_ns()


@app.command(no_args_is_help=True)
def set_gpu(ns: str = typer.Option(..., "--namespace", "-n", prompt=True),
            enabled: bool = typer.Option(..., prompt=True)):
    manager = load_ns(ns)
    manager.namespace_config.gpu_enabled = enabled
    manager.save_config()


@app.command(no_args_is_help=True)
def set_sa_policy(ns: str = typer.Option(..., "--namespace", "-n", prompt=True),
                  arn: str = typer.Option(..., prompt=True)):
    manager = load_ns(ns)
    if manager.namespace_config.sa_policy_arn is not None:
        manager.service_account_manager.delete_service_account()

    manager.namespace_config.sa_policy_arn = arn
    manager.service_account_manager.create_service_account()
    manager.save_config()


@app.command(no_args_is_help=True)
def add_fsx_volume(ns: str = typer.Option(..., "--namespace", "-n", prompt=True),
                   volume_name: str = typer.Option(..., prompt=True),
                   volume_size_in_gb: int = typer.Option(..., prompt=True),
                   volume_handle: str = typer.Option(..., prompt=True),
                   volume_dns: str = typer.Option(..., prompt=True),
                   volume_mount_name: str = typer.Option(..., prompt=True)):
    manager = load_ns(ns)
    fsx_volume_config = FsxVolumeConfig(volume_name,
                                        volume_size_in_gb,
                                        volume_handle,
                                        volume_dns,
                                        volume_mount_name)
    manager.fsx_volume_manager.create_fsx_volume(fsx_volume_config)
    manager.namespace_config.fsx_volumes.append(fsx_volume_config)
    manager.save_config()


@app.command(no_args_is_help=True)
def delete_fsx_volume(ns: str = typer.Option(..., "--namespace", "-n", prompt=True),
                      volume_name: str = typer.Option(..., prompt=True)):
    manager = load_ns(ns)

    items = [(index, item) for (index, item) in enumerate(manager.namespace_config.fsx_volumes)
             if item.volume_name == volume_name]
    if len(items) == 0:
        raise ValueError(f"Didn't find volume of name:{volume_name} in namespace:{ns}",
                         manager.namespace_config.fsx_volumes)

    for (index, item) in items:
        manager.fsx_volume_manager.delete_fsx_volume(item)


