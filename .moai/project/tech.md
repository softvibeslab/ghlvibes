# GoHighLevel Clone - Technology Stack

## Overview

This document details the technology choices, architecture patterns, and infrastructure decisions for the GoHighLevel Clone project.

---

## Technology Stack

### Core Technologies

| Layer | Technology | Version | Purpose |
|-------|------------|---------|---------|
| **Backend** | Python | 3.12 | Server-side programming language |
| **Backend Framework** | FastAPI | Latest | Async web framework with OpenAPI |
| **Frontend** | Next.js | 14 | React framework with App Router |
| **UI Components** | Shadcn/UI | Latest | Headless React component library |
| **Styling** | Tailwind CSS | 3.x | Utility-first CSS framework |

### Database Layer

| Technology | Provider | Purpose |
|------------|----------|---------|
| **PostgreSQL** | Supabase | Primary relational database |
| **Redis** | Self-hosted/Managed | In-memory caching and sessions |
| **Elasticsearch** | Self-hosted/Managed | Full-text search and analytics |

### Authentication and Authorization

| Technology | Purpose |
|------------|---------|
| **Clerk** | User authentication and identity management |
| **Supabase RLS** | Row-level security for data access |
| **RBAC** | Role-based access control |

### AI and Machine Learning

| Provider | Purpose |
|----------|---------|
| **OpenAI** | GPT models for conversational AI |
| **Anthropic** | Claude models for content generation |

### Communication Services

| Service | Provider | Purpose |
|---------|----------|---------|
| **SMS/Voice** | Twilio | SMS, MMS, voice calls, voicemail drops |
| **Email** | SendGrid | Transactional and bulk email |
| **Push** | Firebase | Mobile and web push notifications |

### Payment Processing

| Provider | Features |
|----------|----------|
| **Stripe** | Checkout, subscriptions, Connect marketplace |

### Storage and CDN

| Service | Provider | Purpose |
|---------|----------|---------|
| **File Storage** | Supabase Storage | S3-compatible object storage |
| **CDN** | Cloudflare | Static asset delivery and caching |
| **Video** | Cloudflare Stream | Video hosting and streaming |

### Infrastructure

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Cloud** | AWS | Primary cloud platform |
| **Containers** | Docker | Application containerization |
| **Orchestration** | Kubernetes | Container orchestration |
| **CI/CD** | GitHub Actions | Continuous integration and deployment |

---

## Architecture Decisions

### Pattern: Clean Architecture (Monorepo)

The project follows Clean Architecture principles within a monorepo structure:

```
┌─────────────────────────────────────────────────────────────┐
│                     Presentation Layer                       │
│              (Next.js App Router, React Components)          │
├─────────────────────────────────────────────────────────────┤
│                     Application Layer                        │
│            (FastAPI Routes, Use Cases, DTOs)                 │
├─────────────────────────────────────────────────────────────┤
│                       Domain Layer                           │
│             (Entities, Value Objects, Services)              │
├─────────────────────────────────────────────────────────────┤
│                   Infrastructure Layer                       │
│        (Repositories, External Services, Database)           │
└─────────────────────────────────────────────────────────────┘
```

**Rationale:**

- Separation of concerns enables independent testing
- Domain logic remains pure and framework-agnostic
- External dependencies are isolated and swappable
- Enables parallel development across layers

### Methodology: Domain-Driven Development (DDD)

Development follows the ANALYZE-PRESERVE-IMPROVE cycle:

1. **ANALYZE:** Understand existing behavior and code structure
2. **PRESERVE:** Create characterization tests for existing behavior
3. **IMPROVE:** Implement changes with behavior preservation

**Benefits:**

- Reduces regression risk through characterization tests
- Enables safe refactoring with test validation
- Supports incremental improvements

### Specification Format: EARS

All requirements use the EARS (Event-Action-Result-State) format:

```
When [EVENT],
the system shall [ACTION]
resulting in [RESULT]
in [STATE]
```

