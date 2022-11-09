import json
import os
import subprocess
from typing import Dict


# envsubst < ~/icloud/ws/cluster_config/eks/ray/cluster/ray_cluster_latest.yaml | kubectl apply -f -
#
# print(subprocess.check_output(['ls', '-l']))
# output = subprocess.check_output("eksctl create -f managedcluster.yaml", shell=True)

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

    @staticmethod
    def run_command(command):
        output = subprocess.check_output(command, shell=True)
        print(output.decode('utf-8').rstrip())

    @staticmethod
    def save_config(path: str, data: Dict):
        json_object = json.dumps(data, indent=4)

        # Writing to sample.json
        with open(f"{path}.json", "w") as outfile:
            outfile.write(json_object)

    @staticmethod
    def delete_config(path: str):
        os.remove(f"{path}.json")

    @staticmethod
    def load_config(path: str) -> Dict:
        with open(f'{path}.json', 'r') as openfile:
            # Reading from json file
            json_object = json.load(openfile)
            return json_object
