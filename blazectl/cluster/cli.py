import typer

app = typer.Typer(no_args_is_help=True)


@app.command()
def create(name: str,
           ns: str,
           head_instance_type: str = None,
           default_worker_instance_type: str = None):
    print(f"Hello {name}")


@app.command()
def add_workers():
    pass


@app.command()
def delete_workers():
    # deleting default means setting their count as zero
    pass


def set_workers_replicas():
    # deleting default means setting their count as zero
    pass


@app.command()
def delete(name: str, ns: str):
    print(f"Bye {name}!")
