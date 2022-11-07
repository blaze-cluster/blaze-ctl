import typer

app = typer.Typer(no_args_is_help=True)


@app.command(no_args_is_help=True)
def create(ns: str,
           eks_cluster: str,
           volume_size_in_gb: int = 120,
           sa_policy_arn: str = None,
           gpu_enabled: bool = False):
    print(f"Hello {ns}")


@app.command(no_args_is_help=True)
def add_fsx_volume(ns: str,
                   volume_name: str,
                   volume_size_in_gb: int,
                   volume_handle: str,
                   volume_dns: str,
                   volume_mount_name: str):
    print(f"Hello {ns}")


@app.command(no_args_is_help=True)
def delete_fsx_volume(ns: str,
                      volume_name: str):
    print(f"Hello {ns}")


@app.command(no_args_is_help=True)
def delete(ns: str):
    # load config from namespace
    print(f"Bye {ns}!")
