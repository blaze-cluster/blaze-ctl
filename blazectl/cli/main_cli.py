import pyfiglet
import typer

from .cluster_cli import app as cluster_app
from .job_cli import app as job_app
from .namespace_cli import app as ns_app
from .workers_cli import app as worker_app

app = typer.Typer(no_args_is_help=True)

app.add_typer(ns_app, name="namespace")
app.add_typer(cluster_app, name="cluster")
app.add_typer(job_app, name="job")
app.add_typer(worker_app, name="workers-group")

if __name__ == "__main__":
    print(pyfiglet.figlet_format("blaze"))
    app()
