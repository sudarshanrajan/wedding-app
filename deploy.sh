#!/bin/bash

set -e

APP_NAME="wedding-app"

echo "🔍 Stopping and removing existing containers..."
docker ps -a --filter "name=$APP_NAME" --format "{{.ID}}" | xargs -r docker stop
docker ps -a --filter "name=$APP_NAME" --format "{{.ID}}" | xargs -r docker rm

echo "🧹 Removing existing image..."
docker images --format "{{.Repository}}:{{.Tag}} {{.ID}}" | grep "^$APP_NAME" | awk '{print $2}' | xargs -r docker rmi

echo "🔨 Building fresh image..."
docker build -t $APP_NAME .

echo "🚀 Running container..."
docker run -d \
  --name $APP_NAME \
  --network host \
  -v "$PWD/data:/app/data" \
  -v "$PWD/static:/app/static" \
  $APP_NAME

