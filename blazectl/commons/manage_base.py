import json
import subprocess


# envsubst < ~/icloud/ws/cluster_config/eks/ray/cluster/ray_cluster_latest.yaml | kubectl apply -f -
# subprocess.check_output(['ls', '-l'])  # All that is technically needed...
# print(subprocess.check_output(['ls', '-l']))
# output = subprocess.check_output("eksctl create -f managedcluster.yaml", shell=True)

class ManagerBase:
    def __init__(self):
        pass

    def kubectl_apply(self, data):
        pass

    def kubectl_delete(self, data):
        pass

    @staticmethod
    def print_data(data):
        print(json.dumps(data, indent=2))
