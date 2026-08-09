#!/bin/bash

# Run migrations
python manage.py migrate --noinput

# Create superuser if env vars are provided
if [[ -n "$DJANGO_SUPERUSER_USERNAME" ]] && [[ -n "$DJANGO_SUPERUSER_PASSWORD" ]] && [[ -n "$DJANGO_SUPERUSER_EMAIL" ]]; then
    echo "Creating superuser..."
    python manage.py createsuperuser --no-input || true
fi

# Create admin user (staff) if env vars are provided
if [[ -n "$DJANGO_ADMIN_USERNAME" ]] && [[ -n "$DJANGO_ADMIN_PASSWORD" ]] && [[ -n "$DJANGO_ADMIN_EMAIL" ]]; then
    echo "Creating admin user..."
    python manage.py shell << EOF
from django.contrib.auth import get_user_model
User = get_user_model()
username = "$DJANGO_ADMIN_USERNAME"
if not User.objects.filter(username=username).exists():
    User.objects.create_user(
        username=username,
        email="$DJANGO_ADMIN_EMAIL",
        password="$DJANGO_ADMIN_PASSWORD",
        is_staff=True,
        is_superuser=False
    )
    print(f"Admin user '{username}' created successfully!")
else:
    print(f"Admin user '{username}' already exists.")
EOF
fi

# Start gunicorn
exec gunicorn --bind 0.0.0.0:8000 church_cms.wsgi:application