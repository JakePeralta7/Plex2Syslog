FROM python:3.11-slim

LABEL maintainer="Plex2Syslog"
LABEL description="Docker container to forward Plex webhooks to syslog"

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app.py .

# Create non-root user
RUN useradd -r -s /bin/false plex2syslog
USER plex2syslog

# Expose port
EXPOSE 8080

# Environment variables with defaults
ENV SYSLOG_HOST=localhost
ENV SYSLOG_PORT=514
ENV SYSLOG_FACILITY=LOCAL0
ENV LOG_LEVEL=INFO

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8080/health')"

# Run the application
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "2", "--timeout", "60", "app:app"]
