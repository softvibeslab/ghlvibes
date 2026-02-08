import { ReactElement } from 'react'
import { render, RenderOptions } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { vi } from 'vitest'

// Mock next/navigation
vi.mock('next/navigation', () => ({
  useRouter: () => ({
    push: vi.fn(),
    replace: vi.fn(),
    prefetch: vi.fn(),
    back: vi.fn(),
  }),
  useSearchParams: () => new URLSearchParams(),
  usePathname: () => '/',
}))

// Mock providers
const AllTheProviders = ({ children }: { children: React.ReactNode }) => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
      },
      mutations: {
        retry: false,
      },
    },
  })

  return (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  )
}

const customRender = (
  ui: ReactElement,
  options?: Omit<RenderOptions, 'wrapper'>
) => render(ui, { wrapper: AllTheProviders, ...options })

// Mock handlers for common user actions
export const mockHandlers = {
  click: (onClick: () => void) => ({ onClick }),

  change: (onChange: (value: string) => void) => ({
    onChange: (e: React.ChangeEvent<HTMLInputElement>) => onChange(e.target.value),
  }),

  submit: (onSubmit: (data: any) => void) => ({
    onSubmit: (e: React.FormEvent) => {
      e.preventDefault()
      onSubmit({})
    },
  }),
}

// Re-export everything from Testing Library
export * from '@testing-library/react'
export { default as userEvent } from '@testing-library/user-event'

// Override render method
export { customRender as render }
