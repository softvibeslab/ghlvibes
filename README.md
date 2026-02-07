# GoHighLevel Clone - Marketing Automation Platform

<div align="center">

**A full-featured marketing automation platform built with modern technologies**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python 3.12](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green.svg)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-14.2-black.svg)](https://nextjs.org/)
[![TRUST 5](https://img.shields.io/badge/TRUST%205-PASS-brightgreen)](https://github.com/alfred/moai-adk)
[![Tests](https://img.shields.io/badge/Tests-108+-blue.svg)](backend/tests/)
[![Coverage](https://img.shields.io/badge/Coverage-85%25-brightgreen)](#)

[Features](#features) • [Quick Start](#quick-start) • [Documentation](#documentation) • [Development](#development) • [Deployment](#deployment)

</div>

---

## Overview

GoHighLevel Clone is a comprehensive marketing automation platform designed to help businesses streamline their marketing, sales, and customer relationship management processes. Built with a modern tech stack and following Domain-Driven Design (DDD) principles, this platform provides enterprise-grade features with exceptional code quality and maintainability.

### Key Highlights

- **Modern Architecture**: Clean Architecture with DDD patterns for scalability and maintainability
- **TRUST 5 Quality**: Tested, Readable, Unified, Secured, and Trackable codebase
- **Full-Stack**: Python/FastAPI backend with Next.js 14 frontend
- **Production Ready**: Docker containerization, CI/CD pipelines, comprehensive testing
- **Multi-Tenant**: Account-scoped data isolation with row-level security
- **Real-Time**: WebSocket support for live updates and notifications

---

## Features

### Core Modules

| Module | Features | Status |
|--------|----------|--------|
| **Workflows** | Automation engine, triggers, actions, conditions | 🟢 Implemented |
| **CRM** | Contact management, custom fields, tags, segments | 🟡 Partial |
| **Pipelines** | Sales pipelines, deal tracking, kanban boards | ⚪ Planned |
| **Campaigns** | Email, SMS, multi-channel campaigns | ⚪ Planned |
| **Funnels** | Landing page builder, forms, analytics | ⚪ Planned |
| **Calendars** | Booking system, appointment scheduling | ⚪ Planned |
| **Memberships** | Courses, community, subscriptions | ⚪ Planned |
| **Analytics** | Dashboards, reporting, insights | ⚪ Planned |
| **Integrations** | Webhooks, API connectors, Zapier | ⚪ Planned |

### Technical Features

- **Authentication**: JWT-based auth with refresh tokens
- **Rate Limiting**: Redis-backed rate limiting per account
- **Audit Logging**: Comprehensive activity tracking
- **API Documentation**: Auto-generated OpenAPI/Swagger docs
- **Testing**: 85%+ coverage with unit, integration, and E2E tests
- **Type Safety**: Full TypeScript frontend, Python type hints backend
- **Real-Time Updates**: WebSocket for live data synchronization
- **Background Jobs**: Celery for async task processing

---

## Quick Start

### Prerequisites

- **Python**: 3.12 or higher
- **Node.js**: 20.x or higher
- **Docker**: Latest version (for containerized deployment)
- **PostgreSQL**: 16 or higher
- **Redis**: 7 or higher

### Local Development Setup

#### 1. Clone the Repository

```bash
git clone https://github.com/your-org/gohighlevel-clone.git
cd gohighlevel-clone
```

#### 2. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -e .

# Setup environment variables
cp .env.example .env
# Edit .env with your configuration

# Run database migrations
alembic upgrade head

# Start development server
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

Backend API will be available at [http://localhost:8000](http://localhost:8000)

#### 3. Frontend Setup

```bash
# Navigate to frontend directory (in a new terminal)
cd frontend

# Install dependencies
npm install

# Setup environment variables
cp .env.example .env.local
# Edit .env.local with your configuration

# Start development server
npm run dev
```

Frontend will be available at [http://localhost:3000](http://localhost:3000)

#### 4. Docker Deployment (Recommended)

```bash
# Start all services (PostgreSQL, Redis, Backend, Frontend)
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Verify Installation

```bash
# Check backend health
curl http://localhost:8000/health

# Access API documentation
open http://localhost:8000/docs

# Access frontend
open http://localhost:3000
```

---

## Documentation

### User Documentation

- **[Getting Started Guide](docs/getting-started.md)** - New user orientation
- **[User Manual](docs/user-manual.md)** - Feature-by-feature guide
- **[Admin Guide](docs/admin-guide.md)** - Administration and configuration
- **[FAQ](docs/faq.md)** - Frequently asked questions

### Developer Documentation

- **[API Reference](docs/api/README.md)** - Complete API documentation
  - [Workflows API](docs/api/workflows.md)
  - [Contacts API](docs/api/contacts.md)
  - [Campaigns API](docs/api/campaigns.md)
- **[Architecture Guide](docs/architecture/README.md)** - System design and patterns
  - [System Architecture](docs/architecture/system.md)
  - [Database Schema](docs/architecture/database.md)
  - [Data Flow](docs/architecture/data-flow.md)
- **[Development Guide](docs/development/README.md)** - Development workflows
  - [Backend Development](docs/development/backend.md)
  - [Frontend Development](docs/development/frontend.md)
  - [Testing Guide](docs/development/testing.md)
  - [DDD Methodology](docs/development/ddd.md)
- **[Deployment Guide](docs/deployment/README.md)** - Deployment instructions
  - [Local Development](docs/deployment/local.md)
  - [Docker Deployment](docs/deployment/docker.md)
  - [Cloud Deployment](docs/deployment/cloud.md)

### Project Documentation

- **[CHANGELOG](CHANGELOG.md)** - Version history and changes
- **[Contributing Guide](CONTRIBUTING.md)** - Contribution guidelines
- **[License](LICENSE)** - MIT License

---

## Development

### Technology Stack

#### Backend

- **Framework**: FastAPI 0.115+
- **Language**: Python 3.12+
- **Database**: PostgreSQL 16 with SQLAlchemy 2.0 async
- **Cache**: Redis 7+
- **Authentication**: JWT with python-jose
- **Testing**: pytest, pytest-asyncio, pytest-cov
- **Code Quality**: ruff, mypy, black
- **API Docs**: OpenAPI 3.0 / Swagger

#### Frontend

- **Framework**: Next.js 14.2+ (App Router)
- **Language**: TypeScript 5.4+
- **UI Library**: React 19, Radix UI primitives
- **Styling**: Tailwind CSS 3.4+
- **State Management**: Zustand, TanStack Query
- **Forms**: React Hook Form + Zod validation
- **Charts**: Recharts
- **Testing**: Vitest, Playwright

#### Infrastructure

- **Containerization**: Docker, Docker Compose
- **CI/CD**: GitHub Actions
- **Deployment**: Railway, Vercel
- **Monitoring**: Application logging and metrics
- **Database Migrations**: Alembic

### Development Workflow

#### SPEC-First DDD Methodology

This project follows the MoAI-ADK SPEC-First development approach:

1. **Plan Phase** - Create comprehensive specification in EARS format
2. **Run Phase** - Implement using DDD: ANALYZE → PRESERVE → IMPROVE
3. **Sync Phase** - Generate documentation and create pull request

```bash
# Plan a new feature
/moai:1-plan "Implement contact management with custom fields"

# Implement with DDD
/moai:2-run SPEC-CNT-001

# Document and sync
/moai:3-sync SPEC-CNT-001
```

#### Quality Standards (TRUST 5)

All code must meet TRUST 5 quality standards:

- **Tested**: 85%+ test coverage with characterization tests
- **Readable**: Clear naming, English comments, ruff formatting
- **Unified**: Consistent patterns, single source of truth
- **Secured**: OWASP compliance, input validation, rate limiting
- **Trackable**: Semantic versioning, git history, audit logs

#### Running Tests

```bash
# Backend tests
cd backend
pytest tests/ -v --cov=src --cov-report=html

# Frontend tests
cd frontend
npm run test
npm run test:e2e

# Type checking
npm run type-check

# Linting
npm run lint
```

#### Code Quality Checks

```bash
# Backend - Ruff linting
cd backend
ruff check src/
ruff format src/

# Backend - Type checking
mypy src/

# Frontend - ESLint
cd frontend
npm run lint

# Frontend - Prettier
npm run format
```

---

## Deployment

### Docker Deployment

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f backend

# Stop services
docker-compose down

# Remove volumes (WARNING: deletes data)
docker-compose down -v
```

### Cloud Deployment

#### Railway (Backend)

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and link project
railway login
railway link

# Deploy backend
railway up
```

#### Vercel (Frontend)

```bash
# Install Vercel CLI
npm install -g vercel

# Deploy frontend
cd frontend
vercel
```

### Environment Variables

See [deployment environment configuration](docs/deployment/environment.md) for complete environment variable reference.

---

## Project Structure

```
gohighlevel-clone/
├── backend/                 # FastAPI backend
│   ├── src/
│   │   ├── core/           # Core configuration and utilities
│   │   ├── workflows/      # Workflow automation module
│   │   ├── crm/            # CRM module
│   │   └── main.py         # FastAPI application entry
│   ├── tests/              # Test suite
│   ├── alembic/            # Database migrations
│   ├── Dockerfile
│   └── pyproject.toml
├── frontend/               # Next.js frontend
│   ├── src/
│   │   ├── app/           # Next.js App Router pages
│   │   ├── components/    # React components
│   │   ├── lib/           # Utilities and configurations
│   │   └── styles/        # Global styles
│   ├── public/            # Static assets
│   ├── Dockerfile
│   └── package.json
├── docs/                  # Documentation
├── .github/               # GitHub Actions workflows
├── specs/                 # MoAI-ADK specifications
├── docker-compose.yml
├── README.md
└── CHANGELOG.md
```

---

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Contribution Process

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes following TRUST 5 standards
4. Write/update tests (85%+ coverage required)
5. Ensure all tests pass and code is formatted
6. Commit with conventional commits (`feat: add amazing feature`)
7. Push to your fork and submit a pull request

### Development Guidelines

- Follow the [Code of Conduct](docs/code-of-conduct.md)
- Write clear, descriptive commit messages
- Update documentation for any API changes
- Add tests for new functionality
- Ensure all existing tests pass

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Support

- **Documentation**: [docs/](docs/)
- **Issues**: [GitHub Issues](https://github.com/your-org/gohighlevel-clone/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-org/gohighlevel-clone/discussions)
- **Email**: support@gohighlevel-clone.com

---

## Roadmap

### Current Release: v0.1.0 (Alpha)

- ✅ Workflow automation engine
- ✅ Multi-tenant architecture
- ✅ Rate limiting and security
- 🔄 Contact management (in progress)
- ⚪ Campaign management
- ⚪ Pipeline management
- ⚪ Funnel builder
- ⚪ Booking system

### Upcoming Features

- **v0.2.0**: Email campaigns and automation
- **v0.3.0**: Landing page builder
- **v0.4.0**: Booking and calendar system
- **v0.5.0**: Membership and courses
- **v1.0.0**: Full feature parity with GoHighLevel

---

## Acknowledgments

- Built with [MoAI-ADK](https://github.com/alfred/moai-adk) - SPEC-First AI Development Kit
- UI components inspired by [shadcn/ui](https://ui.shadcn.com/)
- Architecture patterns from [Domain-Driven Design](https://martinfowler.com/tags/domain%20driven%20design.html)

---

<div align="center">

**Built with ❤️ by the GoHighLevel Clone Team**

[GoHighLevel Clone](https://github.com/your-org/gohighlevel-clone) • [Documentation](docs/) • [Support](mailto:support@gohighlevel-clone.com)

</div>
