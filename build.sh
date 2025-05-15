#!/bin/bash

set -e

APP_NAME="wedding-app"

>&2 echo "🔍 Stopping and removing existing containers..."
docker ps -a --filter "name=$APP_NAME" --format "{{.ID}}" | xargs -r docker stop >&2
docker ps -a --filter "name=$APP_NAME" --format "{{.ID}}" | xargs -r docker rm >&2

>&2 echo "🧹 Removing existing image..."
docker images --format "{{.Repository}}:{{.Tag}} {{.ID}}" | grep "^$APP_NAME" | awk '{print $2}' | xargs -r docker rmi >&2

>&2 echo "🔨 Building fresh image..."
docker build -t $APP_NAME . >&2

>&2 echo "🚀 Running container..."
container_id=$(docker run -d \
  --name $APP_NAME \
  --network host \
  --env-file .env \
  -v "$PWD/data:/app/data" \
  -v "$PWD/static:/app/static" \
  $APP_NAME)

# Only output container ID to stdout
echo "$container_id"
