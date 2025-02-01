#!/bin/bash

# Wait for the database to be ready
echo "Waiting for the database..."
while ! nc -z db ${DB_PORT:-5432}; do
  sleep 0.1
done
echo "Database ready!"

# Apply migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Execute the specified command
exec "$@" 