import { describe, it, expect, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { TemplateGallery } from '@/components/templates/template-gallery';
import { TemplateCard } from '@/components/templates/template-card';
import { WorkflowTemplate } from '@/lib/types/workflow';
import { axe, toHaveNoViolations } from 'jest-axe';

expect.extend(toHaveNoViolations);

describe('TemplateGallery', () => {
  const mockTemplates: WorkflowTemplate[] = [
    {
      id: 't1',
      name: 'Lead Nurturing',
      description: 'Nurture leads through email campaigns',
      category: 'Lead Nurturing',
      use_case: 'Convert leads into customers',
      preview_image_url: '/preview1.jpg',
      workflow_definition: {},
      rating: 4.5,
      usage_count: 1200,
      required_integrations: ['Email', 'CRM'],
      created_at: '2025-01-01T00:00:00Z',
      featured: true,
    },
    {
      id: 't2',
      name: 'Onboarding Flow',
      description: 'Welcome new users',
      category: 'Onboarding',
      use_case: 'User onboarding',
      preview_image_url: '/preview2.jpg',
      workflow_definition: {},
      rating: 4.8,
      usage_count: 850,
      required_integrations: ['Email'],
      created_at: '2025-01-02T00:00:00Z',
      featured: false,
    },
  ];

  it('should render template gallery', () => {
    render(
      <TemplateGallery
        templates={mockTemplates}
        onInstantiate={vi.fn()}
      />
    );

    expect(screen.getByText('Lead Nurturing')).toBeInTheDocument();
    expect(screen.getByText('Onboarding Flow')).toBeInTheDocument();
  });

  it('should filter templates by category', async () => {
    const user = userEvent.setup();

    render(
      <TemplateGallery
        templates={mockTemplates}
        onInstantiate={vi.fn()}
      />
    );

    const categorySelect = screen.getByLabelText(/filter by category/i);
    await user.click(categorySelect);

    const onboardingOption = screen.getByText('Onboarding');
    await user.click(onboardingOption);

    await waitFor(() => {
      expect(screen.queryByText('Lead Nurturing')).not.toBeInTheDocument();
      expect(screen.getByText('Onboarding Flow')).toBeInTheDocument();
    });
  });

  it('should search templates', async () => {
    const user = userEvent.setup();

    render(
      <TemplateGallery
        templates={mockTemplates}
        onInstantiate={vi.fn()}
      />
    );

    const searchInput = screen.getByPlaceholderText(/search templates/i);
    await user.type(searchInput, 'Onboarding');

    await waitFor(() => {
      expect(screen.queryByText('Lead Nurturing')).not.toBeInTheDocument();
      expect(screen.getByText('Onboarding Flow')).toBeInTheDocument();
    });
  });

  it('should filter featured templates', async () => {
    const user = userEvent.setup();

    render(
      <TemplateGallery
        templates={mockTemplates}
        onInstantiate={vi.fn()}
      />
    );

    const featuredButton = screen.getByRole('button', { name: /featured/i });
    await user.click(featuredButton);

    await waitFor(() => {
      expect(screen.getByText('Lead Nurturing')).toBeInTheDocument();
      expect(screen.queryByText('Onboarding Flow')).not.toBeInTheDocument();
    });
  });

  it('should show template count', () => {
    render(
      <TemplateGallery
        templates={mockTemplates}
        onInstantiate={vi.fn()}
      />
    );

    expect(screen.getByText('2 templates found')).toBeInTheDocument();
  });
});

describe('TemplateCard', () => {
  const mockTemplate: WorkflowTemplate = {
    id: 't1',
    name: 'Lead Nurturing',
    description: 'Nurture leads through email campaigns',
    category: 'Lead Nurturing',
    use_case: 'Convert leads into customers',
    preview_image_url: '/preview.jpg',
    workflow_definition: {},
    rating: 4.5,
    usage_count: 1200,
    required_integrations: ['Email', 'CRM'],
    created_at: '2025-01-01T00:00:00Z',
    featured: true,
  };

  it('should render template card', () => {
    render(<TemplateCard template={mockTemplate} onSelect={vi.fn()} />);

    expect(screen.getByText('Lead Nurturing')).toBeInTheDocument();
    expect(screen.getByText(/nurture leads/i)).toBeInTheDocument();
    expect(screen.getByText('Lead Nurturing')).toBeInTheDocument();
  });

  it('should display usage count and rating', () => {
    render(<TemplateCard template={mockTemplate} onSelect={vi.fn()} />);

    expect(screen.getByText('1,200')).toBeInTheDocument();
    expect(screen.getByText('4.5')).toBeInTheDocument();
  });

  it('should show featured badge', () => {
    render(<TemplateCard template={mockTemplate} onSelect={vi.fn()} />);

    expect(screen.getByText('Featured')).toBeInTheDocument();
  });

  it('should call onSelect when clicked', async () => {
    const user = userEvent.setup();
    const handleSelect = vi.fn();

    render(<TemplateCard template={mockTemplate} onSelect={handleSelect} />);

    const card = screen.getByRole('button', { name: /preview lead nurturing template/i });
    await user.click(card);

    expect(handleSelect).toHaveBeenCalledTimes(1);
  });

  it('should be keyboard accessible', async () => {
    const user = userEvent.setup();
    const handleSelect = vi.fn();

    render(<TemplateCard template={mockTemplate} onSelect={handleSelect} />);

    const card = screen.getByRole('button');
    card.focus();
    await user.keyboard('{Enter}');

    expect(handleSelect).toHaveBeenCalledTimes(1);
  });

  it('should not have accessibility violations', async () => {
    const { container } = render(
      <TemplateCard template={mockTemplate} onSelect={vi.fn()} />
    );

    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });
});
