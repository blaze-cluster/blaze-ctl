import typer

app = typer.Typer(no_args_is_help=True)


@app.command(no_args_is_help=True)
def create(ns: str = typer.Option(..., "--namespace", "-n", prompt=True),
           eks_cluster: str = typer.Option(..., "--eks-cluster", "-eks", prompt=True),
           volume_size_in_gb: int = typer.Option(120),
           sa_policy_arn: str = typer.Option(None),
           gpu_enabled: bool = typer.Option(False)):
    print(f"Hello {ns}")


@app.command(no_args_is_help=True)
def delete(ns: str = typer.Option(..., "--namespace", "-n", prompt=True)):
    # load config from namespace
    print(f"Bye {ns}!")


@app.command(no_args_is_help=True)
def set_gpu(ns: str = typer.Option(..., "--namespace", "-n", prompt=True),
            enabled: bool = typer.Option(..., prompt=True)):
    pass


@app.command(no_args_is_help=True)
def set_sa_policy(ns: str = typer.Option(..., "--namespace", "-n", prompt=True),
                  arn: str = typer.Option(..., prompt=True)):
    pass


@app.command(no_args_is_help=True)
def add_fsx_volume(ns: str = typer.Option(..., "--namespace", "-n", prompt=True),
                   volume_name: str = typer.Option(..., prompt=True),
                   volume_size_in_gb: int = typer.Option(..., prompt=True),
                   volume_handle: str = typer.Option(..., prompt=True),
                   volume_dns: str = typer.Option(..., prompt=True),
                   volume_mount_name: str = typer.Option(..., prompt=True)):
    print(f"Hello {ns}")


@app.command(no_args_is_help=True)
def delete_fsx_volume(ns: str = typer.Option(..., "--namespace", "-n", prompt=True),
                      volume_name: str = typer.Option(..., prompt=True)):
    print(f"Hello {ns}")