**Types:**

| Type | Description | Example |
|------|-------------|---------|
| Ubiquitous | Always active | "The system shall encrypt all data at rest" |
| Event-driven | Trigger-based | "When a user submits a form, the system shall..." |
| State-driven | Conditional | "While the system is in maintenance mode, the system shall..." |
| Unwanted | Prohibited | "The system shall not store plaintext passwords" |
| Optional | Nice-to-have | "Where possible, the system shall suggest corrections" |

---

## Development Environment

### Prerequisites

| Requirement | Version |
|-------------|---------|
| Python | 3.12+ |
| Node.js | 20 LTS |
| Docker | 24+ |
| Docker Compose | 2.20+ |

### Local Development Stack

```yaml
services:
  # Backend API
  backend:
    image: python:3.12
    ports: ["8000:8000"]

  # Frontend
  frontend:
    image: node:20
    ports: ["3000:3000"]

  # Database
  postgres:
    image: postgres:16
    ports: ["5432:5432"]

  # Cache
  redis:
    image: redis:7
    ports: ["6379:6379"]

  # Search
  elasticsearch:
    image: elasticsearch:8
    ports: ["9200:9200"]
```

### Environment Variables

| Category | Variables |
|----------|-----------|
| **Database** | `DATABASE_URL`, `REDIS_URL` |
| **Auth** | `CLERK_SECRET_KEY`, `CLERK_PUBLISHABLE_KEY` |
| **AI** | `OPENAI_API_KEY`, `ANTHROPIC_API_KEY` |
| **Communication** | `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `SENDGRID_API_KEY` |
| **Payments** | `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET` |
| **Storage** | `SUPABASE_URL`, `SUPABASE_SERVICE_KEY` |

---

## Quality Framework: TRUST 5

All code must meet the TRUST 5 quality standards:

### Tested

| Requirement | Target |
|-------------|--------|
| Unit test coverage | 80% minimum |
| Integration tests | Required for all APIs |
| E2E tests | Required for critical paths |
| Characterization tests | Required for existing code |

### Readable

| Requirement | Standard |
|-------------|----------|
| Documentation | Required for public APIs |
| Code comments | Minimal, explain "why" not "what" |
| Naming convention | snake_case (Python), camelCase (TypeScript) |

### Unified

| Requirement | Implementation |
|-------------|----------------|
| Single source of truth | One location per data entity |
| Centralized config | Environment-based configuration |
| Shared types | TypeScript types shared between layers |

### Secured

| Requirement | Standard |
|-------------|----------|
| OWASP compliance | Top 10 vulnerabilities addressed |
| Encryption at rest | AES-256 for sensitive data |
| Encryption in transit | TLS 1.3 for all connections |
| Audit logging | All data modifications logged |

### Trackable

| Requirement | Standard |
|-------------|----------|
| Version control | Git with conventional commits |
| Semantic versioning | MAJOR.MINOR.PATCH |
| Changelog | Required for all releases |

---

## LSP Quality Gates

The project enforces LSP-based quality validation at each phase:

### Phase Thresholds

| Phase | Errors | Type Errors | Lint Errors | Warnings |
|-------|--------|-------------|-------------|----------|
| **Plan** | Baseline capture | - | - | - |
| **Run** | 0 | 0 | 0 | No regression |
| **Sync** | 0 | 0 | 0 | Max 10 |

### Diagnostic Sources

| Source | Tool | Purpose |
|--------|------|---------|
| Type checking | Pyright, TypeScript | Type safety validation |
| Linting | Ruff, ESLint | Code quality rules |
| Security | Bandit, Semgrep | Security vulnerability detection |

---

## API Design

### REST API Standards

| Aspect | Standard |
|--------|----------|
| Format | JSON with OpenAPI 3.0 documentation |
| Versioning | URL path versioning (`/api/v1/`) |
| Authentication | Bearer tokens (JWT via Clerk) |
| Pagination | Cursor-based with limit/offset fallback |
| Error format | RFC 7807 Problem Details |

### Rate Limiting

| Tier | Requests/minute | Burst |
|------|-----------------|-------|
| Free | 60 | 10 |
| Pro | 300 | 50 |
| Enterprise | 1000 | 100 |

### Webhook Design

| Feature | Implementation |
|---------|----------------|
| Signature | HMAC-SHA256 |
| Retry | Exponential backoff (3 attempts) |
| Timeout | 30 seconds |
| Payload | JSON with event type and data |

---

## Database Design

### Schema Conventions

| Convention | Standard |
|------------|----------|
| Table naming | Plural, snake_case (`contacts`, `campaigns`) |
| Primary keys | UUID v4 |
| Timestamps | `created_at`, `updated_at` (UTC) |
| Soft delete | `deleted_at` column |
| Audit fields | `created_by`, `updated_by` |

### Multi-tenancy

| Strategy | Implementation |
|----------|----------------|
| Isolation | Schema-per-tenant with shared pool |
| Routing | Tenant ID in JWT claims |
| Security | Row-level security policies |

### Indexing Strategy

| Index Type | Use Case |
|------------|----------|
| B-tree | Equality and range queries |
| GIN | Full-text search, JSONB |
| Partial | Frequently filtered subsets |

---

## Caching Strategy

### Cache Layers

| Layer | Technology | TTL | Use Case |
|-------|------------|-----|----------|
| Application | Redis | 5-60 min | Session, API responses |
| Database | Query cache | 1-5 min | Expensive queries |
| CDN | Cloudflare | 1-24 hours | Static assets, pages |

### Cache Invalidation

| Strategy | Implementation |
|----------|----------------|
| Time-based | TTL expiration |
| Event-based | Pub/sub invalidation on write |
| Manual | Admin-triggered purge |

---

## Deployment Architecture

### Production Environment

```
┌─────────────────────────────────────────────────────────────┐
│                        Cloudflare                            │
│                   (CDN, DDoS Protection)                     │
└────────────────────────────┬────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────┐
│                    AWS Load Balancer                         │
│                   (Application LB)                           │
└────────────────────────────┬────────────────────────────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
┌───────▼───────┐   ┌───────▼───────┐   ┌───────▼───────┐
│   Frontend    │   │   Backend     │   │   Workers     │
│  (Next.js)    │   │  (FastAPI)    │   │  (Celery)     │
│   Pods: 3+    │   │   Pods: 5+    │   │   Pods: 3+    │
└───────────────┘   └───────────────┘   └───────────────┘
        │                    │                    │
        └────────────────────┼────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────┐
