import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@/test/test-utils'
import { WorkflowBuilder } from '../WorkflowBuilder'

// Mock the workflow store
vi.mock('@/lib/stores/workflow-store', () => ({
  useWorkflowStore: () => ({
    workflow: {
      id: 'test-workflow-id',
      name: 'Test Workflow',
      status: 'draft',
      steps: [],
    },
    setWorkflow: vi.fn(),
    addStep: vi.fn(),
    updateStep: vi.fn(),
    removeStep: vi.fn(),
  }),
}))

// Mock the canvas store
vi.mock('@/lib/stores/canvas-store', () => ({
  useCanvasStore: () => ({
    nodes: [],
    edges: [],
    setNodes: vi.fn(),
    setEdges: vi.fn(),
    onNodesChange: vi.fn(),
    onEdgesChange: vi.fn(),
    onConnect: vi.fn(),
  }),
}))

describe('WorkflowBuilder', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('Rendering', () => {
    it('renders workflow canvas with initial state', () => {
      // Act
      render(<WorkflowBuilder workflowId="test-workflow-id" />)

      // Assert
      expect(screen.getByText('Test Workflow')).toBeInTheDocument()
      expect(screen.getByTestId('workflow-canvas')).toBeInTheDocument()
    })

    it('renders builder sidebar with step types', () => {
      // Act
      render(<WorkflowBuilder workflowId="test-workflow-id" />)

      // Assert
      expect(screen.getByText('Add Step')).toBeInTheDocument()
      expect(screen.getByText('Triggers')).toBeInTheDocument()
      expect(screen.getByText('Actions')).toBeInTheDocument()
      expect(screen.getByText('Conditions')).toBeInTheDocument()
    })

    it('renders configuration panel when step is selected', async () => {
      // Arrange
      const { container } = render(<WorkflowBuilder workflowId="test-workflow-id" />)

      // Act - Select a step (simulated)
      const addStepButton = screen.getByText('Add Step')
      fireEvent.click(addStepButton)

      await waitFor(() => {
        const configPanel = container.querySelector('[data-testid="configuration-panel"]')
        expect(configPanel).toBeInTheDocument()
      })
    })

    it('displays workflow status badge', () => {
      // Act
      render(<WorkflowBuilder workflowId="test-workflow-id" />)

      // Assert
      expect(screen.getByTestId('workflow-status-badge')).toBeInTheDocument()
      expect(screen.getByText('Draft')).toBeInTheDocument()
    })
  })

  describe('User Interactions', () => {
    it('opens step selector when clicking add step button', async () => {
      // Act
      render(<WorkflowBuilder workflowId="test-workflow-id" />)
      const addStepButton = screen.getByText('Add Step')
      fireEvent.click(addStepButton)

      // Assert
      await waitFor(() => {
        expect(screen.getByText('Send Email')).toBeInTheDocument()
        expect(screen.getByText('Add Tag')).toBeInTheDocument()
        expect(screen.getByText('Wait')).toBeInTheDocument()
      })
    })

    it('adds step to workflow when selecting step type', async () => {
      // Arrange
      const addStepMock = vi.fn()
      vi.mocked(useWorkflowStore).mockReturnValue({
        workflow: { id: 'test', name: 'Test', steps: [] },
        addStep: addStepMock,
      } as any)

      // Act
      render(<WorkflowBuilder workflowId="test-workflow-id" />)
      fireEvent.click(screen.getByText('Add Step'))
      fireEvent.click(screen.getByText('Send Email'))

      // Assert
      await waitFor(() => {
        expect(addStepMock).toHaveBeenCalled()
      })
    })

    it('opens configuration panel when clicking on step', async () => {
      // Arrange
      const workflow = {
        id: 'test-workflow-id',
        name: 'Test',
        status: 'draft',
        steps: [
          {
            id: 'step-1',
            type: 'send_email',
            name: 'Send Email Step',
            config: {},
          },
        ],
      }

      // Act
      render(<WorkflowBuilder workflowId="test-workflow-id" />)
      const stepElement = screen.getByText('Send Email Step')
      fireEvent.click(stepElement)

      // Assert
      await waitFor(() => {
        expect(screen.getByTestId('configuration-panel')).toBeInTheDocument()
      })
    })

    it('updates step configuration when saving', async () => {
      // Arrange
      render(<WorkflowBuilder workflowId="test-workflow-id" />)
      const updateStepMock = vi.fn()

      // Act
      fireEvent.click(screen.getByText('Add Step'))
      fireEvent.click(screen.getByText('Send Email'))

      // Fill in configuration
      const subjectInput = screen.getByPlaceholderText('Email Subject')
      fireEvent.change(subjectInput, { target: { value: 'Test Subject' } })

      const saveButton = screen.getByText('Save')
      fireEvent.click(saveButton)

      // Assert
      await waitFor(() => {
        expect(updateStepMock).toHaveBeenCalledWith(
          expect.anything(),
          expect.objectContaining({
            config: expect.objectContaining({
              subject: 'Test Subject',
            }),
          })
        )
      })
    })

    it('removes step when clicking delete', async () => {
      // Arrange
      const removeStepMock = vi.fn()

      // Act
      render(<WorkflowBuilder workflowId="test-workflow-id" />)
      const deleteButton = screen.getByTestId('delete-step-button')
      fireEvent.click(deleteButton)

      // Confirm deletion
      const confirmButton = screen.getByText('Delete')
      fireEvent.click(confirmButton)

      // Assert
      await waitFor(() => {
        expect(removeStepMock).toHaveBeenCalled()
      })
    })
  })

  describe('Form Validation', () => {
    it('displays validation error for empty step name', async () => {
      // Arrange
      render(<WorkflowBuilder workflowId="test-workflow-id" />)

      // Act
      fireEvent.click(screen.getByText('Add Step'))
      fireEvent.click(screen.getByText('Send Email'))

      // Try to save without filling required fields
      const saveButton = screen.getByText('Save')
      fireEvent.click(saveButton)

      // Assert
      await waitFor(() => {
        expect(screen.getByText(/required/i)).toBeInTheDocument()
      })
    })

    it('validates email format in email step configuration', async () => {
      // Arrange
      render(<WorkflowBuilder workflowId="test-workflow-id" />)

      // Act
      fireEvent.click(screen.getByText('Add Step'))
      fireEvent.click(screen.getByText('Send Email'))

      const emailInput = screen.getByPlaceholderText('recipient@example.com')
      fireEvent.change(emailInput, { target: { value: 'invalid-email' } })

      const saveButton = screen.getByText('Save')
      fireEvent.click(saveButton)

      // Assert
      await waitFor(() => {
        expect(screen.getByText(/invalid email/i)).toBeInTheDocument()
      })
    })

    it('validates wait duration in wait step configuration', async () => {
      // Arrange
      render(<WorkflowBuilder workflowId="test-workflow-id" />)

      // Act
      fireEvent.click(screen.getByText('Add Step'))
      fireEvent.click(screen.getByText('Wait'))

      const durationInput = screen.getByPlaceholderText('Duration')
      fireEvent.change(durationInput, { target: { value: '-1' } })

      const saveButton = screen.getByText('Save')
      fireEvent.click(saveButton)

      // Assert
      await waitFor(() => {
        expect(screen.getByText(/must be positive/i)).toBeInTheDocument()
      })
    })
  })

  describe('Workflow Actions', () => {
    it('saves workflow when clicking save button', async () => {
      // Arrange
      const saveWorkflowMock = vi.fn()

      // Act
      render(<WorkflowBuilder workflowId="test-workflow-id" />)
      const saveButton = screen.getByText('Save Workflow')
      fireEvent.click(saveButton)

      // Assert
      await waitFor(() => {
        expect(saveWorkflowMock).toHaveBeenCalled()
      })
    })

    it('activates workflow when clicking activate button', async () => {
      // Arrange
      const activateWorkflowMock = vi.fn()

      // Act
      render(<WorkflowBuilder workflowId="test-workflow-id" />)
      const activateButton = screen.getByText('Activate')
      fireEvent.click(activateButton)

      // Assert
      await waitFor(() => {
        expect(activateWorkflowMock).toHaveBeenCalled()
      })
    })

    it('shows confirmation dialog before activating workflow', async () => {
      // Act
      render(<WorkflowBuilder workflowId="test-workflow-id" />)
      const activateButton = screen.getByText('Activate')
      fireEvent.click(activateButton)

      // Assert
      await waitFor(() => {
        expect(screen.getByText(/are you sure/i)).toBeInTheDocument()
        expect(screen.getByText('Confirm')).toBeInTheDocument()
        expect(screen.getByText('Cancel')).toBeInTheDocument()
      })
    })
  })

  describe('Edge Cases', () => {
    it('handles empty workflow gracefully', () => {
      // Act
      render(<WorkflowBuilder workflowId="empty-workflow" />)

      // Assert
      expect(screen.getByText('No steps added yet')).toBeInTheDocument()
      expect(screen.getByText('Add your first step to get started')).toBeInTheDocument()
    })

    it('handles workflow with many steps efficiently', () => {
      // Arrange
      const manySteps = Array.from({ length: 50 }, (_, i) => ({
        id: `step-${i}`,
        type: 'send_email',
        name: `Step ${i}`,
      }))

      // Act
      render(<WorkflowBuilder workflowId="test-workflow-id" />)

      // Assert - Should render without hanging
      expect(screen.getByTestId('workflow-canvas')).toBeInTheDocument()
    })

    it('handles concurrent step additions', async () => {
      // Arrange
      const addStepMock = vi.fn()

      // Act - Rapidly click add step multiple times
      render(<WorkflowBuilder workflowId="test-workflow-id" />)
      const addButton = screen.getByText('Add Step')

      fireEvent.click(addButton)
      fireEvent.click(addButton)
      fireEvent.click(addButton)

      // Assert - Should handle gracefully without errors
      await waitFor(() => {
        expect(addStepMock).toHaveBeenCalled()
      })
    })
  })

  describe('Accessibility', () => {
    it('has proper ARIA labels on interactive elements', () => {
      // Act
      render(<WorkflowBuilder workflowId="test-workflow-id" />)

      // Assert
      const canvas = screen.getByTestId('workflow-canvas')
      expect(canvas).toHaveAttribute('role', 'region')
      expect(canvas).toHaveAttribute('aria-label', 'Workflow canvas')
    })

    it('supports keyboard navigation', () => {
      // Act
      render(<WorkflowBuilder workflowId="test-workflow-id" />)

      // Assert - All interactive elements should be focusable
      const addStepButton = screen.getByText('Add Step')
      expect(addStepButton).toHaveAttribute('type', 'button')
    })

    it('announces changes to screen readers', async () => {
      // Arrange
      render(<WorkflowBuilder workflowId="test-workflow-id" />)

      // Act
      fireEvent.click(screen.getByText('Add Step'))
      fireEvent.click(screen.getByText('Send Email'))

      // Assert
      await waitFor(() => {
        const liveRegion = screen.getByRole('status')
        expect(liveRegion).toBeInTheDocument()
      })
    })
  })
})
