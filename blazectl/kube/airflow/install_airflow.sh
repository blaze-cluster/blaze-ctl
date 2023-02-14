helm repo update
envsubst < airflow_git_sync_secret.yaml | kubectl apply -n control-apps-airflow -f -
envsubst < airflow_overwrite.yaml | helm upgrade --install airflow apache-airflow/airflow --namespace control-apps-airflow --create-namespace -f -
