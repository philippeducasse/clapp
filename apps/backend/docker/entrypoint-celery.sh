#!/bin/bash

set -e

echo "waiting for database..."
while ! pg_isready -h "${DB_HOST:-db}" -p "${DB_PORT:-5432}" -U "${DB_USER:-philippe}" > /dev/null 2>&1; do
  sleep 1
done
echo "Database is ready!"

# Run the celery command passed as arguments
exec "$@"