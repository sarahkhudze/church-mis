FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

# Increase timeout and add retries
RUN pip install --default-timeout=1000 --retries 5 --no-cache-dir -r requirements.txt

COPY . .

# Expose port
EXPOSE 8000

# Use Gunicorn instead of Django's development server
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "church_cms.wsgi:application"]