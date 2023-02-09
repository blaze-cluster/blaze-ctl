set +x

USER=""
GROUP=""
while [[ $# -gt 0 ]]; do
  key="$1"
  case $key in
  --user)
    shift
    USER=$1
    ;;
  --group)
    shift
    GROUP=$1
    ;;
  *)
    echo "Usage: user.sh --user <user-name> --group <role-group>"
    exit 1
    ;;
  esac
  shift
done

if [ "$USER" == "" ]; then
  echo "Usage: user.sh --user <user-name> --group <role-group>"
  exit 1
fi

if [ "$GROUP" == "" ]; then
  echo "Usage: user.sh --user <user-name> --group <role-group>"
  exit 1
fi

eksctl delete iamidentitymapping --all \
    --cluster "${EKS_CLUSTER_NAME}" \
    --region="${AWS_DEFAULT_REGION}" \
    --arn arn:aws:iam::"${AWS_ACCOUNT_ID}":user/"$USER"