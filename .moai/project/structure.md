# GoHighLevel Clone - Project Structure

## Directory Overview

```
gohighlevel-clone/
├── .claude/                    # Claude Code configuration
│   ├── agents/moai/           # Agent definitions (20 agents)
│   ├── commands/moai/         # Slash commands (8 commands)
│   ├── hooks/moai/            # Python hooks (10+ hooks)
│   ├── output-styles/moai/    # Response styling (3 styles)
│   ├── rules/                 # Development rules
│   └── skills/                # Skill definitions (60+ skills)
├── .moai/                      # MoAI-ADK configuration
│   ├── announcements/         # Multilingual announcements
│   ├── config/                # Configuration sections
│   └── project/               # Project documentation
├── specs/                      # EARS specifications (11 files, 105+ SPECs)
│   ├── crm/                   # CRM module specs
│   ├── marketing/             # Marketing module specs
│   ├── funnels/               # Funnels module specs
│   ├── bookings/              # Bookings module specs
│   ├── memberships/           # Memberships module specs
│   ├── workflows/             # Workflows module specs
│   ├── whitelabel/            # White Label module specs
│   └── integrations/          # Integrations module specs
├── docs/                       # Documentation (awaiting generation)
├── src/                        # Source code (awaiting implementation)
├── CLAUDE.md                   # Alfred orchestrator directives
├── README.md                   # Project overview (Spanish)
├── moai-project.yaml          # Project configuration
└── .gitignore                  # Git ignore rules
```

---

## Directory Details

### .claude/ - Claude Code Configuration

The `.claude/` directory contains all Claude Code extensions and configurations that power the AI-assisted development workflow.

#### .claude/agents/moai/

Agent definitions for specialized AI assistants. Each agent has a specific expertise domain and toolset.

| Agent | Purpose |
|-------|---------|
| builder-agent.md | Create new agent definitions |
| builder-command.md | Create new slash commands |
| builder-plugin.md | Create new plugins |
| builder-skill.md | Create new skills |
| expert-backend.md | Backend API development |
| expert-debug.md | Debugging and troubleshooting |
| expert-devops.md | CI/CD and infrastructure |
| expert-frontend.md | React/Next.js development |
| expert-performance.md | Performance optimization |
| expert-refactoring.md | Code refactoring |
| expert-security.md | Security analysis |
| expert-testing.md | Test creation and strategy |
| manager-ddd.md | Domain-Driven Development execution |
| manager-docs.md | Documentation generation |
| manager-git.md | Git operations management |
| manager-project.md | Project configuration |
| manager-quality.md | Quality gates and TRUST 5 |
| manager-spec.md | SPEC document creation |
| manager-strategy.md | System design decisions |

#### .claude/commands/moai/

Slash commands for workflow execution.

| Command | Purpose |
|---------|---------|
| 0-project.md | Generate project documentation |
| 1-plan.md | Create SPEC documents (Plan phase) |
| 2-run.md | Execute DDD implementation (Run phase) |
| 3-sync.md | Synchronize documentation (Sync phase) |
| 9-feedback.md | Submit feedback or report issues |
| alfred.md | Autonomous task execution |
| fix.md | Parallel auto-fix scanning |
| loop.md | Autonomous loop until completion |

#### .claude/hooks/moai/

Python hooks for automated quality checks and workflow automation.

| Hook | Trigger | Purpose |
|------|---------|---------|
| post_tool__ast_grep_scan.py | Post-tool | AST-based code scanning |
| post_tool__code_formatter.py | Post-tool | Auto-format code changes |
| post_tool__linter.py | Post-tool | Run linting checks |
| post_tool__lsp_diagnostic.py | Post-tool | LSP diagnostic collection |
| pre_tool__security_guard.py | Pre-tool | Security validation |
| quality_gate_with_lsp.py | Quality gate | LSP-based quality validation |
| session_end__auto_cleanup.py | Session end | Cleanup temporary files |
| session_end__rank_submit.py | Session end | Submit ranking metrics |
| session_start__show_project_info.py | Session start | Display project info |
| stop__loop_controller.py | Stop | Control loop termination |

