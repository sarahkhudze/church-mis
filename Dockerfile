FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --default-timeout=1000 --retries 5 --no-cache-dir -r requirements.txt

COPY . .

# Make the entrypoint script executable
RUN chmod +x /app/entrypoint.sh

EXPOSE 8000

# Use entrypoint.sh
CMD ["/app/entrypoint.sh"]