FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

# Increase timeout and add retries
RUN pip install --default-timeout=1000 --retries 5 --no-cache-dir -r requirements.txt

COPY . .

# Run migrations
RUN python manage.py migrate --noinput

# Create superuser if environment variables are provided
RUN if [ -n "$DJANGO_SUPERUSER_USERNAME" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ] && [ -n "$DJANGO_SUPERUSER_EMAIL" ]; then \
    python manage.py createsuperuser --no-input; \
    fi

# Expose port
EXPOSE 8000

# Use Gunicorn instead of Django's development server
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "church_cms.wsgi:application"]