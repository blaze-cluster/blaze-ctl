import json
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
        pass

    @staticmethod
    def kubectl_delete(data):
        pass

    @staticmethod
    def run_command(command):
        output = subprocess.check_output(command, shell=True)
        print(output)

    @staticmethod
    def print_data(data: Dict):
        print(json.dumps(data, indent=2))

    @staticmethod
    def save_config(path: str, data: Dict):
        pass

    @staticmethod
    def delete_config(path: str):
        pass

    @staticmethod
    def load_config(path: str) -> Dict:
        pass
