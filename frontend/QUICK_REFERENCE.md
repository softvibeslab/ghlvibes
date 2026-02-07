# Frontend Quick Reference Guide
## Workflows Module - SPEC-FRN-001

**Last Updated**: 2026-02-07
**Status**: Phase 1-3 Complete (35% Overall)

---

## Project Structure Overview

```
frontend/
├── src/
│   ├── app/                    # Next.js App Router pages
│   │   ├── workflows/         # Workflow pages
│   │   ├── layout.tsx         # Root layout
│   │   ├── page.tsx           # Home page
│   │   └── providers.tsx      # React Query provider
│   ├── components/            # React components
│   │   ├── workflows/         # Workflow-specific components
│   │   ├── ui/                # Shadcn UI components
│   │   ├── layout/            # Layout components (header, sidebar)
│   │   └── common/            # Shared components
│   ├── lib/                   # Core libraries
│   │   ├── api/               # API integration layer
│   │   ├── stores/            # Zustand stores
│   │   ├── types/             # TypeScript definitions
│   │   ├── validations/       # Zod schemas
│   │   └── utils/             # Utility functions
│   ├── hooks/                 # Custom React hooks
│   └── styles/                # Global styles
├── public/                    # Static assets
├── package.json               # Dependencies
├── tsconfig.json              # TypeScript config
├── tailwind.config.ts         # Tailwind config
├── next.config.js             # Next.js config
└── .env.local                 # Environment variables (gitignored)
```

---

## Key Technologies

| Technology | Version | Purpose |
|------------|---------|---------|
| Next.js | 14.2.0 | React framework with App Router |
| React | 19.0.0 | UI library |
| TypeScript | 5.4.5 | Type safety |
| Tailwind CSS | 3.4.3 | Styling |
| Shadcn UI | Latest | Component library |
| Zustand | Latest | Client state management |
| TanStack Query | 5.40.0 | Server state management |
| React Hook Form | Latest | Form management |
| Zod | 3.23.8 | Schema validation |
| @dnd-kit | Latest | Drag and drop |
| React Flow | 12.0.0 | Visual workflow canvas |
| Lucide React | Latest | Icons |
| Recharts | Latest | Charts |

---

## Common Commands

```bash
# Development
npm run dev              # Start dev server (localhost:3000)
npm run build           # Production build
npm run start           # Start production server

# Code Quality
npm run lint            # Run ESLint
npm run type-check      # TypeScript type check

# Testing (not yet implemented)
npm run test            # Unit tests (Vitest)
npm run test:e2e        # E2E tests (Playwright)
```

---

## Component Usage

### Workflow List Table
```typescript
import { WorkflowListTable } from '@/components/workflows/workflow-list-table';

<WorkflowListTable
  workflows={workflows}
  onEdit={(id) => router.push(`/workflows/${id}/edit`)}
  onDelete={(id) => deleteWorkflow(id)}
  onDuplicate={(id) => duplicateWorkflow(id)}
/>
```

### Workflow Status Badge
```typescript
import { WorkflowStatusBadge } from '@/components/workflows/workflow-status-badge';

<WorkflowStatusBadge status="active" /> // Green badge
<WorkflowStatusBadge status="draft" /> // Gray badge
<WorkflowStatusBadge status="paused" /> // Yellow badge
```

### Workflow Metrics
```typescript
import { WorkflowMetrics } from '@/components/workflows/workflow-metrics';

<WorkflowMetrics
  stats={{
    total_enrolled: 1250,
    currently_active: 342,
    completed: 891,
    drop_off_rate: 28.7,
    avg_completion_time_minutes: 45.3
  }}
/>
```

### Empty State
```typescript
import { EmptyState } from '@/components/common/empty-state';
import { Workflow } from 'lucide-react';

<EmptyState
  icon={Workflow}
  title="No workflows found"
  description="Create your first workflow to get started"
  action={{
    label: 'Create Workflow',
    onClick: () => router.push('/workflows/create')
  }}
/>
```

---

## State Management Examples

