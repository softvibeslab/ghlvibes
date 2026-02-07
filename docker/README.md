# Docker Setup for GoHighLevel Clone

This directory contains Docker configurations for running the GoHighLevel Clone locally.

## Quick Start

### Prerequisites
- Docker Desktop (Mac/Windows) or Docker Engine (Linux)
- 4GB RAM minimum
- 10GB disk space

### Running All Services

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down
```

### Running Individual Services

```bash
# Backend only
docker-compose up -d backend postgres redis

# Frontend only
docker-compose up -d frontend

# With Celery worker
docker-compose --profile with-celery up -d
```

## Services

### Backend API
- **URL**: http://localhost:8000
- **Health Check**: http://localhost:8000/health
- **API Docs**: http://localhost:8000/docs

### Frontend
- **URL**: http://localhost:3000
- **Health Check**: http://localhost:3000

### PostgreSQL
- **Host**: localhost:5432
- **Database**: gohighlevel
- **Username**: gohighlevel
- **Password**: gohighlevel

### Redis
- **Host**: localhost:6379

## Development Workflow

### Hot Reloading

The backend and frontend support hot reloading during development:

```bash
# Backend changes are reflected automatically
# Frontend changes are reflected automatically

# View logs for a specific service
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Database Migrations

```bash
# Run migrations in the backend container
docker-compose exec backend alembic upgrade head

# Create a new migration
docker-compose exec backend alembic revision --autogenerate -m "description"
```

### Entering Containers

```bash
# Backend shell
docker-compose exec backend bash

# Frontend shell
docker-compose exec frontend sh

# PostgreSQL psql
docker-compose exec postgres psql -U gohighlevel -d gohighlevel

# Redis CLI
docker-compose exec redis redis-cli
```

## Troubleshooting

### Port Conflicts

If ports are already in use, modify the ports in docker-compose.yml:

```yaml
ports:
  - "8001:8000"  # Change backend port
```

### Database Connection Issues

```bash
# Check if PostgreSQL is healthy
docker-compose ps postgres

# View PostgreSQL logs
docker-compose logs postgres

# Restart database
docker-compose restart postgres
```

### Clearing Everything

```bash
# Stop and remove all containers, volumes, and images
docker-compose down -v --rmi all

# Rebuild from scratch
docker-compose build --no-cache
docker-compose up -d
```

## Production Deployment

For production deployment, refer to:
- Backend: Railway (see railway.toml)
- Frontend: Vercel (see vercel.json)
- CI/CD: `.github/workflows/ci-cd.yml`

## Security Notes

**NEVER commit these files to version control:**
- `.env` files with real credentials
- Database backups
- SSL certificates

**ALWAYS change default credentials in production**
