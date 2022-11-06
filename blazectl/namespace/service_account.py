def create_service_account(ns: str, eks_cluster: str, policy_arn: str):
    command = f'''eksctl create iamserviceaccount \
      --name {ns}-isra \
      --namespace {ns} \
      --cluster {eks_cluster} \
      --attach-policy-arn {policy_arn} \
      --approve'''
    pass


def delete_service_account(ns: str, eks_cluster: str):
    command = f'''eksctl delete iamserviceaccount \
      --name {ns}-isra \
      --namespace {ns} \
      --cluster {eks_cluster} \
      --approve'''
    pass
