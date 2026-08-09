FROM python:3.12-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --default-timeout=1000 --retries 5 --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Run migrations and conditionally create superuser using env vars
RUN python manage.py migrate --noinput && \
    if [ -n "$DJANGO_SUPERUSER_USERNAME" ] && \
       [ -n "$DJANGO_SUPERUSER_PASSWORD" ] && \
       [ -n "$DJANGO_SUPERUSER_EMAIL" ]; then \
        echo "✅ Creating superuser: $DJANGO_SUPERUSER_USERNAME"; \
        echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('$DJANGO_SUPERUSER_USERNAME', '$DJANGO_SUPERUSER_EMAIL', '$DJANGO_SUPERUSER_PASSWORD')" | python manage.py shell; \
    else \
        echo "⚠️ Skipping superuser creation — set DJANGO_SUPERUSER_USERNAME, PASSWORD, and EMAIL in Render environment variables"; \
    fi

# Expose port
EXPOSE 8000

# Start with Gunicorn (replace 'church_cms' if your project name is different)
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "church_cms.wsgi:application"]