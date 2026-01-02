#!/bin/bash

set -e 

echo "waiting for database..."
while ! pg_isready -h "${DB_HOST:-cab}" -p "${DB_PORT:-5432}" -U "${DB_USER:-philippe}" > /dev/null 2>&1; do
  sleep 1
done
echo "Database is ready!"


echo "Running migrations..."
python manage.py migrate --noinput

echo "Starting Gunicorn..."
exec gunicorn \
    --bind 0.0.0.0:8000 \
    --workers ${GUNICORN_WORKERS:-3} \
    --worker-class ${GUNICORN_WORKER_CLASS:-sync} \
    --access-logfile - \
    --error-logfile - \
    circus_agent_project.wsgi:application