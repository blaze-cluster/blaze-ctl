import pyfiglet
import typer
from blazectl.commons.configuration import ConfigStoreKind, DBConfiguration, LocalConfiguration
from blazectl.commons.utils import Utils

from .cluster_cli import app as cluster_app
from .job_cli import app as job_app
from .namespace_cli import app as ns_app
from .workers_cli import app as worker_app

app = typer.Typer(no_args_is_help=True)

app.add_typer(ns_app, name="namespace")
app.add_typer(cluster_app, name="cluster")
app.add_typer(job_app, name="job")
app.add_typer(worker_app, name="workers-group")


@app.command()
def configure():
    config_store_kind = typer.prompt("Config Store Kind?", type=ConfigStoreKind, default=ConfigStoreKind.DB)

    if config_store_kind == ConfigStoreKind.DB:
        # more prompts
        db_host = typer.prompt("DB Host")
        db_port = typer.prompt("DB Port", type=int, default=3306)
        db_user = typer.prompt("DB User", default="blaze")
        db_password = typer.prompt("DB Password")
        db_name = typer.prompt("DB Name", default="blaze_cluster")

        configuration = DBConfiguration(host=db_host, port=db_port, user=db_user, password=db_password, database=db_name)

    elif config_store_kind == ConfigStoreKind.LOCAL:
        configuration = LocalConfiguration()
    else:
        print(f"ERROR: Unknown config store kind: {config_store_kind}")
        raise typer.Abort()

    Utils.save_blazectl_config(configuration)


if __name__ == "__main__":
    print(pyfiglet.figlet_format("blaze"))
    app()