**Hook Library (.claude/hooks/moai/lib/)**

Supporting utilities for hooks:

| Library | Purpose |
|---------|---------|
| atomic_write.py | Safe file writing |
| checkpoint.py | Checkpoint management |
| config.py | Configuration loading |
| config_manager.py | Configuration management |
| config_validator.py | Configuration validation |
| enhanced_output_style_detector.py | Output style detection |
| exceptions.py | Custom exceptions |
| file_utils.py | File utilities |
| git_collector.py | Git information collection |
| git_operations_manager.py | Git operations |
| language_detector.py | Language detection |
| language_validator.py | Language validation |
| memory_collector.py | Memory management |
| metrics_tracker.py | Metrics tracking |
| models.py | Data models |
| path_utils.py | Path utilities |
| project.py | Project information |
| renderer.py | Output rendering |
| timeout.py | Timeout handling |
| tool_registry.py | Tool registration |
| unified_timeout_manager.py | Unified timeout management |
| update_checker.py | Update checking |
| version_reader.py | Version reading |

#### .claude/output-styles/moai/

Response styling options for different interaction modes.

| Style | Description |
|-------|-------------|
| alfred.md | Professional butler-style responses |
| r2d2.md | Concise, technical responses |
| yoda.md | Wisdom-oriented responses |

#### .claude/skills/

Skill definitions organized by domain. Over 60 skills covering:

- **Foundation skills:** Core principles, Claude Code patterns, memory management
- **Domain skills:** Backend, frontend, database, UI/UX
- **Language skills:** Python, TypeScript, JavaScript, and more
- **Platform skills:** Supabase, Clerk, Vercel, Firebase
- **Library skills:** Nextra, Mermaid, Shadcn
- **Workflow skills:** DDD, testing, documentation generation
- **Tool skills:** AST-grep, data formats

---

### .moai/ - MoAI-ADK Configuration

The `.moai/` directory contains MoAI-ADK specific configuration and state.

#### .moai/announcements/

Multilingual announcement templates for user communication.

#### .moai/config/

Configuration files split by concern:

- Constitution settings (quality requirements)
- Language settings
- User preferences
- Report generation settings

#### .moai/project/

Project documentation (this directory):

| File | Purpose |
|------|---------|
| product.md | Product vision and features |
| structure.md | Directory structure (this file) |
| tech.md | Technology stack and architecture |

---

### specs/ - EARS Specifications

The `specs/` directory contains all feature specifications in EARS format, organized by module.

#### specs/crm/

| File | SPECs | Description |
|------|-------|-------------|
| contacts.yaml | 8 | Contact management (create, import, search, tag, opt-out, sync, delete) |
| pipelines.yaml | 5 | Sales pipeline management |

#### specs/marketing/

| File | SPECs | Description |
|------|-------|-------------|
| campaigns.yaml | 10 | Multi-channel campaign execution |
| ai-conversations.yaml | 7 | AI-powered conversational marketing |

#### specs/funnels/

| File | SPECs | Description |
|------|-------|-------------|
| builder.yaml | 10 | Visual page builder and publishing |
| analytics.yaml | 8 | Conversion tracking and optimization |

#### specs/bookings/

| File | SPECs | Description |
|------|-------|-------------|
| calendar.yaml | 12 | Calendar management and scheduling |

#### specs/memberships/

| File | SPECs | Description |
|------|-------|-------------|
| courses.yaml | 13 | Course creation and membership management |

#### specs/workflows/

| File | SPECs | Description |
|------|-------|-------------|
| automation.yaml | 12 | Visual workflow builder with 50+ triggers |

#### specs/whitelabel/

| File | SPECs | Description |
|------|-------|-------------|
| branding.yaml | 8 | White-label customization |
| security.yaml | 11 | Security and authentication |

#### specs/integrations/

| File | SPECs | Description |
|------|-------|-------------|
| external-apis.yaml | 11 | OAuth, webhooks, and external integrations |

---

### docs/ - Documentation

