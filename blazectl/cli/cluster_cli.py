import typer

app = typer.Typer(no_args_is_help=True)


@app.command(no_args_is_help=True)
def create(name: str = typer.Option(..., prompt=True),
           namespace: str = typer.Option(..., "--namespace", "-n", prompt=True),
           head_instance_type: str = typer.Option(None),
           default_workers_instance_type: str = typer.Option(None),
           default_workers_count: int = typer.Option(0)):
    print(f"Hello {name}")


@app.command(no_args_is_help=True)
def delete(name: str = typer.Option(..., prompt=True),
           namespace: str = typer.Option(..., "--namespace", "-n", prompt=True)):
    print(f"Bye {name}!")


@app.command(no_args_is_help=True)
def restart(name: str = typer.Option(..., prompt=True),
            namespace: str = typer.Option(..., "--namespace", "-n", prompt=True)):
    print(f"Bye {name}!")
