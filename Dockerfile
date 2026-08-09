FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --default-timeout=1000 --retries 5 --no-cache-dir -r requirements.txt

COPY . .

# Make the start script executable
RUN chmod +x /app/start.sh

EXPOSE 8000

CMD ["/app/start.sh"]