│                       Data Layer                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐    │
│  │PostgreSQL│  │  Redis   │  │Elastic   │  │Supabase  │    │
│  │(Supabase)│  │ (Cache)  │  │ Search   │  │ Storage  │    │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘    │
└─────────────────────────────────────────────────────────────┘
```

### CI/CD Pipeline

```
┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐
│  Push   │───▶│  Build  │───▶│  Test   │───▶│ Deploy  │
│         │    │         │    │         │    │         │
└─────────┘    └─────────┘    └─────────┘    └─────────┘
                   │              │              │
              ┌────┴────┐    ┌───┴───┐    ┌────┴────┐
              │ Docker  │    │ Unit  │    │Staging │
              │  Build  │    │ Tests │    │  ──▶   │
              │   +     │    │   +   │    │  Prod  │
              │  Lint   │    │ E2E   │    │        │
              └─────────┘    └───────┘    └────────┘
```

### Environments

| Environment | Purpose | URL Pattern |
|-------------|---------|-------------|
| Development | Local development | localhost:3000 |
| Staging | Pre-production testing | staging.domain.com |
| Production | Live environment | app.domain.com |

---

## Monitoring and Observability

### Logging

| Component | Destination | Format |
|-----------|-------------|--------|
| Application | CloudWatch | JSON structured |
| Access logs | CloudWatch | Combined format |
| Error logs | Sentry | Exception tracking |

### Metrics

| Category | Metrics |
|----------|---------|
| Application | Request latency, error rate, throughput |
| Infrastructure | CPU, memory, disk, network |
| Business | Active users, conversions, revenue |

### Alerting

| Severity | Response Time | Examples |
|----------|---------------|----------|
| Critical | 5 minutes | Service down, data loss |
| High | 30 minutes | High error rate, degradation |
| Medium | 4 hours | Performance issues |
| Low | Next business day | Non-critical warnings |

---

## Security Architecture

### Authentication Flow

```
┌──────────┐     ┌──────────┐     ┌──────────┐
│  Client  │────▶│  Clerk   │────▶│   API    │
│          │◀────│          │◀────│          │
└──────────┘     └──────────┘     └──────────┘
     │                │                │
     │  1. Login      │  2. Validate   │
     │  Request       │  Token         │
     │                │                │
     │  4. Return     │  3. User       │
     │  JWT Token     │  Session       │
