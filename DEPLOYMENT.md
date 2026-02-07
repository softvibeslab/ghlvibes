# Deployment Guide for GoHighLevel Clone

Complete guide for deploying GoHighLevel Clone to production.

## Table of Contents

- [Architecture Overview](#architecture-overview)
- [Prerequisites](#prerequisites)
- [Platform Setup](#platform-setup)
- [Environment Configuration](#environment-configuration)
- [Deployment Process](#deployment-process)
- [Monitoring and Health Checks](#monitoring-and-health-checks)
- [Rollback Procedures](#rollback-procedures)
- [Troubleshooting](#troubleshooting)

## Architecture Overview

### Deployment Architecture

```
┌─────────────────┐      ┌─────────────────┐
│   Vercel (CDN)  │────▶│  Next.js App    │
│  Frontend       │      │  (Edge Functions)│
└─────────────────┘      └────────┬────────┘
                                  │
                                  ▼
                         ┌─────────────────┐
                         │  Railway API     │
                         │  (FastAPI)       │
                         └────────┬────────┘
                                  │
                    ┌─────────────┼─────────────┐
                    ▼             ▼             ▼
            ┌───────────┐  ┌───────────┐  ┌───────────┐
            │PostgreSQL │  │  Redis    │  │ Celery    │
            │(Railway)  │  │(Railway)  │  │ Workers   │
            └───────────┘  └───────────┘  └───────────┘
```

### Platform Selection Rationale

**Backend - Railway**
- Container-based deployment (Docker)
- Managed PostgreSQL and Redis
- Private networking
- Auto-scaling
- Zero-downtime deployments

**Frontend - Vercel**
- Next.js optimization
- Edge Functions
- Global CDN
- Preview deployments
- Automatic SSL

## Prerequisites

### Required Accounts

1. **Railway Account** (Backend & Database)
   - Sign up at https://railway.app
   - Add payment method (free tier available)
   - Install Railway CLI: `npm install -g @railway/cli`

2. **Vercel Account** (Frontend)
   - Sign up at https://vercel.com
   - Connect GitHub account
   - Install Vercel CLI: `npm install -g vercel`

3. **GitHub Account** (CI/CD)
   - Enable GitHub Actions
   - Configure repository secrets

### Required Secrets

Configure these in GitHub repository settings (Settings → Secrets and variables → Actions):

```
RAILWAY_TOKEN=your-railway-token
VERCEL_TOKEN=your-vercel-token
VERCEL_ORG_ID=your-vercel-org-id
VERCEL_PROJECT_ID=your-vercel-project-id
GITHUB_TOKEN=automatic
```

## Platform Setup

### Step 1: Railway Setup (Backend)

#### 1.1 Create Railway Project

```bash
# Login to Railway
railway login

# Initialize project
railway init

# Link to existing project
railway link
```

#### 1.2 Create Services

```bash
# Create PostgreSQL database
railway add postgres

# Create Redis cache
railway add redis

# Create backend service (from current directory)
railway up
```

#### 1.3 Configure Environment Variables

In Railway dashboard or via CLI:

```bash
# Set environment variables
railway variables set SECRET_KEY=your-production-secret-key
railway variables set ENVIRONMENT=production
railway variables set DEBUG=false
```

Railway automatically provides:
- `DATABASE_URL` (PostgreSQL connection)
- `REDIS_URL` (Redis connection)
- `RAILWAY_PRIVATE_DOMAIN` (Private networking)

#### 1.4 Configure Deploy Settings

Edit `railway.toml`:

```toml
[deploy]
healthcheckPath = "/health"
restartPolicyType = "ON_FAILURE"
numReplicas = 1

[deploy.scaling]
minReplicas = 1
maxReplicas = 5
targetCPUUtilization = 70
```

#### 1.5 Deploy Backend

```bash
# Deploy to Railway
railway up

# View deployment status
railway status

# View logs
railway logs

# Get deployment URL
railway domain
```

### Step 2: Vercel Setup (Frontend)

#### 2.1 Create Vercel Project

```bash
# Install Vercel CLI
npm install -g vercel

# Login to Vercel
vercel login

# Deploy to Vercel (interactive)
cd frontend
vercel

# Deploy to production
vercel --prod
```

#### 2.2 Configure Environment Variables

In Vercel dashboard or via CLI:

```bash
# Set environment variable
vercel env add NEXT_PUBLIC_API_URL production

# Use your Railway backend URL
# Value: https://your-backend.railway.app
```

#### 2.3 Configure vercel.json

The `vercel.json` file is already configured with:
- Framework detection (Next.js)
- Build commands
- Environment variables
- Security headers
- Regional deployment

#### 2.3 Deploy Frontend

```bash
# Deploy frontend
cd frontend
vercel --prod

# Get deployment URL
vercel ls
```

### Step 3: Configure CORS

Update backend CORS to allow Vercel frontend:

```python
# In backend/src/config/settings.py
CORS_ORIGINS = [
    "https://your-frontend.vercel.app",
    "https://your-custom-domain.com",
]
```

Redeploy backend:

```bash
railway up
```

## Environment Configuration

### Production Environment Variables

Create `.env.production` in backend (NEVER commit):

```bash
# Application
ENVIRONMENT=production
DEBUG=false
SECRET_KEY=your-cryptographically-secure-secret-key

# Database (Railway provides automatically)
DATABASE_URL=${DATABASE_URL}

# Redis (Railway provides automatically)
REDIS_URL=${REDIS_URL}

# CORS
CORS_ORIGINS=https://your-frontend.vercel.app,https://yourdomain.com

# JWT
JWT_SECRET_KEY=your-jwt-secret-key
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7
```

### Frontend Environment Variables

Configure in Vercel dashboard:

```bash
NEXT_PUBLIC_API_URL=https://your-backend.railway.app
NEXT_PUBLIC_APP_NAME=GoHighLevel Clone
```

## Deployment Process

### Automated Deployment (CI/CD)

The GitHub Actions workflow (`.github/workflows/ci-cd.yml`) automatically:

1. **On Push to Main Branch**:
   - Run backend tests (pytest, ruff, mypy)
   - Run frontend tests (vitest, playwright)
   - Build Docker images
   - Deploy backend to Railway
   - Deploy frontend to Vercel
   - Run integration tests

2. **On Pull Request**:
   - Run all tests
   - Build artifacts (no deployment)

### Manual Deployment

#### Deploy Backend Manually

```bash
# Build and push to Railway
railway up --detach

# Monitor deployment
railway logs
```

#### Deploy Frontend Manually

```bash
# Deploy to Vercel
cd frontend
vercel --prod
```

## Monitoring and Health Checks

### Health Check Endpoints

**Backend Health Check:**

```bash
GET /health
```

Response:
```json
{
  "status": "healthy",
  "database": "connected",
  "redis": "connected",
  "timestamp": "2026-02-07T12:00:00Z"
}
```

**Frontend Health Check:**

Vercel automatically checks the Next.js server.

### Monitoring Setup

#### Railway Monitoring

- **Logs**: `railway logs`
- **Metrics**: Railway dashboard (CPU, memory, requests)
- **Alerts**: Configure in Railway settings

#### Vercel Monitoring

- **Analytics**: Vercel Analytics (Web Vitals)
- **Speed Insights**: Performance monitoring
- **Logs**: Vercel dashboard

#### Application Logging

Backend uses structured JSON logging:

```python
import logging

logger = logging.getLogger(__name__)
logger.info("User action", extra={"user_id": 123, "action": "login"})
```

### Error Tracking (Optional)

Integrate Sentry for error tracking:

```bash
# Backend
pip install sentry-sdk

# Frontend
npm install @sentry/nextjs
```

## Rollback Procedures

### Railway Rollback

```bash
# View deployment history
railway status

# Rollback to previous deployment
railway rollback

# Rollback to specific deployment
railway rollback --deployment-id <id>
```

### Vercel Rollback

```bash
# View deployments
vercel ls

# Rollback in Vercel dashboard
# Or promote a previous deployment:
vercel promote <deployment-url> --scope <team>
```

### GitHub Actions Rollback

If CI/CD deployment fails:

1. Check GitHub Actions logs for errors
2. Fix the issue in a new branch
3. Create pull request
4. After tests pass, merge to main

## Troubleshooting

### Common Issues

#### 1. Database Connection Errors

**Symptoms**: Backend fails to connect to database

**Solutions**:
```bash
# Check DATABASE_URL environment variable
railway variables

# Verify PostgreSQL is running
railway status

# Check database logs
railway logs --service postgres

# Test connection
railway exec --service postgres psql -U postgres
```

#### 2. CORS Errors

**Symptoms**: Frontend cannot connect to backend API

**Solutions**:
```bash
# Check CORS_ORIGINS in backend
railway variables get CORS_ORIGINS

# Ensure frontend URL is allowed
railway variables set CORS_ORIGINS=https://your-frontend.vercel.app

# Redeploy backend
railway up
```

#### 3. Build Failures

**Symptoms**: Docker build fails in CI/CD

**Solutions**:
- Check GitHub Actions logs
- Test build locally: `docker build -t test .`
- Verify dependencies in `pyproject.toml` or `package.json`
- Check for syntax errors

#### 4. Deployment Timeout

**Symptoms**: Railway deployment times out

**Solutions**:
```bash
# Increase health check timeout in railway.toml
[deploy]
healthcheckTimeout = 60

# Check application startup time
railway logs

# Verify health endpoint is responding
curl https://your-backend.railway.app/health
```

#### 5. Out of Memory

**Symptoms**: Service crashes due to memory limits

**Solutions**:
```bash
# Increase memory allocation in railway.toml
[deploy.resources]
memory = "1024"  # Increase from 512MB

# Check memory usage
railway status

# Enable auto-scaling
[deploy.scaling]
minReplicas = 2
maxReplicas = 10
```

### Getting Help

1. **Logs**: Always check logs first
   - Railway: `railway logs`
   - Vercel: Dashboard → Logs
   - GitHub Actions: Actions tab

2. **Health Checks**: Verify services are healthy
   - Backend: `GET /health`
   - Database: `railway status --service postgres`
   - Redis: `railway status --service redis`

3. **Documentation**:
   - Railway: https://docs.railway.app
   - Vercel: https://vercel.com/docs
   - Docker: https://docs.docker.com

## Security Checklist

- [ ] Change default passwords and secrets
- [ ] Enable HTTPS (automatic on Railway/Vercel)
- [ ] Configure CORS properly
- [ ] Set environment variable `DEBUG=false` in production
- [ ] Use strong `SECRET_KEY` for JWT
- [ ] Enable rate limiting
- [ ] Set up database backups (Railway automatic)
- [ ] Monitor logs for suspicious activity
- [ ] Keep dependencies updated
- [ ] Run security scans in CI/CD

## Cost Optimization

### Free Tier Limits

**Railway**:
- $5 free credit/month
- After: Pay-per-use (approx. $5-20/month for small apps)

**Vercel**:
- Hobby plan: Free
- Pro plan: $20/month

### Optimization Tips

1. **Right-size resources**: Don't over-allocate memory/CPU
2. **Enable caching**: Use Redis for session storage
3. **Database connection pooling**: Limit max connections
4. **CDN for assets**: Vercel handles this automatically
5. **Monitor usage**: Set up alerts for cost spikes

## Next Steps

1. Set up monitoring and alerting
2. Configure custom domains
3. Set up database backup strategy
4. Configure SSL certificates (automatic)
5. Set up staging environment
6. Document runbook for operations team

## Additional Resources

- [Railway Documentation](https://docs.railway.app)
- [Vercel Documentation](https://vercel.com/docs)
- [Docker Documentation](https://docs.docker.com)
- [GitHub Actions Documentation](https://docs.github.com/actions)
