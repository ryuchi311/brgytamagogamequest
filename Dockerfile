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

# Expose port (Cloud Run uses PORT env variable, defaults to 8080)
EXPOSE 8080

# Default command - uses startup script for Cloud Run compatibility
CMD ["./start-server.sh"]
