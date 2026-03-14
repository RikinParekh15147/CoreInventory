#!/bin/bash
echo "Starting deployment script for Azure Web App..."

# Run collecting static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Run migrations
echo "Running database migrations..."
python manage.py migrate --noinput

# Start Gunicorn server
echo "Starting Gunicorn server..."
gunicorn --bind=0.0.0.0 --timeout 600 --workers 4 config.wsgi:application
