set +x
shopt -s nullglob

export MYSQL_CLUSTER_NS=control-apps
export MYSQL_CLUSTER_NAME=common-mysql
export MYSQL_CLUSTER_SERVICE_ACCOUNT="josh-recsys-eks-cluster-control-apps-access-sa"
export MYSQL_CLUSTER_S3_BUCKET="josh-recsys-eks-cluster-data"

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
