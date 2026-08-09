FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

# Increase timeout and add retries
RUN pip install --default-timeout=1000 --retries 5 --no-cache-dir -r requirements.txt

COPY . .

# Run migrations on first start (only once!)
RUN python manage.py migrate --noinput

# Expose port
EXPOSE 8000

# Use Gunicorn instead of Django's development server
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "church_cms.wsgi:application"]