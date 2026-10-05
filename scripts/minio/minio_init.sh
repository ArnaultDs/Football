#!/bin/sh
set -e

echo "Waiting for MinIO to be ready ..."
mc alias set local "http://minio:9000" "$MINIO_ROOT_USER" "$MINIO_ROOT_PASSWORD"

echo "Creating buckets ..."
mc mb --ignore-existing "local/$MINIO_BRONZE_BUCKET"
mc mb --ignore-existing "local/$MINIO_SILVER_BUCKET"

echo "Applying policy ..."
mc admin policy create local pipelines-shared-policy /scripts/pipelines-shared-policies.json

echo "Creating shared pipeline user ..."
if mc admin user info local "$MINIO_PIPELINE_USER" >/dev/null 2>&1; then
    echo "User $MINIO_PIPELINE_USER already exists, skipping creation."
else
    mc admin user add local "$MINIO_PIPELINE_USER" "$MINIO_PIPELINE_PASSWORD" 
fi 

mc admin policy attach local pipelines-shared-policy --user "$MINIO_PIPELINE_USER"

echo "Creating service account ..."
if mc admin user svcacct info local "$MINIO_PIPELINE_ACCESS_KEY" >/dev/null 2>&1; then 
    echo "Service account $MINIO_PIPELINE_ACCESS_KEY already exists, skipping creation."
else
    mc admin user svcacct add local "$MINIO_PIPELINE_USER" \
        --access-key "$MINIO_PIPELINE_ACCESS_KEY" \
        --secret-key "$MINIO_PIPELINE_SECRET_KEY"
fi 

echo "✅ Init MinIO successfully finished"