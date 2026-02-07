# Deployment Guide

This guide covers deploying the GoHighLevel Clone Workflow Automation frontend to various platforms.

## Prerequisites

- Node.js 20+
- npm or yarn
- Git
- Cloud provider account (Vercel, Netlify, AWS, etc.)

## Environment Variables

Create `.env.production`:

```env
NEXT_PUBLIC_API_URL=https://api.example.com
NEXT_PUBLIC_WS_URL=wss://api.example.com
NEXT_PUBLIC_APP_URL=https://app.example.com
NEXT_PUBLIC_SENTRY_DSN=your-sentry-dsn
NEXT_PUBLIC_ANALYTICS_ID=your-analytics-id
```

## Build Process

### Local Build

```bash
npm run build
```

This creates:
- `.next/` - Build output
- `public/` - Static assets

### Build Optimization

```bash
# Analyze bundle size
npm run build -- --analyze

# Generate standalone build
NEXT_PRIVATE_STANDALONE=true npm run build
```

## Vercel Deployment (Recommended)

### Setup

1. Install Vercel CLI:
```bash
npm i -g vercel
```

2. Login:
```bash
vercel login
```

3. Deploy:
```bash
vercel
```

### Automatic Deployment

Connect your Git repository to Vercel for automatic deployments on push.

### Environment Variables

Set in Vercel dashboard:
- `NEXT_PUBLIC_API_URL`
- `NEXT_PUBLIC_WS_URL`
- `NEXT_PUBLIC_APP_URL`

### Custom Domain

1. Add domain in Vercel dashboard
2. Update DNS records:
   - CNAME: `cname.vercel-dns.com`

## Netlify Deployment

### Setup

1. Install Netlify CLI:
```bash
npm i -g netlify-cli
```

2. Build:
```bash
npm run build
```

3. Deploy:
```bash
netlify deploy --prod
```

### Configuration

Create `netlify.toml`:

```toml
[build]
  command = "npm run build"
  publish = ".next"

[[plugins]]
  package = "@netlify/plugin-nextjs"

[build.environment]
  NEXT_PUBLIC_API_URL = "https://api.example.com"
```

## Docker Deployment

### Dockerfile

```dockerfile
FROM node:20-alpine AS base

# Install dependencies only when needed
FROM base AS deps
RUN apk add --no-cache libc6-compat
WORKDIR /app

COPY package*.json ./
RUN npm ci

# Rebuild the source code only when needed
FROM base AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .

ENV NEXT_TELEMETRY_DISABLED 1

RUN npm run build

# Production image, copy all the files and run next
FROM base AS runner
WORKDIR /app

ENV NODE_ENV production
ENV NEXT_TELEMETRY_DISABLED 1

RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

EXPOSE 3000

ENV PORT 3000
ENV HOSTNAME "0.0.0.0"

CMD ["node", "server.js"]
```

### Build and Run

```bash
# Build image
docker build -t gohighlevel-frontend .

# Run container
docker run -p 3000:3000 \
  -e NEXT_PUBLIC_API_URL=https://api.example.com \
  gohighlevel-frontend
```

### Docker Compose

```yaml
version: '3.8'

services:
  frontend:
    build: .
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=https://api.example.com
      - NEXT_PUBLIC_WS_URL=wss://api.example.com
    restart: unless-stopped
```

## AWS Deployment

### S3 + CloudFront

1. Build static export:
```bash
# next.config.js
module.exports = {
  output: 'export',
}

npm run build
```

2. Upload to S3:
```bash
aws s3 sync out/ s3://your-bucket --delete
```

3. Configure CloudFront distribution

### AWS Amplify

1. Connect repository to Amplify
2. Configure build settings:
```yaml
version: 1
frontend:
  phases:
    preBuild:
      commands:
        - npm ci
    build:
      commands:
        - npm run build
  artifacts:
    baseDirectory: .next
    files:
      - '**/*'
  cache:
    paths:
      - node_modules/**/*
```

## Kubernetes Deployment

### Deployment YAML

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: gohighlevel-frontend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: gohighlevel-frontend
  template:
    metadata:
      labels:
        app: gohighlevel-frontend
    spec:
      containers:
      - name: frontend
        image: your-registry/gohighlevel-frontend:latest
        ports:
        - containerPort: 3000
        env:
        - name: NEXT_PUBLIC_API_URL
          value: "https://api.example.com"
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
---
apiVersion: v1
kind: Service
metadata:
  name: gohighlevel-frontend-service
spec:
  selector:
    app: gohighlevel-frontend
  ports:
  - protocol: TCP
    port: 80
    targetPort: 3000
  type: LoadBalancer
```

## Performance Optimization

### CDN Configuration

1. Enable CDN for static assets
2. Set cache headers:
```http
Cache-Control: public, max-age=31536000, immutable
```

3. Enable compression (gzip, brotli)

### Monitoring

1. **Sentry** for error tracking:
```javascript
import * as Sentry from "@sentry/nextjs";

Sentry.init({
  dsn: process.env.NEXT_PUBLIC_SENTRY_DSN,
});
```

2. **Vercel Analytics**:
```javascript
import { Analytics } from '@vercel/analytics/react';

export default function RootLayout({ children }) {
  return (
    <html>
      <body>
        {children}
        <Analytics />
      </body>
    </html>
  );
}
```

3. **Web Vitals** monitoring

## Security

### Headers

Configure security headers in `next.config.js`:

```javascript
module.exports = {
  async headers() {
    return [
      {
        source: '/:path*',
        headers: [
          {
            key: 'X-DNS-Prefetch-Control',
            value: 'on'
          },
          {
            key: 'Strict-Transport-Security',
            value: 'max-age=63072000; includeSubDomains; preload'
          },
          {
            key: 'X-Frame-Options',
            value: 'SAMEORIGIN'
          },
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff'
          },
          {
            key: 'X-XSS-Protection',
            value: '1; mode=block'
          },
          {
            key: 'Referrer-Policy',
            value: 'origin-when-cross-origin'
          },
          {
            key: 'Content-Security-Policy',
            value: "default-src 'self'; script-src 'self' 'unsafe-eval' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:;"
          }
        ]
      }
    ]
  }
}
```

### Environment Variables

- Never commit `.env.local`
- Use platform-specific environment variable management
- Rotate secrets regularly

## Rollback Strategy

### Vercel

```bash
# List deployments
vercel ls

# Rollback to specific deployment
vercel rollback <deployment-url>
```

### Git

```bash
# Revert commit
git revert HEAD

# Push rollback
git push origin main
```

## Health Checks

Configure health check endpoint:

```javascript
// app/api/health/route.ts
export async function GET() {
  return Response.json({ status: 'ok', timestamp: Date.now() });
}
```

## Troubleshooting

### Build Failures

1. Check Node.js version
2. Clear cache: `rm -rf .next node_modules`
3. Reinstall: `npm install`
4. Check logs

### Runtime Errors

1. Check browser console
2. Check server logs
3. Verify environment variables
4. Check API connectivity

### Performance Issues

1. Run Lighthouse audit
2. Check bundle size
3. Analyze Web Vitals
4. Review database queries

## Monitoring

### Key Metrics

- Response time
- Error rate
- Uptime
- Core Web Vitals (LCP, FID, CLS)
- Bundle size
- API latency

### Alerts

Set up alerts for:
- Error rate > 1%
- Response time > 3s
- Uptime < 99.9%
- Bundle size increase > 20%

## Support

For deployment issues:
- Check documentation
- Review logs
- Contact DevOps team
- Open support ticket
