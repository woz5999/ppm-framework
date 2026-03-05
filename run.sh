#!/bin/bash
set -e

IMAGE_NAME="${1:-ppm}"
PORT="${2:-8888}"

docker build -t "$IMAGE_NAME" .
echo "Building Docker image '$IMAGE_NAME' completed."

docker stop "$IMAGE_NAME" 2>/dev/null || true
doker rm "$IMAGE_NAME" 2>/dev/null || true
docker run --rm -d -p "$PORT":8888 --name "$IMAGE_NAME" \
  -v "$(pwd)":/workspace:ro \
  "$IMAGE_NAME"

echo "Jupyter Lab is running at http://localhost:$PORT"
