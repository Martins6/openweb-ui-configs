#!/bin/bash

# Update script for OpenWebUI custom image
set -e

echo "🔄 Updating OpenWebUI custom image..."

# Stop and remove existing container
echo "⏹️  Stopping existing container..."
docker stop open-webui 2>/dev/null || true
docker rm open-webui 2>/dev/null || true

# Pull latest base image
echo "📥 Pulling latest OpenWebUI base image..."
docker pull ghcr.io/open-webui/open-webui:main

# Rebuild custom image
echo "🏗️  Rebuilding custom image..."
docker build -t open-webui-custom:latest .

# Start new container
echo "🚀 Starting updated container..."
docker run -d \
  -p 3000:8080 \
  --add-host=host.docker.internal:host-gateway \
  -v open-webui:/app/backend/data \
  -v ./functions:/app/custom-functions/functions \
  --name open-webui \
  --restart always \
  open-webui-custom:latest

echo "✅ Update complete!"
echo "🌐 OpenWebUI is available at: http://localhost:3001"

