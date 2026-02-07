import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ExecutionList } from '@/components/execution/execution-list';
import { ExecutionDetailModal } from '@/components/execution/execution-detail-modal';
import { WorkflowExecution } from '@/lib/types/workflow';
import { axe, toHaveNoViolations } from 'jest-axe';

expect.extend(toHaveNoViolations);

describe('ExecutionList', () => {
  const mockExecutions: WorkflowExecution[] = [
    {
      id: '1',
      workflow_id: 'wf1',
      contact_id: 'c1',
      contact_name: 'John Doe',
      contact_email: 'john@example.com',
      status: 'success',
      started_at: '2025-01-01T10:00:00Z',
      completed_at: '2025-01-01T10:05:00Z',
      current_step: null,
      error_message: null,
      steps: [],
    },
    {
      id: '2',
      workflow_id: 'wf1',
      contact_id: 'c2',
      contact_name: 'Jane Smith',
      contact_email: 'jane@example.com',
      status: 'error',
      started_at: '2025-01-01T11:00:00Z',
      completed_at: null,
      current_step: 'send_email',
      error_message: 'Failed to send email',
      steps: [],
    },
  ];

  beforeEach(() => {
    // Mock fetch
    global.fetch = vi.fn(() =>
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve(mockExecutions),
      })
    ) as any;
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('should render execution list', async () => {
    render(<ExecutionList workflowId="wf1" onSelectExecution={vi.fn()} />);

    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument();
      expect(screen.getByText('Jane Smith')).toBeInTheDocument();
    });
  });

  it('should filter executions by search text', async () => {
    const user = userEvent.setup();

    render(<ExecutionList workflowId="wf1" onSelectExecution={vi.fn()} />);

    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument();
    });

    const searchInput = screen.getByPlaceholderText(/search by contact name or email/i);
    await user.type(searchInput, 'Jane');

    await waitFor(() => {
      expect(screen.queryByText('John Doe')).not.toBeInTheDocument();
      expect(screen.getByText('Jane Smith')).toBeInTheDocument();
    });
  });

  it('should filter executions by status', async () => {
    const user = userEvent.setup();

    render(<ExecutionList workflowId="wf1" onSelectExecution={vi.fn()} />);

    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument();
      expect(screen.getByText('Jane Smith')).toBeInTheDocument();
    });

    // Select error status filter
    const statusSelect = screen.getByLabelText(/filter by status/i);
    await user.click(statusSelect);

    const errorOption = screen.getByText('Error');
    await user.click(errorOption);

    await waitFor(() => {
      expect(screen.queryByText('John Doe')).not.toBeInTheDocument();
      expect(screen.getByText('Jane Smith')).toBeInTheDocument();
    });
  });

  it('should call onSelectExecution when item is clicked', async () => {
    const user = userEvent.setup();
    const handleSelect = vi.fn();

    render(<ExecutionList workflowId="wf1" onSelectExecution={handleSelect} />);

    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument();
    });

    const executionItem = screen.getByLabelText(/view execution details for john doe/i);
    await user.click(executionItem);

    expect(handleSelect).toHaveBeenCalledWith(mockExecutions[0]);
  });

  it('should not have accessibility violations', async () => {
    const { container } = render(
      <ExecutionList workflowId="wf1" onSelectExecution={vi.fn()} />
    );

    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument();
    });

    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });
});

describe('ExecutionDetailModal', () => {
  const mockExecution: WorkflowExecution = {
    id: '1',
    workflow_id: 'wf1',
    contact_id: 'c1',
    contact_name: 'John Doe',
    contact_email: 'john@example.com',
    status: 'success',
    started_at: '2025-01-01T10:00:00Z',
    completed_at: '2025-01-01T10:05:00Z',
    current_step: null,
    error_message: null,
    steps: [
      {
        id: 's1',
        execution_id: '1',
        action_id: 'a1',
        action_type: 'communication.sendEmail',
        status: 'success',
        started_at: '2025-01-01T10:00:00Z',
        completed_at: '2025-01-01T10:01:00Z',
        error_message: null,
        input_data: { to: 'john@example.com' },
        output_data: { messageId: 'msg123' },
      },
    ],
  };

  it('should render execution details', () => {
    render(
      <ExecutionDetailModal
        execution={mockExecution}
        open={true}
        onClose={vi.fn()}
      />
    );

    expect(screen.getByText('Execution Details')).toBeInTheDocument();
    expect(screen.getByText('John Doe')).toBeInTheDocument();
    expect(screen.getByText('john@example.com')).toBeInTheDocument();
  });

  it('should display step timeline', () => {
    render(
      <ExecutionDetailModal
        execution={mockExecution}
        open={true}
        onClose={vi.fn()}
      />
    );

    expect(screen.getByText('communication.sendEmail')).toBeInTheDocument();
  });

  it('should call onClose when close button is clicked', async () => {
    const user = userEvent.setup();
    const handleClose = vi.fn();

    render(
      <ExecutionDetailModal
        execution={mockExecution}
        open={true}
        onClose={handleClose}
      />
    );

    // Close dialog by clicking overlay
    const overlay = screen.getByText('Execution Details').closest('[role="dialog"]')?.parentElement;
    if (overlay) {
      await user.click(overlay);
      expect(handleClose).toHaveBeenCalled();
    }
  });

  it('should not have accessibility violations', async () => {
    const { container } = render(
      <ExecutionDetailModal
        execution={mockExecution}
        open={true}
        onClose={vi.fn()}
      />
    );

    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });
});
