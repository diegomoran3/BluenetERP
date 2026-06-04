#!/bin/bash
set -e

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
ENV_FILE="$PROJECT_DIR/.env"
COMPOSE_FILE="$PROJECT_DIR/compose.yaml"
PROJECT_NAME="bluenet"
SITE_NAME="localhost"
ADMIN_PASSWORD="admin"

load_env() {
  while IFS='=' read -r key value; do
    [[ -z "$key" || "$key" =~ ^# ]] && continue
    export "$key=$value"
  done < "$ENV_FILE"
}

load_env

echo "=== Regenerating compose.yaml ==="
"$PROJECT_DIR/generate.sh"

echo ""
echo "=== Pulling images ==="
docker compose -p "$PROJECT_NAME" -f "$COMPOSE_FILE" pull

echo ""
echo "=== Starting containers ==="
docker compose -p "$PROJECT_NAME" -f "$COMPOSE_FILE" up -d --remove-orphans

echo ""
echo "=== Waiting for MariaDB ==="
until docker compose -p "$PROJECT_NAME" -f "$COMPOSE_FILE" exec -T db \
  mariadb-admin ping --silent 2>/dev/null; do
  sleep 2
done
echo "MariaDB is ready."

echo ""
echo "=== Waiting for backend (gunicorn) ==="
echo "(this may take a minute)"
until docker compose -p "$PROJECT_NAME" -f "$COMPOSE_FILE" exec -T backend \
  bench --version >/dev/null 2>&1; do
  sleep 3
done
echo "Backend is ready."

echo ""
echo "=== Creating site: $SITE_NAME ==="
if docker compose -p "$PROJECT_NAME" -f "$COMPOSE_FILE" exec -T backend \
  test -d "sites/$SITE_NAME" 2>/dev/null; then
  echo "Site '$SITE_NAME' already exists, skipping."
else
  docker compose -p "$PROJECT_NAME" -f "$COMPOSE_FILE" exec -T backend \
    bench new-site \
      --mariadb-user-host-login-scope=% \
      --db-root-password "$DB_PASSWORD" \
      --install-app erpnext \
      --admin-password "$ADMIN_PASSWORD" \
      "$SITE_NAME"
  echo "Site '$SITE_NAME' created."
fi

echo ""
echo "===================================="
echo "  ERPNext is running!"
echo "  URL:      http://localhost:$HTTP_PUBLISH_PORT"
echo "  Username: Administrator"
echo "  Password: $ADMIN_PASSWORD"
echo "===================================="