### Using Workflow Store
```typescript
import { useWorkflowStore } from '@/lib/stores/workflow-store';

function WorkflowEditor() {
  const { workflow, isLoading, updateWorkflow, saveDraft } = useWorkflowStore();

  const handleNameChange = (name: string) => {
    updateWorkflow({ name });
  };

  const handleSave = () => {
    saveDraft();
  };

  return (
    // JSX
  );
}
```

### Using Canvas Store
```typescript
import { useCanvasStore } from '@/lib/stores/canvas-store';

function WorkflowCanvas() {
  const {
    nodes,
    edges,
    selectedNodeId,
    addNode,
    removeNode,
    setSelectedNode
  } = useCanvasStore();

  const handleAddNode = (node: WorkflowNode) => {
    addNode(node);
  };

  return (
    // JSX
  );
}
```

---

## API Integration Examples

### Fetching Workflows
```typescript
import { useQuery } from '@tanstack/react-query';
import { getWorkflows } from '@/lib/api/workflows';

function WorkflowList() {
  const { data, isLoading, error } = useQuery({
    queryKey: ['workflows', { status: 'active' }],
    queryFn: () => getWorkflows({ status: 'active', page: 1, pageSize: 50 }),
  });

  if (isLoading) return <WorkflowTableSkeleton />;
  if (error) return <ErrorMessage error={error} />;

  return <WorkflowListTable workflows={data?.items || []} />;
}
```

### Creating a Workflow
```typescript
import { useMutation } from '@tanstack/react-query';
import { createWorkflow } from '@/lib/api/workflows';

function CreateWorkflowForm() {
  const mutation = useMutation({
    mutationFn: (data: CreateWorkflowDto) => createWorkflow(data),
    onSuccess: (workflow) => {
      router.push(`/workflows/${workflow.id}`);
    },
  });

  const handleSubmit = (data) => {
    mutation.mutate(data);
  };

  return <form onSubmit={handleSubmit}>{/* Form fields */}</form>;
}
```

---

## Type Definitions

### Workflow Type
```typescript
interface Workflow {
  id: string;
  account_id: string;
  name: string;
  description: string;
  trigger_type: TriggerType | null;
  trigger_config: Record<string, unknown>;
  status: WorkflowStatus;
  version: number;
  created_at: string;
  updated_at: string;
  created_by: string;
  updated_by: string;
  actions: WorkflowAction[];
  goals: WorkflowGoal[];
  stats: WorkflowStats;
}

type WorkflowStatus = 'draft' | 'active' | 'paused' | 'archived';
```

### Trigger Types (26 total)
```typescript
type TriggerType =
  | 'contact.created'
  | 'contact.updated'
  | 'contact.tagAdded'
  | 'contact.tagRemoved'
  | 'form.submitted'
  | 'pipeline.stageChanged'
  | 'appointment.booked'
  | 'payment.received'
  | 'email.opened'
  | 'specific.datetime'
  // ... 16 more types
```

### Action Types (25+ total)
```typescript
type ActionType =
  | 'communication.sendEmail'
  | 'communication.sendSms'
  | 'crm.addTag'
  | 'crm.setCustomField'
  | 'timing.wait'
  | 'logic.ifElse'
  | 'webhook.call'
  // ... 18+ more types
```

---

## Utility Functions

### Date Formatting
```typescript
import { formatDate, formatDateTime, formatRelativeTime } from '@/lib/utils';

formatDate('2026-02-07')        // "Feb 7, 2026"
formatDateTime('2026-02-07T10:30:00Z')  // "Feb 7, 2026, 10:30 AM"
formatRelativeTime('2026-02-07T10:30:00Z') // "2 hours ago"
```

### Number Formatting
```typescript
import { formatNumber, formatPercentage } from '@/lib/utils';

formatNumber(1250)              // "1,250"
formatPercentage(28.7)          // "28.7%"
```

### ClassName Merging
```typescript
import { cn } from '@/lib/utils';

cn('px-4 py-2', 'bg-blue-500', isActive && 'bg-blue-700')
// "px-4 py-2 bg-blue-500 bg-blue-700"
```

