eksctl create iamidentitymapping \
    --cluster "${EKS_CLUSTER_NAME}" \
    --region="${AWS_DEFAULT_REGION}" \
    --arn arn:aws:iam::"${AWS_ACCOUNT_ID}":user/"$USER" \
    --group "$ROLE_GROUP" \
    --no-duplicate-arns