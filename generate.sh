#!/bin/bash
set -e

# Path to frappe_docker (relative to this script)
FRAPPE_DOCKER_DIR="${FRAPPE_DOCKER_DIR:-$(cd ../frappe_docker && pwd)}"
PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
ENV_FILE="$PROJECT_DIR/.env"
OUTPUT_FILE="$PROJECT_DIR/compose.yaml"
PROJECT_NAME="${PROJECT_NAME:-bluenet}"

echo "Frappe Docker: $FRAPPE_DOCKER_DIR"
echo "Project:       $PROJECT_DIR"
echo "Env:           $ENV_FILE"
echo "Output:        $OUTPUT_FILE"
echo "Project name:  $PROJECT_NAME"
echo ""

cd "$FRAPPE_DOCKER_DIR"

docker compose --project-name "$PROJECT_NAME" \
  --env-file "$ENV_FILE" \
  -f compose.yaml \
  -f overrides/compose.mariadb.yaml \
  -f overrides/compose.redis.yaml \
  -f overrides/compose.noproxy.yaml \
  config > "$OUTPUT_FILE"

echo "Generated $OUTPUT_FILE"
