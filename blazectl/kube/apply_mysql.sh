set +x
shopt -s nullglob

export CONTROL_APPS_NS=control-apps
export MYSQL_CLUSTER_NS=$CONTROL_APPS_NS
export MYSQL_CLUSTER_NAME=common-mysql
export MYSQL_CLUSTER_SERVICE_ACCOUNT="${EKS_CLUSTER_NAME}-${CONTROL_APPS_NS}-access-sa"
export MYSQL_CLUSTER_S3_BUCKET="${EKS_CLUSTER_NAME}-${CONTROL_APPS_NS}-data"

delete=""
while [[ $# -gt 0 ]]; do
  key="$1"
  case $key in
  --delete)
    delete="YES"
    ;;
  *)
    echo "Usage: apply_mysql.sh.sh [ --delete ]"
    exit 1
    ;;
  esac
  shift
done

if [ "$delete" == "YES" ]; then
  for f in $(ls "mysql/"* | sort -nr) ; do
    echo "${f}"
    envsubst < "${f}" | kubectl delete -f -
  done
else
  for f in $(ls "mysql/"* | sort -n) ; do
    echo "${f}"
    envsubst < "${f}" | kubectl apply -f -
  done
fi
