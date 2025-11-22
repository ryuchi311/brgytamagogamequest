FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Allow selecting a requirements file at build time to split bot vs backend deps
ARG REQUIREMENTS_FILE=requirements-backend.txt
COPY ${REQUIREMENTS_FILE} /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Copy application code
COPY . .

# Make startup script executable
RUN chmod +x start-server.sh

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Default runtime configuration (can be overridden at runtime)
ENV HOST=0.0.0.0 \
    PORT=8080 \
    API_PORT=8000 \
    SERVE_FRONTEND=false \
    FRONTEND_DIR=frontend

# Expose primary (frontend) and API ports
EXPOSE 8080 8000

# Default command - uses startup script for Cloud Run compatibility
CMD ["./start-server.sh"]
