# GitHub Actions CI/CD Workflows

This directory contains GitHub Actions workflows for automating the development and deployment pipeline.

## Workflows

### CI/CD Pipeline (`ci-cd.yml`)

**Triggers**:
- Push to `main` or `develop` branches
- Pull requests to `main` branch

**Jobs**:

#### 1. Backend Tests & Quality
- **Python Version**: 3.12
- **Steps**:
  - Install dependencies with pip
  - Run ruff linting
  - Run ruff formatting check
  - Run mypy type checking
  - Run pytest with coverage
  - Upload coverage to Codecov

#### 2. Frontend Tests & Quality
- **Node Version**: 20
- **Steps**:
  - Install dependencies with npm
  - Run ESLint
  - Run TypeScript type check
  - Run vitest unit tests
  - Run Playwright E2E tests

#### 3. Build Docker Images
- **Conditions**: Only on push events, after tests pass
- **Steps**:
  - Set up Docker Buildx
  - Login to GitHub Container Registry
  - Build and push backend image
  - Build and push frontend image
  - Use layer caching for faster builds

#### 4. Deploy Backend to Railway
- **Conditions**: Only on push to `main` branch
- **Steps**:
  - Install Railway CLI
  - Deploy backend service
  - Verify deployment health

#### 5. Deploy Frontend to Vercel
- **Conditions**: Only on push to `main` branch
- **Steps**:
  - Deploy to Vercel production
  - Automatic alias updates

#### 6. Integration Tests
- **Conditions**: After successful deployments
- **Steps**:
  - Run integration tests against production URLs
  - Verify API endpoints
  - Check database connectivity

## Required Secrets

Configure these in GitHub repository settings:

### Railway Deployment
```
RAILWAY_TOKEN=your-railway-token
```
Get token from: https://railway.app/account/tokens

### Vercel Deployment
```
VERCEL_TOKEN=your-vercel-token
VERCEL_ORG_ID=your-vercel-org-id
VERCEL_PROJECT_ID=your-vercel-project-id
```
Get values from: Vercel dashboard → Settings

### Optional Services
```
CODECOV_TOKEN=your-codecov-token
SENTRY_AUTH_TOKEN=your-sentry-token
SLACK_WEBHOOK_URL=your-slack-webhook
```

## Usage

### Manual Workflow Trigger

You can manually trigger the workflow from GitHub Actions tab:

1. Go to Actions tab in repository
2. Select "CI/CD Pipeline"
3. Click "Run workflow"
4. Select branch
5. Click "Run workflow"

### Skipping CI in Commits

To skip CI for a specific commit (not recommended for main branch):

```bash
git commit -m "your message [skip ci]"
```

### Testing Locally

You can test the CI/CD pipeline locally using [act](https://github.com/nektos/act):

```bash
# Install act
brew install act  # macOS
# or
choco install act  # Windows

# Run workflow locally
act push
```

## Workflow Status Badges

Add these badges to your README.md:

```markdown
![Backend Tests](https://github.com/username/repo/workflows/Backend%20Tests%20&%20Quality/badge.svg)
![Frontend Tests](https://github.com/username/repo/workflows/Frontend%20Tests%20&%20Quality/badge.svg)
![Deploy](https://github.com/username/repo/workflows/Deploy/badge.svg)
```

## Troubleshooting

### Pipeline Failures

**Tests Failing**:
- Check test logs in GitHub Actions
- Reproduce locally: `pytest` (backend) or `npm test` (frontend)
- Fix issues and push new commit

**Build Failures**:
- Check Docker build logs
- Test locally: `docker build -t test .`
- Verify Dockerfile syntax

**Deployment Failures**:
- Verify secrets are correctly configured
- Check platform status (Railway/Vercel)
- Review deployment logs in platform dashboards

**Integration Test Failures**:
- Check if previous deployment succeeded
- Verify API_BASE_URL secret
- Test endpoints manually

### Common Issues

**Outdated Dependencies**:
- The workflow uses `pip` and `npm` caching
- If dependencies are outdated, clear cache in GitHub Actions settings

**Timeout Issues**:
- Default timeout is 360 minutes (6 hours)
- If timeout occurs, check for infinite loops or long-running tests

**Rate Limiting**:
- GitHub Actions has usage limits
- Consider using self-hosted runners for heavy workloads

## Advanced Configuration

### Customizing the Workflow

**Adding New Jobs**:
```yaml
custom-job:
  runs-on: ubuntu-latest
  steps:
    - name: Run custom script
      run: ./scripts/custom.sh
```

**Adding Matrix Builds**:
```yaml
test-matrix:
  strategy:
    matrix:
      python-version: [3.11, 3.12]
      node-version: [18, 20]
  steps:
    # ... test steps
```

**Conditional Execution**:
```yaml
job-name:
  if: github.event_name == 'push' && github.ref == 'refs/heads/main'
  steps:
    # ... job steps
```

### Performance Optimization

**Parallel Jobs**:
- Independent jobs run in parallel by default
- Use `needs` keyword to create dependencies

**Caching**:
- Python pip: Automatic caching enabled
- npm modules: Automatic caching enabled
- Docker layers: GitHub Container Registry caching

**Resource Limits**:
- Default: 2-core CPU, 7 GB RAM
- Can be increased in workflow settings

## Monitoring and Alerts

### Workflow Notifications

**Slack Notifications** (optional):
```yaml
- name: Slack Notification
  uses: 8398a7/action-slack@v3
  with:
    status: ${{ job.status }}
    webhook_url: ${{ secrets.SLACK_WEBHOOK_URL }}
  if: always()
```

**Email Notifications**:
- Enabled by default for workflow failures
- Configure in GitHub repository settings

### Metrics Tracking

Track these metrics:
- Workflow duration
- Success rate
- Test coverage trends
- Deployment frequency

## Best Practices

1. **Keep Workflows Fast**: Use caching, parallel jobs
2. **Secure Secrets**: Never log secrets, use GitHub Secrets
3. **Clear Logs**: Use descriptive log messages
4. **Test Locally**: Use `act` to test workflows locally
5. **Monitor Costs**: GitHub Actions has usage limits

## Additional Resources

- [GitHub Actions Documentation](https://docs.github.com/actions)
- [Railway CLI Documentation](https://docs.railway.app/reference/cli)
- [Vercel CLI Documentation](https://vercel.com/docs/cli)
- [Docker Build Push Action](https://github.com/docker/build-push-action)

---

Last Updated: 2026-02-07
