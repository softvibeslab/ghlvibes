# GoHighLevel Clone - Moai-ADK Project

Plataforma de automatización de marketing todo-en-uno, construida con Moai-ADK siguiendo el enfoque SPEC-First.

## Estructura del Proyecto

```
gohighlevel-clone/
├── moai-project.yaml          # Configuración principal del proyecto
├── specs/                     # Especificaciones EARS por módulo
│   ├── crm/
│   │   ├── contacts.yaml      # 8 SPECs - Gestión de contactos
│   │   └── pipelines.yaml     # 5 SPECs - Pipelines de ventas
│   ├── marketing/
│   │   ├── campaigns.yaml     # 10 SPECs - Campañas multicanal
│   │   └── ai-conversations.yaml  # 7 SPECs - IA conversacional
│   ├── funnels/
│   │   ├── builder.yaml       # 10 SPECs - Constructor de páginas
│   │   └── analytics.yaml     # 8 SPECs - Analíticas de conversión
│   ├── bookings/
│   │   └── calendar.yaml      # 12 SPECs - Sistema de reservas
│   ├── memberships/
│   │   └── courses.yaml       # 13 SPECs - Cursos y membresías
│   ├── workflows/
│   │   └── automation.yaml    # 12 SPECs - Automatización
│   ├── whitelabel/
│   │   ├── branding.yaml      # 8 SPECs - Marca blanca
│   │   └── security.yaml      # 11 SPECs - Seguridad
│   └── integrations/
│       └── external-apis.yaml # 11 SPECs - APIs externas
├── docs/                      # Documentación adicional
└── src/                       # Código fuente (generado)
```

## Stack Tecnológico

| Capa | Tecnología | Skill Moai-ADK |
|------|------------|----------------|
| Backend | FastAPI (Python 3.12) | moai-lib-fastapi |
| Frontend | Next.js 14 + Shadcn | moai-lib-nextjs |
| Base de Datos | PostgreSQL (Supabase) | moai-platform-supabase |
| Auth | Clerk | moai-platform-clerk |
| AI | OpenAI + Anthropic | moai-domain-ml |
| Pagos | Stripe | moai-context7-integration |
| SMS/Voz | Twilio | moai-context7-integration |
| Email | SendGrid | moai-context7-integration |

## Módulos y SPECs

### Total: 105+ SPECs en formato EARS

| Módulo | Archivo | SPECs | Prioridad |
|--------|---------|-------|-----------|
| CRM - Contactos | contacts.yaml | 8 | Crítica |
| CRM - Pipelines | pipelines.yaml | 5 | Alta |
| Marketing - Campañas | campaigns.yaml | 10 | Crítica |
| Marketing - IA | ai-conversations.yaml | 7 | Alta |
| Funnels - Builder | builder.yaml | 10 | Alta |
| Funnels - Analytics | analytics.yaml | 8 | Alta |
| Bookings | calendar.yaml | 12 | Alta |
| Memberships | courses.yaml | 13 | Media |
| Workflows | automation.yaml | 12 | Crítica |
| White Label - Branding | branding.yaml | 8 | Alta |
| White Label - Security | security.yaml | 11 | Crítica |
| Integrations | external-apis.yaml | 11 | Alta |

## Fases de Desarrollo

1. **Fase 1: Infraestructura Core**
   - Seguridad y autenticación
   - Integraciones externas base

2. **Fase 2: CRM Foundation**
   - Gestión de contactos
   - Pipelines de ventas

3. **Fase 3: Motor de Comunicación**
   - Campañas multicanal
   - Automatización de workflows

4. **Fase 4: Herramientas de Conversión**
   - Constructor de funnels
   - Sistema de reservas

5. **Fase 5: Monetización**
   - Cursos y membresías
   - Procesamiento de pagos

6. **Fase 6: White Label**
   - Personalización de marca
   - Multi-tenancy

## Comandos Moai-ADK

```bash
# Inicializar proyecto
moai-adk init gohighlevel-clone --locale es

# Planificar implementación de un módulo
moai-adk plan --spec-dir specs/crm/

# Implementar módulo con TDD
moai-adk run --module crm

# Ejecutar tests
moai-adk test --coverage

# Desplegar
moai-adk deploy --env production
```

## Formato EARS

Cada SPEC sigue el formato:

```
When [EVENT],
the system shall [ACTION]
resulting in [RESULT]
in [STATE]
```

## Requisitos TRUST 5

- **T**estable: Cobertura mínima 80%
- **R**eadable: Código documentado y limpio
- **U**nified: Fuente única de verdad
- **S**ecured: Cumplimiento OWASP
- **T**rackable: Versionado semántico
