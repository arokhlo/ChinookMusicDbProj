#!/bin/bash

echo "Starting deployment..."

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Import Chinook database tables (for PostgreSQL)
echo "Setting up Chinook database..."
python manage.py import_chinook

# Run migrations
echo "Running migrations..."
python manage.py migrate --noinput

# Create superuser if it doesn't exist (optional)
echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(username='admin').exists() or User.objects.create_superuser('admin', 'admin@example.com', 'admin123')" | python manage.py shell

echo "Deployment completed successfully!"