```

### Authorization Model

| Level | Implementation |
|-------|----------------|
| API | JWT validation middleware |
| Resource | RBAC with permission checks |
| Data | Row-level security (RLS) |

### Data Protection

| Data Type | Protection |
|-----------|------------|
| PII | Encrypted at rest, masked in logs |
| Credentials | Vault storage, never logged |
| Sessions | HTTP-only cookies, secure flag |
| API keys | Hashed storage, scoped permissions |

---

## Integration Architecture

### External Service Integration

| Service | Integration Method | Retry Strategy |
|---------|-------------------|----------------|
| Twilio | REST API + Webhooks | 3 retries, exponential |
| SendGrid | REST API | 3 retries, exponential |
| Stripe | REST API + Webhooks | Idempotent requests |
| Clerk | REST API + Webhooks | Circuit breaker |

### Webhook Processing

```
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│ External │───▶│ Webhook  │───▶│  Queue   │───▶│ Worker   │
│ Service  │    │ Endpoint │    │ (Redis)  │    │          │
└──────────┘    └──────────┘    └──────────┘    └──────────┘
                     │
                ┌────┴────┐
                │Signature│
                │Validate │
                └─────────┘
```

---

## Performance Targets

| Metric | Target | Measurement |
|--------|--------|-------------|
| API response time (p95) | < 200ms | Application metrics |
| Page load time (p95) | < 2s | Core Web Vitals |
| Uptime | 99.9% | Monitoring alerts |
| Error rate | < 0.1% | Application metrics |
| Database query time (p95) | < 50ms | Query monitoring |

---

## Development Framework

### MoAI-ADK Integration

| Version | 10.7.0 |
|---------|--------|
| Methodology | SPEC-First DDD |
| Quality Framework | TRUST 5 |
| Specification Format | EARS |

### Development Commands

| Command | Purpose |
|---------|---------|
| `/moai:1-plan` | Create SPEC documents |
| `/moai:2-run SPEC-XXX` | Execute DDD implementation |
| `/moai:3-sync SPEC-XXX` | Synchronize documentation |
| `/moai:alfred` | Autonomous task execution |
| `/moai:fix` | Parallel auto-fix scanning |

---

## Technology Rationale

### Why FastAPI?

- Native async support for high concurrency
- Automatic OpenAPI documentation
- Type hints with Pydantic validation
- High performance (comparable to Node.js, Go)

### Why Next.js 14?

- React Server Components for performance
- App Router for modern routing patterns
- Built-in image and font optimization
- Excellent Vercel deployment support

### Why Supabase?

- PostgreSQL with real-time subscriptions
- Built-in authentication (Row Level Security)
- S3-compatible storage
- Open source and self-hostable

### Why Clerk?

- Modern authentication UX
- Pre-built UI components
- Multi-factor authentication
- SSO and social login support

### Why Cloudflare?

- Global CDN with edge computing
- DDoS protection included
- Stream for video hosting
- Workers for edge logic
