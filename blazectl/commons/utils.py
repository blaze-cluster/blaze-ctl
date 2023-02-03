import json
import os
import subprocess
from typing import Dict
from pathlib import Path

import mysql.connector
import typer
from mysql.connector import MySQLConnection

from blazectl.commons import configuration
from blazectl.commons.configuration import Configuration, DBConfiguration

BLAZECTL_CONFIG_DIR = ".blazectl"
BLAZECTL_CONFIG_PATH = "config"


# TODO: support dry-run
class Utils:
    @staticmethod
    def kubectl_apply(data):
        Utils.kubectl_data_command("apply", data)

    @staticmethod
    def kubectl_delete(data):
        Utils.kubectl_data_command("delete", data)

    @staticmethod
    def kubectl_data_command(command, data):
        spec = json.dumps(data)

        kubectl = subprocess.Popen(f"kubectl {command} -f -",
                                   stdin=subprocess.PIPE,
                                   shell=True)
        kubectl.communicate(spec.encode('utf-8'))
        while kubectl.returncode is None:
            kubectl.poll()

        # TODO: do this only if global debug field is set
        # if kubectl.returncode != 0:
        #     print("Input:")
        #     print(json.dumps(data, indent=2))

    @staticmethod
    def run_command(command):
        output = subprocess.check_output(command, shell=True)
        print(output.decode('utf-8').rstrip())

    @staticmethod
    def connect_db(cfg: DBConfiguration) -> MySQLConnection:
        return mysql.connector.connect(
            host=cfg.host,
            port=cfg.port,
            user=cfg.user,
            password=cfg.password,
            database=cfg.database
        )

    @staticmethod
    def local_config_path(path):
        config_dir = Path.home() / BLAZECTL_CONFIG_DIR
        os.makedirs(config_dir, exist_ok=True)

        local_config_path = config_dir / f"{path}.json"

        return local_config_path

    @staticmethod
    def load_config_local(path: str) -> Dict:
        with open(Utils.local_config_path(path), 'r') as openfile:
            # Reading from json file
            json_object = json.load(openfile)
            return json_object

    @staticmethod
    def load_config_db(path: str, cfg: DBConfiguration) -> Dict:
        db = None
        try:
            db = Utils.connect_db(cfg)
            cursor = db.cursor()

            cursor.execute("SELECT data FROM configs where id = %s", (path,))
            result = cursor.fetchone()
            if result is not None:
                (data,) = result
                return json.loads(data)

            print(f"ERROR: No config found for {path}")
            raise typer.Abort()
        finally:
            if db is not None:
                db.close()

    @staticmethod
    def load_config(path: str) -> Dict:
        cfg = Utils.load_blazectl_config()
        if isinstance(cfg, DBConfiguration):
            return Utils.load_config_db(path, cfg)
        else:
            return Utils.load_config_local(path)

    @staticmethod
    def load_blazectl_config() -> Configuration:
        data = Utils.load_config_local(BLAZECTL_CONFIG_PATH)
        return configuration.get_instance(data)

    @staticmethod
    def save_config_local(path: str, data: Dict):
        json_object = json.dumps(data, indent=2)
        with open(Utils.local_config_path(path), "w") as outfile:
            outfile.write(json_object)

    @staticmethod
    def save_config_db(path: str, data: Dict, configuration: DBConfiguration):
        db = None
        try:
            db = Utils.connect_db(configuration)
            cursor = db.cursor()

            json_object = json.dumps(data)
            sql = "INSERT INTO configs (id, data) VALUES (%s, %s)"
            val = (path, json_object)
            cursor.execute(sql, val)

            db.commit()
        finally:
            if db is not None:
                db.close()

    @staticmethod
    def save_config(path: str, data: Dict):
        cfg = Utils.load_blazectl_config()
        print("Configuration: ", cfg)
        if isinstance(cfg, DBConfiguration):
            Utils.save_config_db(path, data, cfg)
        else:
            Utils.save_config_local(path, data)

    @staticmethod
    def save_blazectl_config(configuration: Configuration):
        Utils.save_config_local(BLAZECTL_CONFIG_PATH, configuration.dict())

    @staticmethod
    def delete_config_local(path: str):
        os.remove(Utils.local_config_path(path))

    @staticmethod
    def delete_config_db(path: str, configuration: DBConfiguration):
        db = None
        try:
            db = Utils.connect_db(configuration)
            cursor = db.cursor()

            sql = "DELETE FROM configs WHERE id = %s"
            cursor.execute(sql, (path,))

            db.commit()
        finally:
            if db is not None:
                db.close()

    @staticmethod
    def delete_config(path: str):
        cfg = Utils.load_blazectl_config()
        if isinstance(cfg, DBConfiguration):
            Utils.delete_config_db(path, cfg)
        else:
            Utils.delete_config_local(path)
