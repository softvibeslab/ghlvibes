# GoHighLevel Clone - Workflows Frontend

This is the frontend application for the GoHighLevel Clone Workflows Module, built with Next.js 14, React 19, TypeScript, and Shadcn UI.

## Tech Stack

- **Framework**: Next.js 14+ with App Router
- **UI Library**: React 19+
- **Language**: TypeScript 5+
- **Styling**: Tailwind CSS 3+
- **Components**: Shadcn UI (Radix UI primitives)
- **State Management**: Zustand (global), TanStack Query (server)
- **Forms**: React Hook Form + Zod
- **Icons**: Lucide React
- **Drag & Drop**: @dnd-kit/core, React Flow
- **Charts**: Recharts
- **Authentication**: Clerk (to be integrated)

## Getting Started

### Prerequisites

- Node.js 20+ or 18+
- npm or yarn or pnpm

### Installation

1. Install dependencies:

```bash
npm install
# or
yarn install
# or
pnpm install
```

2. Set up environment variables:

```bash
cp .env.example .env.local
```

Edit `.env.local` and configure:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

3. Run the development server:

```bash
npm run dev
# or
yarn dev
# or
pnpm dev
```

4. Open [http://localhost:3000](http://localhost:3000) in your browser.

## Project Structure

```
src/
├── app/                          # Next.js App Router pages
│   ├── workflows/               # Workflow-related pages
│   │   ├── page.tsx             # Workflow list
│   │   ├── [id]/               # Workflow detail
│   │   │   ├── page.tsx        # Detail view
│   │   │   ├── edit/           # Workflow builder
│   │   │   ├── analytics/      # Analytics dashboard
│   │   │   ├── executions/     # Execution logs
│   │   │   ├── versions/       # Version history
│   │   │   └── settings/       # Workflow settings
│   │   ├── templates/          # Template marketplace
│   │   └── create/             # Creation wizard
│   ├── layout.tsx              # Root layout
│   ├── page.tsx                # Home page
│   └── providers.tsx           # React Query provider
├── components/
│   ├── workflows/              # Workflow-specific components
│   │   ├── workflow-list-table.tsx
│   │   ├── workflow-status-badge.tsx
│   │   ├── workflow-metrics.tsx
│   │   ├── workflow-canvas.tsx # Visual builder (React Flow)
│   │   └── ...
│   ├── ui/                     # Shadcn UI components
│   │   ├── button.tsx
│   │   ├── input.tsx
│   │   ├── card.tsx
│   │   └── ...
│   ├── layout/                 # Layout components
│   │   ├── header.tsx
│   │   ├── sidebar.tsx
│   │   └── footer.tsx
│   └── common/                 # Common components
│       ├── empty-state.tsx
│       ├── loading-spinner.tsx
│       └── error-boundary.tsx
├── lib/
│   ├── api/                    # API integration layer
│   │   ├── workflows.ts
│   │   ├── executions.ts
│   │   ├── analytics.ts
│   │   └── versions.ts
│   ├── stores/                 # Zustand stores
│   │   ├── workflow-store.ts
│   │   └── canvas-store.ts
│   ├── types/                  # TypeScript types
│   │   ├── workflow.ts
│   │   ├── trigger.ts
│   │   ├── action.ts
│   │   └── execution.ts
│   ├── validations/            # Zod schemas
│   │   ├── workflow-schema.ts
│   │   ├── trigger-schema.ts
│   │   └── action-schema.ts
│   └── utils/                  # Utility functions
│       ├── canvas-layout.ts
│       └── workflow-export.ts
├── hooks/                      # Custom React hooks
│   ├── use-workflows.ts
│   ├── use-workflow-detail.ts
│   ├── use-workflow-canvas.ts
│   └── use-workflow-auto-save.ts
└── styles/
    └── workflows.css           # Workflow-specific styles
```

## Features

- ✅ Workflow List with search, filter, and pagination
- ✅ Workflow Detail View with metrics
- ✅ Visual Workflow Builder (drag-and-drop canvas)
- 🚧 Analytics Dashboard with charts
- 🚧 Template Marketplace
- 🚧 Execution Logs Viewer
- 🚧 Version History
- 🚧 Bulk Enrollment Interface
- 🚧 Real-time updates via SSE

## Status

**Current Progress**: Phase 1-3 Complete (Foundation)

- ✅ Project setup with Next.js 14, React 19, TypeScript
- ✅ Shadcn UI components integration
- ✅ Zustand state management setup
- ✅ TanStack Query for server state
- ✅ Workflow list page
- ✅ Workflow detail page
- 🚧 Visual workflow builder (in progress)
- 🚧 Analytics dashboard (pending)
- 🚧 Template marketplace (pending)

## API Integration

The frontend integrates with the backend API at `/api/v1/`:

- **Workflows**: `/api/v1/workflows`
- **Executions**: `/api/v1/workflows/{id}/executions`
- **Analytics**: `/api/v1/workflows/{id}/analytics`
- **Templates**: `/api/v1/workflows/templates`
- **Versions**: `/api/v1/workflows/{id}/versions`

## Performance Targets

- First Contentful Paint (FCP): < 1.5s
- Largest Contentful Paint (LCP): < 2.5s
- Time to Interactive (TTI): < 3.5s
- Cumulative Layout Shift (CLS): < 0.1
- Initial Bundle Size: < 250KB

## Accessibility

- WCAG 2.1 AA compliant
- Keyboard navigation support
- Screen reader optimization
- ARIA attributes on interactive elements
- Focus management in modals and panels

## Testing

```bash
# Unit tests
npm run test

# E2E tests
npm run test:e2e

# Type checking
npm run type-check

# Linting
npm run lint
```

## Build

```bash
# Production build
npm run build

# Start production server
npm run start
```

## Deployment

The frontend is designed to be deployed on:

- **Vercel** (recommended for Next.js)
- **AWS S3 + CloudFront**
- **Docker containers** (self-hosted)

## License

MIT

## Support

For issues and questions, please open an issue in the repository.
