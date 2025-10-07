# Build stage for frontend
FROM node:18-alpine as frontend-builder

WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci

COPY frontend/ ./
RUN npm run build

# Production stage
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=config.settings_fly

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        postgresql-client \
        gcc \
        python3-dev \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy and install Python dependencies
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend application
COPY backend/ ./

# Copy built frontend static files
COPY --from=frontend-builder /app/frontend/dist ./staticfiles/

# Create necessary directories
RUN mkdir -p /data/staticfiles /data/media

# Collect static files
RUN python manage.py collectstatic --noinput

# Create non-root user
RUN addgroup --system --gid 1001 django \
    && adduser --system --uid 1001 --ingroup django django

# Change ownership of app directory
RUN chown -R django:django /app /data

# Switch to non-root user
USER django

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/api/health/', timeout=10)"

# Default command
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "2", "--worker-class", "gthread", "--threads", "4", "--worker-connections", "1000", "--max-requests", "1000", "--max-requests-jitter", "100", "--timeout", "120", "config.wsgi:application"]