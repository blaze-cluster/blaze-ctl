#!/bin/bash
set +x

usage() {
  echo "Usage:
          submit_job  [ -c | --cluster CLUSTER ]
                      [ -n | --namespace NAMESPACE ]
                      [ -j | --job-id JOB_ID ]
                      [ -e | --entrypoint ENTRYPOINT ]
                      [ -g | --giturl FULLY QUALIFIED GIT URL eg https://username:password@github.com/username/repository.git ]
                      [ -d | --deps EXTRA DEPENDENCIES ]
                      [ -h | --help ]"
  exit 2
}

CLUSTER=""
NAMESPACE=""
GIT_URL=""
ENTRYPOINT=""
JOB_ID=""
EXTRA_DEPS="--pip overrides --pip xxhash --pip wandb --pip mlflow --pip retry --pip importlib --pip smart_open --pip hydra-core --pip pydantic --pip hnswlib --pip s3fs"

SHORT_OPTS=c:,n:,j:,e:,g:,d::,h
LONG_OPTS=cluster:,namespace:,job-id:,entrypoint:,giturl:,deps::,help
PARSED_ARGUMENTS=$(getopt -a -n submit_job --options $SHORT_OPTS --longoptions $LONG_OPTS -- "$@")
echo "PARSED_ARGUMENTS is $PARSED_ARGUMENTS"
if [ "$PARSED_ARGUMENTS" == "--" ]; then
  usage
fi

eval set -- "$PARSED_ARGUMENTS"
while :; do
  case "$1" in
  -c | --cluster)
    CLUSTER="$2"
    shift 2
    ;;
  -n | --namespace)
    NAMESPACE="$2"
    shift 2
    ;;
  -j | --job-id)
    JOB_ID="$2"
    shift 2
    ;;
  -e | --entrypoint)
    ENTRYPOINT="$2"
    shift 2
    ;;
  -g | --giturl)
    GIT_URL="$2"
    shift 2
    ;;
  -d | --deps)
    EXTRA_DEPS="$2"
    shift 2
    ;;
  -h | --help)
    usage
    shift
    ;;
  # -- means the end of the arguments; drop this, and break out of the while loop
  --)
    shift
    break
    ;;
  # If invalid options were passed, then getopt should have reported an error,
  # which we checked as VALID_ARGUMENTS when getopt was called...
  *)
    echo "Unexpected option: $1 - this should not happen."
    usage
    ;;
  esac
done

[ -z "$GIT_URL" ] && echo "giturl arg must be passed" && exit
[ -z "$CLUSTER" ] && echo "cluster arg must be passed" && exit
[ -z "$NAMESPACE" ] && echo "namespace arg must be passed" && exit
[ -z "$ENTRYPOINT" ] && echo "entrypoint arg must be passed" && exit

rm -rf project && mkdir project
cd project || exit
git -c credential.helper='!f() { sleep 1; echo "username=${GIT_USERNAME}"; echo "password=${GIT_PASSWORD}"; }; f' clone "${GIT_URL}" . || exit

#git clone "${GIT_URL}" . || exit

blazectl job run -c "${CLUSTER}" -n "${NAMESPACE}" -j "${JOB_ID}" -e "${ENTRYPOINT}" --no-wait-for-job-end ${EXTRA_DEPS}
