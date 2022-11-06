import typer
import pyfiglet

from .cluster.cli import app as cluster_cli
from .job.cli import app as job_cli
from .workers.cli import app as workers_cli


def callback():
    print(pyfiglet.figlet_format("blaze"))


app = typer.Typer(callback=callback)
app.add_typer(cluster_cli, name="cluster")
app.add_typer(job_cli, name="job")
app.add_typer(workers_cli, name="workers")
