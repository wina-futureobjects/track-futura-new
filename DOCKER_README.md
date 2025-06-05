# Docker Setup for Track-Futura

This document provides instructions for running Track-Futura using Docker containers.

## Prerequisites

- Docker Engine 20.10 or later
- Docker Compose V2 or later
- At least 4GB of available RAM
- At least 10GB of available disk space

## Quick Start

### Production Setup

1. **Build and run all services:**
   ```bash
   docker-compose up -d
   ```

2. **Access the application:**
   - Frontend: http://localhost (port 80)
   - Backend API: http://localhost:8000
   - Django Admin: http://localhost:8000/admin

3. **Create a superuser:**
   ```bash
   docker-compose exec backend python manage.py createsuperuser
   ```

### Development Setup

1. **Run development environment with hot reload:**
   ```bash
   docker-compose -f docker-compose.dev.yml up -d
   ```

2. **Access the application:**
   - Frontend: http://localhost:3000 (Vite dev server)
   - Backend API: http://localhost:8000 (Django dev server)

## Services Overview

### Production (`docker-compose.yml`)

- **frontend**: React app served by Nginx (Port 80)
- **backend**: Django API with Gunicorn (Port 8000)
- **db**: PostgreSQL database (Port 5432)
- **redis**: Redis for caching (Port 6379)

### Development (`docker-compose.dev.yml`)

- **frontend**: React app with Vite dev server (Port 3000)
- **backend**: Django with development server (Port 8000)
- Uses SQLite database (no separate DB container)

## Environment Variables

Create a `.env` file in the root directory with the following variables:

```env
# Django Settings
DEBUG=0
SECRET_KEY=your-super-secret-key-change-this-in-production
ALLOWED_HOSTS=localhost,127.0.0.1,frontend,backend

# Database (PostgreSQL for production)
POSTGRES_DB=track_futura
POSTGRES_USER=track_futura_user
POSTGRES_PASSWORD=track_futura_password

# Redis
REDIS_URL=redis://redis:6379/0

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:80

# React
REACT_APP_API_URL=http://localhost:8000/api

# BrightData
BRIGHTDATA_API_KEY=your-brightdata-api-key
```

## Common Commands

### Building Images

```bash
# Build all images
docker-compose build

# Build specific service
docker-compose build backend

# Build without cache
docker-compose build --no-cache
```

### Managing Services

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Restart a service
docker-compose restart backend
```

### Database Operations

```bash
# Run migrations
docker-compose exec backend python manage.py migrate

# Create superuser
docker-compose exec backend python manage.py createsuperuser

# Load demo data
docker-compose exec backend python manage.py loaddata demo_data.json

# Access PostgreSQL shell
docker-compose exec db psql -U track_futura_user -d track_futura

# Backup database
docker-compose exec db pg_dump -U track_futura_user track_futura > backup.sql
```

### Frontend Operations

```bash
# Install new npm package
docker-compose exec frontend npm install package-name

# Run frontend tests
docker-compose exec frontend npm test

# Build production assets
docker-compose exec frontend npm run build
```

### Backend Operations

```bash
# Install new Python package
docker-compose exec backend pip install package-name

# Run Django shell
docker-compose exec backend python manage.py shell

# Run tests
docker-compose exec backend python manage.py test

# Collect static files
docker-compose exec backend python manage.py collectstatic
```

## Volume Management

### Data Volumes

- `postgres_data`: PostgreSQL database files
- `redis_data`: Redis persistence files
- `static_volume`: Django static files
- `media_volume`: User uploaded files

### Backup Volumes

```bash
# Backup volumes
docker run --rm -v track_futura_postgres_data:/data -v $(pwd):/backup alpine tar czf /backup/postgres_backup.tar.gz /data

# Restore volumes
docker run --rm -v track_futura_postgres_data:/data -v $(pwd):/backup alpine tar xzf /backup/postgres_backup.tar.gz -C /
```

## Networking

All services run on the `track_futura_network` network and can communicate using service names:

- Backend accessible at `http://backend:8000`
- Database accessible at `db:5432`
- Redis accessible at `redis:6379`

## Troubleshooting

### Common Issues

1. **Port conflicts:**
   ```bash
   # Check what's using the port
   netstat -tulpn | grep :8000
   
   # Change ports in docker-compose.yml if needed
   ```

2. **Permission issues:**
   ```bash
   # Fix file permissions
   sudo chown -R $USER:$USER .
   ```

3. **Database connection issues:**
   ```bash
   # Check database service status
   docker-compose ps db
   
   # View database logs
   docker-compose logs db
   ```

4. **Memory issues:**
   ```bash
   # Check Docker memory usage
   docker stats
   
   # Increase Docker memory limit in Docker Desktop settings
   ```

### Logs and Debugging

```bash
# View all service logs
docker-compose logs

# Follow logs in real-time
docker-compose logs -f

# View specific service logs
docker-compose logs backend
docker-compose logs frontend

# View last 100 lines
docker-compose logs --tail=100 backend
```

### Performance Optimization

1. **Use multi-stage builds** (already implemented)
2. **Optimize image layers** (already implemented)
3. **Use .dockerignore** (already implemented)
4. **Enable BuildKit:**
   ```bash
   export DOCKER_BUILDKIT=1
   docker-compose build
   ```

## Security Considerations

1. **Change default passwords** in production
2. **Use environment variables** for sensitive data
3. **Enable HTTPS** with reverse proxy (Nginx, Traefik)
4. **Regular security updates:**
   ```bash
   docker-compose pull
   docker-compose up -d
   ```

## Production Deployment

For production deployment, consider:

1. **Use Docker Swarm or Kubernetes**
2. **Implement proper logging** (ELK stack, Fluentd)
3. **Add monitoring** (Prometheus, Grafana)
4. **Use external database** (AWS RDS, Google Cloud SQL)
5. **Implement backup strategy**
6. **Use secrets management** (Docker secrets, HashiCorp Vault)

## Additional Resources

- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Django Docker Best Practices](https://docs.docker.com/language/python/best-practices/)
- [React Docker Deployment](https://create-react-app.dev/docs/deployment/) 