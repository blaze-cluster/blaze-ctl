import json
import os
import subprocess
from typing import Dict
from pathlib import Path


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

        if kubectl.returncode != 0:
            print("Input:")
            print(json.dumps(data, indent=2))

    @staticmethod
    def run_command(command):
        output = subprocess.check_output(command, shell=True)
        print(output.decode('utf-8').rstrip())

    @staticmethod
    def config_path(path):
        config_dir = Path.home() / ".blazectl"
        os.makedirs(config_dir, exist_ok=True)

        config_path = config_dir / f"{path}.json"

        return config_path

    @staticmethod
    def save_config(path: str, data: Dict):
        json_object = json.dumps(data, indent=2)
        with open(Utils.config_path(path), "w") as outfile:
            outfile.write(json_object)

    @staticmethod
    def delete_config(path: str):
        os.remove(Utils.config_path(path))

    @staticmethod
    def load_config(path: str) -> Dict:
        with open(Utils.config_path(path), 'r') as openfile:
            # Reading from json file
            json_object = json.load(openfile)
            return json_object