---

## Styling Guidelines

### Using Tailwind Classes
```typescript
// Spacing
<div className="p-4 m-2">Padding 4, margin 2</div>

// Flexbox
<div className="flex items-center justify-between">
  <span>Left</span>
  <span>Right</span>
</div>

// Grid
<div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
  <div>Item 1</div>
  <div>Item 2</div>
  <div>Item 3</div>
</div>

// Responsive
<div className="text-sm md:text-base lg:text-lg">
  Responsive text
</div>
```

### Design Tokens (CSS Variables)
```css
/* Colors */
background: hsl(var(--background));
foreground: hsl(var(--foreground));
primary: hsl(var(--primary));
border: hsl(var(--border));

/* Usage in className */
<div className="bg-background text-foreground border border-border">
```

---

## Environment Variables

Create `.env.local`:
```env
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1

# Authentication (Clerk) - Not yet integrated
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_...
CLERK_SECRET_KEY=sk_test_...
```

---

## Common Patterns

### Protected Page
```typescript
'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';

export default function ProtectedPage() {
  const router = useRouter();

  useEffect(() => {
    // Check authentication
    const token = localStorage.getItem('auth_token');
    if (!token) {
      router.push('/login');
    }
  }, [router]);

  return <div>Protected content</div>;
}
```

### Loading and Error States
```typescript
const { data, isLoading, error, refetch } = useQuery({
  queryKey: ['workflows'],
  queryFn: getWorkflows,
});

if (isLoading) return <WorkflowTableSkeleton />;
if (error) return (
  <EmptyState
    icon={AlertCircle}
    title="Error loading workflows"
    description={error.message}
    action={{ label: 'Retry', onClick: () => refetch() }}
  />
);
```

### Debounced Search
```typescript
const [search, setSearch] = useState('');
const [debouncedSearch, setDebouncedSearch] = useState('');

useEffect(() => {
  const timer = setTimeout(() => {
    setDebouncedSearch(search);
  }, 300);
  return () => clearTimeout(timer);
}, [search]);
```

---

## Troubleshooting

### Build Errors
```bash
# Clear Next.js cache
rm -rf .next

# Reinstall dependencies
rm -rf node_modules package-lock.json
npm install

# Type check
npm run type-check
```

### Styling Issues
```bash
# Ensure Tailwind is scanning all files
# Check tailwind.config.ts content array

# Regenerate Tailwind
npm run build
```

### API Issues
```bash
# Check API URL in .env.local
echo $NEXT_PUBLIC_API_URL

# Test API endpoint
curl http://localhost:8000/api/v1/workflows
```

---

## Performance Tips

1. **Code Splitting**: Use dynamic imports for large components
   ```typescript
   const HeavyComponent = dynamic(() => import('./HeavyComponent'), {
     loading: () => <Skeleton />,
   });
   ```

2. **Image Optimization**: Always use Next.js Image component
   ```typescript
   import Image from 'next/image';
   <Image src="/logo.png" alt="Logo" width={200} height={100} />
   ```

3. **Memoization**: Use React.memo for expensive components
   ```typescript
   export const ExpensiveComponent = React.memo(({ data }) => {
     // Component logic
   });
   ```

4. **Query Caching**: TanStack Query caches by default
   ```typescript
   useQuery({
     queryKey: ['workflows'],
     queryFn: getWorkflows,
     staleTime: 5 * 60 * 1000, // 5 minutes
   });
   ```

---

## Resources

- **Next.js Documentation**: https://nextjs.org/docs
- **React 19 Docs**: https://react.dev
- **Tailwind CSS**: https://tailwindcss.com/docs
- **Shadcn UI**: https://ui.shadcn.com
- **TanStack Query**: https://tanstack.com/query/latest
- **Zustand**: https://zustand-demo.pmnd.rs
- **React Flow**: https://reactflow.dev

---

## Contact

For questions or issues, please refer to the main project README or open an issue in the repository.
