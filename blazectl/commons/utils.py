import json
import subprocess


# envsubst < ~/icloud/ws/cluster_config/eks/ray/cluster/ray_cluster_latest.yaml | kubectl apply -f -
#
# print(subprocess.check_output(['ls', '-l']))
# output = subprocess.check_output("eksctl create -f managedcluster.yaml", shell=True)

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
    def print_data(data):
        print(json.dumps(data, indent=2))
