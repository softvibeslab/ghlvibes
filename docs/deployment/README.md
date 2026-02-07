# Deployment Guide

Complete guide for deploying the GoHighLevel Clone platform to various environments.

## Table of Contents

- [Local Development](./local.md)
- [Docker Deployment](./docker.md)
- [Cloud Deployment](./cloud.md)
- [Environment Configuration](#environment-configuration)
- [CI/CD Pipeline](#cicd)
- [Monitoring](#monitoring)
- [Troubleshooting](#troubleshooting)

## Quick Start Deployments

### Docker Compose (Recommended for Local)

```bash
git clone https://github.com/your-org/gohighlevel-clone.git
cd gohighlevel-clone
docker-compose up -d
```

Services:
- Backend: `http://localhost:8000`
- Frontend: `http://localhost:3000`
- PostgreSQL: `localhost:5432`
- Redis: `localhost:6379`

### Railway (Backend)

```bash
npm install -g @railway/cli
railway login
railway init
railway up
```

### Vercel (Frontend)

```bash
npm install -g vercel
cd frontend
vercel
```

## Environment Configuration

### Backend Environment Variables

Create `.env` file in `backend/` directory:

```bash
# Application
APP_NAME=GoHighLevel Clone
APP_VERSION=1.0.0
ENVIRONMENT=development
DEBUG=true

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/gohighlevel

# Redis
REDIS_URL=redis://localhost:6379/0

# Authentication
SECRET_KEY=your-secret-key-min-32-characters
JWT_ALGORITHM=RS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=15
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8000

# External Services
SENDGRID_API_KEY=your-sendgrid-key
TWILIO_ACCOUNT_SID=your-twilio-sid
TWILIO_AUTH_TOKEN=your-twilio-token
STRIPE_SECRET_KEY=your-stripe-key

# Rate Limiting
RATE_LIMIT_PER_HOUR=100
```

### Frontend Environment Variables

Create `.env.local` file in `frontend/` directory:

```bash
# API
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000

# Authentication
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=your-clerk-key

# Feature Flags
NEXT_PUBLIC_ENABLE_ANALYTICS=true
NEXT_PUBLIC_ENABLE_BETA_FEATURES=false
```

## Docker Deployment

### Build Images

```bash
# Backend
docker build -t gohighlevel-backend ./backend

# Frontend
docker build -t gohighlevel-frontend ./frontend
```

### Run with Docker Compose

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Remove volumes
docker-compose down -v
```

### Production Docker Compose

```yaml
version: '3.8'

services:
  backend:
    image: gohighlevel-backend:latest
    environment:
      - ENVIRONMENT=production
      - DEBUG=false
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '1'
          memory: 1G
    restart: always

  frontend:
    image: gohighlevel-frontend:latest
    environment:
      - NEXT_PUBLIC_API_URL=https://api.example.com
    deploy:
      replicas: 2
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
    restart: always
```

## Cloud Deployment

### Railway (Full Stack)

1. **Create Railway Account**
   - Visit [railway.app](https://railway.app)
   - Create account and connect GitHub

2. **Deploy Backend**
   ```bash
   railway login
   railway init
   railway add postgresql
   railway add redis
   railway up
   ```

3. **Configure Environment Variables**
   - Set all backend environment variables in Railway dashboard
   - Update `DATABASE_URL` and `REDIS_URL` with Railway URLs

4. **Deploy Frontend to Vercel**
   ```bash
   cd frontend
   vercel
   ```

5. **Update Frontend Environment**
   - Set `NEXT_PUBLIC_API_URL` to Railway backend URL

### AWS (ECS + RDS)

1. **Create VPC and Security Groups**
2. **Launch RDS PostgreSQL**
   ```bash
   aws rds create-db-instance \
     --db-instance-identifier gohighlevel-db \
     --db-instance-class db.t3.micro \
     --engine postgres \
     --master-username admin \
     --master-user-password password
   ```

3. **Launch ElastiCache Redis**
   ```bash
   aws elasticache create-cache-cluster \
     --cache-cluster-id gohighlevel-redis \
     --engine redis \
     --cache-node-type cache.t3.micro
   ```

4. **Create ECS Task Definition**
   ```json
   {
     "family": "gohighlevel-backend",
     "containerDefinitions": [
       {
         "name": "backend",
         "image": "your-ecr-repo/backend:latest",
         "memory": 1024,
         "cpu": 512,
         "environment": [
           {"name": "DATABASE_URL", "value": "your-rds-url"},
           {"name": "REDIS_URL", "value": "your-redis-url"}
         ],
         "portMappings": [{"containerPort": 8000}]
       }
     ]
   }
   ```

5. **Create ECS Service and Load Balancer**

### Google Cloud (Cloud Run + Cloud SQL)

1. **Deploy Backend to Cloud Run**
   ```bash
   gcloud run deploy gohighlevel-backend \
     --image gcr.io/your-project/backend \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated
   ```

2. **Create Cloud SQL Instance**
   ```bash
   gcloud sql instances create gohighlevel-db \
     --database-version POSTGRES_16 \
     --tier db-f1-micro \
     --region us-central1
   ```

3. **Create Memorystore Redis**
   ```bash
   gcloud redis instances create gohighlevel-redis \
     --region us-central1 \
     --tier basic \
     --memory-size 1GB
   ```

## CI/CD Pipeline

### GitHub Actions

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - name: Install dependencies
        run: |
          cd backend
          pip install -e '.[dev]'
      - name: Run tests
        run: |
          cd backend
          pytest tests/ --cov=src --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v4

  deploy-backend:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Deploy to Railway
        run: |
          npm install -g @railway/cli
          railway login --token ${{ secrets.RAILWAY_TOKEN }}
          railway up
        env:
          RAILWAY_TOKEN: ${{ secrets.RAILWAY_TOKEN }}

  deploy-frontend:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Deploy to Vercel
        run: |
          npm install -g vercel
          cd frontend
          vercel --prod --token=${{ secrets.VERCEL_TOKEN }}
        env:
          VERCEL_TOKEN: ${{ secrets.VERCEL_TOKEN }}
```

## Monitoring

### Health Checks

**Backend Health Endpoint**

```bash
curl https://api.example.com/health
```

Response:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "database": "connected",
  "redis": "connected"
}
```

### Application Monitoring

1. **Logging**
   - Backend: Structured JSON logs to stdout
   - Frontend: Browser console + remote logging service

2. **Metrics**
   - Request rate and latency
   - Error rate by endpoint
   - Database query performance
   - Cache hit/miss ratio

3. **Alerting**
   - Error rate > 5%
   - Response time > 1s
   - Database connections > 80%
   - Redis memory > 90%

### Recommended Tools

- **Logging**: Sentry, LogRocket
- **Monitoring**: Datadog, New Relic
- **Uptime**: Pingdom, UptimeRobot
- **Analytics**: Google Analytics, Plausible

## Troubleshooting

### Common Issues

**1. Database Connection Failed**

```
Error: could not connect to server: Connection refused
```

**Solution**:
- Check PostgreSQL is running: `docker ps | grep postgres`
- Verify DATABASE_URL is correct
- Check network connectivity

**2. Redis Connection Error**

```
Error: Error connecting to Redis
```

**Solution**:
- Verify Redis is running: `docker ps | grep redis`
- Check REDIS_URL format
- Test connection: `redis-cli ping`

**3. CORS Errors in Browser**

```
Access to fetch at 'http://localhost:8000' has been blocked by CORS policy
```

**Solution**:
- Add frontend origin to `CORS_ORIGINS`
- Check preflight OPTIONS requests
- Verify credentials mode

**4. Rate Limiting Issues**

```
Error: Rate limit exceeded
```

**Solution**:
- Check `RATE_LIMIT_PER_HOUR` setting
- Verify Redis is working for rate limiting
- Review application usage patterns

**5. Migration Failures**

```
Error: Target database is not up to date
```

**Solution**:
```bash
# Check current version
alembic current

# Upgrade to latest
alembic upgrade head

# If stuck, stamp to specific version
alembic stamp head
```

### Debug Mode

Enable debug logging:

```bash
# Backend
export DEBUG=true
export LOG_LEVEL=debug

# Frontend
export NEXT_PUBLIC_DEBUG=true
```

### Database Reset

**Warning: This deletes all data**

```bash
# Drop and recreate database
alembic downgrade base
alembic upgrade head

# Or with Docker
docker-compose down -v
docker-compose up -d
```

## Performance Optimization

### Backend

1. **Database Connection Pooling**
   ```python
   # settings.py
   DATABASE_POOL_SIZE = 20
   DATABASE_MAX_OVERFLOW = 40
   ```

2. **Redis Connection Pool**
   ```python
   REDIS_POOL_SIZE = 50
   ```

3. **Gunicorn Workers**
   ```bash
   gunicorn src.main:app \
     --workers 4 \
     --worker-class uvicorn.workers.UvicornWorker \
     --bind 0.0.0.0:8000
   ```

### Frontend

1. **Image Optimization**
   - Use Next.js Image component
   - Enable sharp for image optimization

2. **Bundle Size**
   - Code splitting with dynamic imports
   - Tree shaking with proper imports

3. **Caching**
   - ISR for static content
   - SWR for frequently changing data

## Security Checklist

- [ ] Change default passwords
- [ ] Use strong SECRET_KEY (min 32 chars)
- [ ] Enable HTTPS only
- [ ] Set secure CORS origins
- [ ] Enable rate limiting
- [ ] Configure firewall rules
- [ ] Enable audit logging
- [ ] Regular security updates
- [ ] Environment variables not in git
- [ ] Database backups enabled

## Backup Strategy

### Database Backups

```bash
# Manual backup
pg_dump $DATABASE_URL > backup_$(date +%Y%m%d).sql

# Automated backup (cron)
0 2 * * * pg_dump $DATABASE_URL | gzip > /backups/db_$(date +\%Y\%m\%d).sql.gz
```

### Restore Backup

```bash
psql $DATABASE_URL < backup_20240101.sql
```

## Scaling Guide

### Vertical Scaling

- Increase CPU/memory allocation
- Optimize database queries
- Add database indexes

### Horizontal Scaling

- Add more application instances
- Use load balancer
- Implement database read replicas
- Use Redis cluster for cache

## Related Documentation

- [Local Development](./local.md)
- [Docker Deployment](./docker.md)
- [Cloud Deployment](./cloud.md)
- [Architecture](../architecture/system.md)
- [API Reference](../api/README.md)
