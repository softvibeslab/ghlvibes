# Contributing to GoHighLevel Clone Frontend

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Focus on what is best for the community
- Show empathy towards other community members

## Development Workflow

### 1. Setup

```bash
# Fork and clone repository
git clone https://github.com/YOUR-USERNAME/gohighlevel-clone.git
cd gohighlevel-clone/frontend

# Install dependencies
npm install

# Create feature branch
git checkout -b feature/your-feature-name
```

### 2. Coding Standards

#### TypeScript
- Use TypeScript for all new files
- Avoid `any` types
- Use strict mode
- Provide return types for functions
- Use interfaces for object shapes

#### React
- Use functional components with hooks
- Follow Rules of Hooks
- Use `React.memo` for expensive components
- Implement proper dependency arrays
- Handle loading and error states

#### Naming Conventions
- Components: PascalCase (e.g., `WorkflowBuilder.tsx`)
- Utilities: camelCase (e.g., `formatDate.ts`)
- Types: PascalCase (e.g., `WorkflowProps`)
- Constants: UPPER_SNAKE_CASE (e.g., `MAX_RETRIES`)
- Files: kebab-case (e.g., `workflow-list.tsx`)

#### File Organization
```
ComponentName/
├── ComponentName.tsx       # Main component
├── ComponentName.test.tsx  # Tests
├── index.ts               # Exports
└── types.ts               # Local types (if needed)
```

### 3. Component Guidelines

#### Accessibility
- Include ARIA labels on all interactive elements
- Implement keyboard navigation
- Support screen readers
- Maintain focus management
- Test with accessibility tools

#### Performance
- Use `React.memo` for expensive renders
- Implement proper memoization
- Lazy load heavy components
- Optimize images and assets
- Code splitting where appropriate

#### Testing
- Write tests for all new components
- Aim for 80%+ code coverage
- Test accessibility with jest-axe
- Include E2E tests for user flows
- Test error states

### 4. Commit Messages

Follow Conventional Commits:

```
<type>(<scope>): <subject>

<body>

<footer>
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks
- `perf`: Performance improvements

Examples:
```bash
feat(workflows): add template marketplace
fix(analytics): correct date range calculation
docs(readme): update installation instructions
test(execution): add E2E tests for execution logs
```

### 5. Pull Request Process

1. **Update Tests**
   - Add tests for new features
   - Update existing tests if needed
   - Ensure all tests pass

2. **Update Documentation**
   - Update README if needed
   - Add JSDoc comments for complex functions
   - Document any breaking changes

3. **Code Quality**
   - Run linter: `npm run lint`
   - Type check: `npm run type-check`
   - Format code: `npm run format`
   - Run tests: `npm run test`

4. **Submit PR**
   - Provide clear description of changes
   - Reference related issues
   - Include screenshots for UI changes
   - Add `Closes #issue-number` to description

5. **Code Review**
   - Address review feedback
   - Keep PRs focused and small
   - Respond to comments promptly

### 6. Testing Requirements

#### Unit Tests
```typescript
describe('ComponentName', () => {
  it('should render correctly', () => {
    // Test implementation
  });

  it('should handle user interaction', async () => {
    // Test user interaction
  });

  it('should not have accessibility violations', async () => {
    // A11y test
  });
});
```

#### E2E Tests
```typescript
test('should complete user flow', async ({ page }) => {
  await page.goto('/workflows');
  await page.click('text=Create Workflow');
  // ... rest of test
});
```

### 7. Documentation

#### Component Documentation
```typescript
/**
 * Component description
 *
 * @param prop1 - Description of prop1
 * @param prop2 - Description of prop2
 *
 * @example
 * ```tsx
 * <ComponentName prop1="value" prop2={123} />
 * ```
 */
```

#### Complex Functions
```typescript
/**
 * Calculates the drop-off rate for workflow steps
 *
 * @param entered - Number of contacts who entered the step
 * @param completed - Number of contacts who completed the step
 * @returns Drop-off rate as a percentage
 *
 * @example
 * ```ts
 * const rate = calculateDropOffRate(1000, 800)
 * // Returns: 20
 * ```
 */
```

### 8. Code Review Checklist

- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] No console errors or warnings
- [ ] Accessible (keyboard navigation, screen reader)
- [ ] Responsive design
- [ ] Loading states handled
- [ ] Error states handled
- [ ] Performance optimized
- [ ] TypeScript types correct
- [ ] Follows coding standards

### 9. Performance Guidelines

#### Bundle Size
- Keep main bundle under 250KB
- Use dynamic imports for routes
- Lazy load heavy components
- Optimize images and assets

#### Runtime Performance
- Use `React.memo` for expensive renders
- Implement proper memoization
- Avoid unnecessary re-renders
- Optimize list rendering with virtualization

### 10. Accessibility Checklist

- [ ] All interactive elements are keyboard accessible
- [ ] ARIA labels on icon-only buttons
- [ ] Proper heading hierarchy
- [ ] Form inputs have labels
- [ ] Color contrast meets WCAG AA (4.5:1)
- [ ] Focus indicators visible
- [ ] Skip links present
- [ ] Screen reader testing completed

## Getting Help

- Open an issue for bugs or feature requests
- Start a discussion for questions
- Check existing documentation
- Review similar PRs for reference

## License

By contributing, you agree that your contributions will be licensed under the same license as the project.
