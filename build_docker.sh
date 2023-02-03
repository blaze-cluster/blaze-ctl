set -x
REPOSITORY="recsys/blazectl"
IMAGE="docker"
TAG="latest"
AWS_REGION="ap-south-1"
AWS_ACCOUNT_ID="$(aws sts get-caller-identity --query Account --output text)"
IMAGE_REPOSITORY_PATH="${REPOSITORY}":"${TAG}"
ECR_ADDR="${AWS_ACCOUNT_ID}".dkr.ecr."${AWS_REGION}".amazonaws.com
ECR_IMAGE_PATH="${ECR_ADDR}"/"${REPOSITORY}":"${TAG}"


while [[ $# -gt 0 ]]; do
  key="$1"
  case $key in
  --tag)
    shift
    TAG=$1
    ;;
  --repository)
    shift
    REPOSITORY=$1
    ;;
  --image)
    shift
    IMAGE=$1
    ;;
  --region)
    shift
    AWS_REGION=$1
    ;;
  *)
    echo "Usage: build.sh --image <image name> --repository <repository name> [--tag <tag name, default latest>] [--region <aws region name, default ap-south-1>]"
    exit 1
    ;;
  esac
  shift
done

if [ "$IMAGE" == "" ]; then
  echo "Unknown $IMAGE."
  exit 1
fi

if [ "$REPOSITORY" == "" ]; then
  echo "Unknown $REPOSITORY."
  exit 1
fi

docker build -t "${IMAGE_REPOSITORY_PATH}" "${IMAGE}"/
docker tag "${IMAGE_REPOSITORY_PATH}" "${ECR_IMAGE_PATH}"
aws ecr get-login-password --region "${AWS_REGION}" | docker login --username AWS --password-stdin "${ECR_ADDR}"
docker push "${ECR_IMAGE_PATH}"

echo "$ECR_IMAGE_PATH"