import typer
import pyfiglet

from cluster import cli as cluster_cli
from job import cli as job_cli
from namespace import cli as ns_cli

app = typer.Typer(no_args_is_help=True)


# @app.callback(invoke_without_command=True)
# def callback():
#     print(pyfiglet.figlet_format("blaze"))


app.add_typer(ns_cli.app, name="namespace")
app.add_typer(cluster_cli.app, name="cluster")
app.add_typer(job_cli.app, name="job")
# app.add_typer(workers_cli, name="workers")

if __name__ == "__main__":
    print(pyfiglet.figlet_format("blaze"))
    app()
