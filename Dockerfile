FROM python:3.11-slim

WORKDIR /app

# Ensure logs output instantly (no buffering)
ENV PYTHONUNBUFFERED=1

# Set GEMINI_API_KEY at build or runtime:
#   docker run -e GEMINI_API_KEY=your_key ...
ENV GEMINI_API_KEY=""

# Install requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Cloud Run defaults to Port 8080
EXPOSE 8080

# Health check — polls /api/health every 30s (Member 3 endpoint)
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/api/health')" || exit 1

# Serve with Gunicorn (single worker, 8 threads — suitable for Cloud Run)
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 main:app
