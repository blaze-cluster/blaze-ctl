import typer

app = typer.Typer(no_args_is_help=True)


@app.command(no_args_is_help=True)
def add(name: str = typer.Option(..., prompt=True),
        cluster_name: str = typer.Option(..., "--cluster", "-c", prompt=True),
        namespace: str = typer.Option(..., "--namespace", "-n", prompt=True),
        instance_type: str = typer.Option(..., prompt=True),
        count: int = typer.Option(0),
        gpu: bool = typer.Option(False)):
    pass


@app.command(no_args_is_help=True)
def update(name: str = typer.Option(..., prompt=True),
           cluster_name: str = typer.Option(..., "--cluster", "-c", prompt=True),
           namespace: str = typer.Option(..., "--namespace", "-n", prompt=True),
           instance_type: str = typer.Option(None, prompt=True),
           count: int = typer.Option(None),
           gpu: bool = typer.Option(None)):
    pass


@app.command(no_args_is_help=True)
def delete(name: str = typer.Option(..., prompt=True),
           cluster_name: str = typer.Option(..., "--cluster", "-c", prompt=True),
           namespace: str = typer.Option(..., "--namespace", "-n", prompt=True)):
    # deleting default means setting their count as zero
    pass


@app.command(no_args_is_help=True)
def set_replicas(name: str = typer.Option(..., prompt=True),
                 cluster_name: str = typer.Option(..., "--cluster", "-c", prompt=True),
                 namespace: str = typer.Option(..., "--namespace", "-n", prompt=True),
                 count: int = typer.Option(..., prompt=True)):
    pass
