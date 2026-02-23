#!/bin/bash

set -e 

echo "waiting for database..."
while ! pg_isready -h "${DB_HOST:-db}" -p "${DB_PORT:-5432}" -U "${DB_USER:-philippe}" > /dev/null 2>&1; do
  sleep 1
done
echo "Database is ready!"


echo "Running migrations..."
python manage.py migrate --noinput

echo "Starting Gunicorn..."
exec gunicorn \
    --config conf/gunicorn.conf.py \
    --workers ${GUNICORN_WORKERS:-3} \
    --worker-class ${GUNICORN_WORKER_CLASS:-sync} \
    clapp_backend.wsgi:application