The `docs/` directory will contain generated documentation after implementation:

```
docs/                           # (Planned structure)
├── api/                       # API reference documentation
│   ├── openapi.yaml          # OpenAPI specification
│   └── endpoints/            # Endpoint documentation
├── guides/                    # User guides
│   ├── getting-started.md    # Quick start guide
│   ├── configuration.md      # Configuration guide
│   └── tutorials/            # Step-by-step tutorials
├── architecture/              # Architecture documentation
│   ├── overview.md           # System overview
│   ├── database.md           # Database schema
│   └── diagrams/             # Mermaid diagrams
└── changelog/                 # Version history
    └── CHANGELOG.md          # Change log
```

---

### src/ - Source Code

The `src/` directory will contain the application source code after implementation:

```
src/                            # (Planned structure)
├── backend/                   # FastAPI backend
│   ├── api/                  # API routes
│   ├── core/                 # Core utilities
│   ├── domain/               # Domain models
│   ├── infrastructure/       # External services
│   └── tests/                # Backend tests
├── frontend/                  # Next.js frontend
│   ├── app/                  # App router pages
│   ├── components/           # React components
│   ├── hooks/                # Custom hooks
│   ├── lib/                  # Utility libraries
│   └── tests/                # Frontend tests
└── shared/                    # Shared code
    ├── types/                # TypeScript types
    └── constants/            # Shared constants
```

---

### Root Files

| File | Purpose |
|------|---------|
| CLAUDE.md | Alfred orchestrator directives and execution rules |
| README.md | Project overview in Spanish |
| moai-project.yaml | Project configuration (stack, modules, phases) |
| .gitignore | Git ignore patterns |
| .mcp.json | MCP server configuration |

---

## Key File Locations

### Configuration Files

| Purpose | Location |
|---------|----------|
| Project configuration | /moai-project.yaml |
| Alfred directives | /CLAUDE.md |
| MCP servers | /.mcp.json |
| Git ignore | /.gitignore |
| Quality constitution | /.moai/config/constitution.yaml |
| Language settings | /.moai/config/language.yaml |

### SPEC Files

| Module | Location |
|--------|----------|
| CRM | /specs/crm/*.yaml |
| Marketing | /specs/marketing/*.yaml |
| Funnels | /specs/funnels/*.yaml |
| Bookings | /specs/bookings/*.yaml |
| Memberships | /specs/memberships/*.yaml |
| Workflows | /specs/workflows/*.yaml |
| White Label | /specs/whitelabel/*.yaml |
| Integrations | /specs/integrations/*.yaml |

### Agent Definitions

| Type | Location |
|------|----------|
| All agents | /.claude/agents/moai/*.md |
| Builder agents | /.claude/agents/moai/builder-*.md |
| Expert agents | /.claude/agents/moai/expert-*.md |
| Manager agents | /.claude/agents/moai/manager-*.md |

### Slash Commands

| Command | Location |
|---------|----------|
| All commands | /.claude/commands/moai/*.md |
| Workflow commands | /.claude/commands/moai/[0-3]-*.md |
| Utility commands | /.claude/commands/moai/{alfred,fix,loop}.md |

### Skills

| Domain | Location |
|--------|----------|
| All skills | /.claude/skills/*/SKILL.md |
| Foundation | /.claude/skills/moai-foundation-*/SKILL.md |
| Domain | /.claude/skills/moai-domain-*/SKILL.md |
| Language | /.claude/skills/moai-lang-*/SKILL.md |
| Platform | /.claude/skills/moai-platform-*/SKILL.md |

---

## Module Organization

The project follows a modular monorepo structure where each business domain (CRM, Marketing, Funnels, etc.) has:

1. **SPEC files** in `/specs/{module}/` defining requirements
2. **Backend code** (planned) in `/src/backend/domain/{module}/`
3. **Frontend code** (planned) in `/src/frontend/app/{module}/`
4. **Tests** co-located with source files

This structure enables:

- Clear domain boundaries
- Independent module development
- Parallel team work
- Incremental deployment
