#!/bin/bash
set -e

IMAGE_NAME="${1:-ppm}"
PORT_LAB="${2:-8888}"
PORT_VOILA="${3:-8889}"

# Run from repo root: bash dev/run.sh
docker build -f dev/Dockerfile -t "$IMAGE_NAME" .

docker stop "$IMAGE_NAME" 2>/dev/null || true
docker rm   "$IMAGE_NAME" 2>/dev/null || true

docker run --rm -d \
  -p "$PORT_LAB":8888 \
  -p "$PORT_VOILA":8889 \
  --name "$IMAGE_NAME" \
  -v "$(pwd)":/workspace:ro \
  "$IMAGE_NAME"

echo ""
echo "  Jupyter Lab  →  http://localhost:$PORT_LAB"
echo "  Voilà        →  http://localhost:$PORT_VOILA"
echo ""
