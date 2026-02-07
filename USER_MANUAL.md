# 📘 GoHighLevel Clone - Manual de Usuario

**Versión:** 1.0.0
**Última actualización:** 2026-02-07
**Nivel:** Principiante a Intermedio

---

## 📖 Tabla de Contenidos

1. [Introducción](#introducción)
2. [Primeros Pasos](#primeros-pasos)
3. [Gestión de Workflows](#gestión-de-workflows)
4. [CRM y Gestión de Contacts](#crm-y-gestión-de-contacts)
5. [Marketing Campaigns](#marketing-campaigns)
6. [Funnels de Conversión](#funnels-de-conversión)
7. [Calendario y Citas](#calendario-y-citas)
8. [Analytics y Reportes](#analytics-y-reportes)
9. [Configuración](#configuración)
10. [Solución de Problemas](#solución-de-problemas)

---

## Introducción

### ¿Qué es GoHighLevel Clone?

GoHighLevel Clone es una plataforma **todo-en-uno** de automatización de marketing y CRM que te permite:

- 🔄 **Automatizar** procesos de marketing y ventas
- 👥 **Gestionar** contacts, deals, y empresas
- 📧 **Enviar** campaigns de email y SMS
- 🎯 **Crear** funnels de conversión
- 📅 **Programar** citas y reuniones
- 📊 **Analizar** performance con dashboards en tiempo real

### Conceptos Básicos

#### ¿Qué es un Workflow?
Un **workflow** es una automatización que se dispara basado en un **trigger** (evento) y ejecuta una serie de **actions** (acciones).

**Ejemplo:**
- **Trigger:** Un nuevo contact se crea
- **Actions:**
  1. Enviar email de bienvenida
  2. Agregar tag "nuevo lead"
  3. Crear tarea de seguimiento
  4. Notificar al equipo de ventas

#### ¿Qué es un Funnel?
Un **funnel** (embudo) es una secuencia de páginas diseñada para convertir visitantes en leads o clientes.

**Ejemplo:**
1. **Página 1:** Landing page con oferta
2. **Página 2:** Formulario de registro
3. **Página 3:** Checkout/pago
4. **Página 4:** Página de agradecimiento

#### ¿Qué es un Deal?
Un **deal** (oportunidad) representa una venta potencial que avanza a través de un **pipeline** de ventas.

**Etapas típicas:**
- Nuevo → Contactado → Calificado → Propuesta → Negociación → Ganado/Perdido

---

## Primeros Pasos

### Crear tu Cuenta

1. **Ir a:** `https://app.gohighlevel.com/signup`
2. **Ingresar datos:**
   - Nombre completo
   - Email corporativo
   - Contraseña segura
3. **Verificar email:** Revisa tu bandeja de entrada
4. **Iniciar sesión:** Usar email y contraseña

### Configurar tu Perfil

1. **Ir a:** Settings → Profile
2. **Configurar:**
   - Foto de perfil
   - Zona horaria
   - Idioma preferido
   - Notificaciones por email

### Crear tu Primer Workflow

**Objetivo:** Enviar email de bienvenida a nuevos contacts.

1. **Ir a:** Workflows → Create Workflow
2. **Nombre:** "Welcome Email Sequence"
3. **Trigger:** Seleccionar "Contact Created"
4. **Actions:**
   - Click "Add Action"
   - Seleccionar "Send Email"
   - Asunto: "Bienvenido a nuestra comunidad"
   - Cuerpo: "Hola {{first_name}}, gracias por unirte..."
   - Click "Save"

5. **Activar:**
   - Click en "Activate"
   - Confirmar activación

¡Tu primer workflow está activo! 🎉

---

## Gestión de Workflows

### Crear un Workflow

1. **Navegar a:** Workflows → All Workflows
2. **Click:** "Create Workflow" button
3. **Completar campos:**
   - **Nombre:** Descriptivo y único
   - **Descripción:** Explica el propósito
   - **Trigger:** Selecciona el evento que inicia el workflow

### Configurar Triggers

#### Tipos de Triggers Disponibles

**Contact Triggers:**
- `contact.created` - Nuevo contact creado
- `contact.updated` - Contact actualizado
- `contact.tag_added` - Tag agregada
- `contact.converted` - Contact convertido

**Workflow Triggers:**
- `workflow.completed` - Workflow completado
- `workflow.step_completed` - Paso completado

**Funnel Triggers:**
- `funnel.page_viewed` - Página de funnel vista
- `funnel.lead captured` - Lead capturado

**Time Triggers:**
- `time.scheduled` - A una hora específica
- `time.recurring` - Recurrente (diario, semanal, mensual)

#### Configurar Trigger con Filtros

```json
{
  "type": "contact.created",
  "filters": {
    "tags": ["new-lead"],
    "custom_fields": {
      "source": "website"
    }
  }
}
```

### Agregar Actions

#### Tipos de Actions

**Communication:**
- `send_email` - Enviar email
- `send_sms` - Enviar SMS
- `send_notification` - Notificar al equipo

**CRM:**
- `add_tag` - Agregar tag
- `remove_tag` - Remover tag
- `create_task` - Crear tarea
- `update_deal` - Actualizar deal

**Timing:**
- `wait` - Esperar X minutos/horas/días
- `wait_until_date` - Esperar hasta fecha específica

**Logic:**
- `condition` - Evaluar condición (if/else)
- `branch` - Ramificar workflow
- `loop` - Iterar sobre items

**Integrations:**
- `webhook` - Llamar webhook externo
- `api_call` - Llamar API REST

#### Ejemplo: Configurar Wait Action

```
Type: Wait
Duration: 2 days
Description: "Give them time to read the email"
```

### Configurar Goals

Los **goals** definen cuándo un workflow se considera "exitoso".

**Ejemplos:**
- Contact abre email dentro de 24 horas
- Contact hace clic en enlace
- Contact completa formulario
- Deal alcanza etapa específica

### Probar Workflow

1. **Ir a:** Workflows → Select Workflow
2. **Click:** "Test Workflow"
3. **Seleccionar contact de prueba**
4. **Click:** "Run Test"
5. **Verificar:** Revisar tab "Execution Logs"

### Monitorear Ejecuciones

**Ver logs en tiempo real:**
- Ir a: Workflows → Select Workflow
- Tab: "Execution Logs"
- Ver actualizaciones automáticas (SSE)

**Métricas disponibles:**
- Total enrollments
- Completados
- Drop-offs
- Tiempo promedio de completion

---

## CRM y Gestión de Contacts

### Agregar Contacts

#### Manualmente

1. **Ir a:** CRM → Contacts
2. **Click:** "Add Contact"
3. **Completar:**
   - Email (requerido)
   - Nombre
   - Apellido
   - Teléfono
   - Empresa (opcional)
   - Tags
   - Custom fields

#### Importar CSV

1. **Preparar CSV** con columnas:
   ```
   email,first_name,last_name,phone,company,tags
   john@example.com,John,Doe,+1234567890,ACME,"vip,lead"
   ```

2. **Ir a:** CRM → Contacts → Import
3. **Upload CSV file**
4. **Map columns** (mapear columnas del CSV a campos del sistema)
5. **Review** y confirmar

### Organizar Contacts con Tags

#### Crear Tags

1. **Ir a:** CRM → Tags
2. **Click:** "Create Tag"
3. **Configurar:**
   - Nombre: "VIP Client"
   - Color: Seleccionar color

#### Asignar Tags

**Individual:**
- Abrir contact → Sección Tags → Seleccionar tag

**Bulk:**
- Contacts → Seleccionar contacts (checkboxes)
- Actions → Add Tags → Seleccionar tags

### Gestión de Pipelines y Deals

#### Crear Pipeline

1. **Ir a:** CRM → Pipelines
2. **Click:** "Create Pipeline"
3. **Nombre:** "Sales Process 2024"
4. **Agregar stages:**
   - Stage 1: New Lead
   - Stage 2: Qualified
   - Stage 3: Proposal
   - Stage 4: Negotiation
   - Stage 5: Won

#### Crear Deal

1. **Ir a:** CRM → Deals → Create Deal
2. **Completar:**
   - Deal name (requerido)
   - Contact (opcional)
   - Pipeline (requerido)
   - Stage
   - Value
   - Expected close date

#### Mover Deals entre Stages

**Kanban View:**
- Arrastrar deal card de una columna a otra

**List View:**
- Abrir deal → Actions → Move to Stage → Seleccionar stage

### Gestión de Companies

#### Crear Company

1. **Ir a:** CRM → Companies
2. **Click:** "Add Company"
3. **Completar:**
   - Nombre (requerido)
   - Dominio (website)
   - Industria
   - Tamaño (empleados)
   - Dirección

#### Asociar Contacts a Company

**Desde Contact:**
- Abrir contact → Edit → Seleccionar Company

**Desde Company:**
- Abrir company → Tab Contacts → Add Contact

### Gestión de Tasks y Activities

#### Crear Task

1. **Ir a:** CRM → Tasks
2. **Click:** "Add Task"
3. **Configurar:**
   - Título (requerido)
   - Descripción
   - Asignado a
   - Due date
   - Prioridad (Alta, Media, Baja)
   - Tipo (Llamada, Email, Reunión)

#### Completar Task

- Tasks → Seleccionar task → Click checkbox
- O abrir task → Mark as Complete

### Notes y Communications

#### Agregar Note

1. **Ir a:** Contact → Tab Notes
2. **Click:** "Add Note"
3. **Completar:**
   - Contenido
   - Tipo (Note, Email Call, SMS)
   - Asociar a deal/contacto

---

## Marketing Campaigns

### Crear Email Campaign

1. **Ir a:** Marketing → Campaigns → Create Campaign
2. **Tipo:** Email Campaign
3. **Configurar:**
   - **Nombre:** "Newsletter Febrero"
   - **Asunto:** "Tus novedades de este mes"
   - **Lista:** Seleccionar lista de contacts
   - **Template:** Seleccionar o crear desde cero

#### Diseñar Email

**Editor Visual:**
- Drag-and-drop elementos (texto, imágenes, botones)
- Personalizar con variables: `{{first_name}}`, `{{email}}`
- Vista previa móvil/desktop

#### Programar Envío

- **Inmediato:** Send now
- **Programado:** Schedule para fecha/hora específica
- **Recurrente:** Daily, weekly, monthly

### Crear SMS Campaign

1. **Ir a:** Marketing → Campaigns → Create Campaign
2. **Tipo:** SMS Campaign
3. **Mensaje:** "Hola {{first_name}}, tu oferta expira pronto"
4. **Recipients:** Seleccionar segmento

**Límites:**
- 160 caracteres por mensaje
- Respetar hora local del recipient
- Frequency caps (max X mensajes por día)

### Crear Form

1. **Ir a:** Marketing → Forms → Create Form
2. **Nombre:** "Lead Magnet Download"
3. **Agregar campos:**
   - Nombre (Text)
   - Email (Email)
   - Teléfono (Phone)
   - Empresa (Text)
   - Mensaje (Textarea)

#### Configurar Form

- **After submit:** Redirigir a página de agradecimiento
- **Webhook:** Enviar datos a URL externa
- **Email notification:** Notificar al equipo

---

## Funnels de Conversión

### Crear Funnel

1. **Ir a:** Funnels → Create Funnel
2. **Nombre:** "Product Launch Funnel"
3. **Objetivo:** Select goal (Sale, Lead, Registration)

### Agregar Páginas

#### Crear Landing Page

1. **Click:** "Add Page"
2. **Template:** Seleccionar template o blank page
3. **Editor Visual:**
   - **Header:** Logo, navegación
   - **Hero Section:** Título, subtítulo, CTA button
   - **Features:** 3 columnas con iconos
   - **Social Proof:** Testimonios
   - **Footer:** Links, copyright

#### Configurar Page

- **SEO Settings:** Meta title, description, OG image
- **Advanced:** Custom CSS, tracking scripts

### Configurar Elementos de Página

#### Elementos Disponibles

**Basics:**
- Text block
- Image
- Video (YouTube, Vimeo)
- Button
- Divider

**Form Elements:**
- Input field
- Textarea
- Dropdown
- Checkbox/Radio
- File upload

**Advanced:**
- Countdown timer
- Progress bar
- Social share buttons
- Embed code

### Configurar Checkout

1. **Ir a:** Funnel → Add Checkout Step
2. **Configurar:**
   - Producto o servicio
   - Precio
   - Campos de facturación
   - Payment gateway (Stripe)

#### Order Bumps

**One-click upsell:** Ofrecer producto adicional antes de checkout
```
"Wait! Don't miss this special offer..."
+ Add to order ($47)
```

### Configurar Analytics

#### Habilitar Tracking

1. **Ir a:** Funnels → Select Funnel → Analytics
2. **Métricas automáticas:**
   - Page views
   - Conversion rate
   - Drop-off rate
   - Revenue

#### Eventos Personalizados

```javascript
// Track custom event
gohighlevel.track('custom_event', {
  funnel_id: 'uuid',
  page_id: 'uuid',
  event_name: 'button_clicked',
  element_id: 'cta-button'
});
```

---

## Calendario y Citas

### Crear Calendario

1. **Ir a:** Calendars → Create Calendar
2. **Configurar:**
   - **Nombre:** "Sales Calls"
   - **Timezone:** Seleccionar zona horaria
   - **Availability:** Configurar horas disponibles

### Configurar Disponibilidad

#### Horario de Trabajo

```
Lunes a Viernes: 9:00 AM - 6:00 PM
Sábados: 10:00 AM - 2:00 PM
Domingos: Cerrado
```

#### Configurar Bloques de Tiempo

- **Duration:** 15 min, 30 min, 60 min
- **Buffer time:** 15 min entre citas
- **Breaks:** Hora de lunch (12-1 PM)

### Crear Booking Widget

1. **Ir a:** Calendars → Booking Widgets → Create Widget
2. **Configurar:**
   - **Nombre:** "Discovery Call"
   - **Calendar:** Seleccionar calendario
   - **Diseño:** Colores, branding
   - **Campos:** Nombre, email, teléfono

#### Embed Widget

**Código embed:**
```html
<script src="https://app.gohighlevel.com/widget/booking.js"
  data-calendar-id="uuid"
  data-theme="light">
</script>
```

### Gestionar Citas

#### Ver Agenda

1. **Ir a:** Calendars → Select Calendar → Agenda
2. **Vista:** Calendar view con citas

#### Acciones en Cita

- **Confirmar:** Confirm appointment
- **Cancelar:** Cancel appointment (envía email de cancelación)
- **Reschedule:** Cambiar fecha/hora

---

## Analytics y Reportes

### Dashboard Principal

**Acceder a:** Dashboard → Overview

**Métricas principales:**
- Total contacts
- Active workflows
- Open deals
- Revenue mes actual
- Conversion rate

### Workflow Analytics

**Acceder a:** Workflows → Select Workflow → Analytics

**Métricas:**
- Total enrollments
- Completion rate
- Drop-off por step
- Average completion time
- Goal achievement rate

### Funnel Analytics

**Acceder a:** Funnels → Select Funnel → Analytics

**Métricas:**
- Visitas totales
- Conversion rate
- Revenue por funnel
- Top traffic sources
- Device breakdown (mobile/desktop)

### Exportar Reportes

**Formatos disponibles:**
- CSV (Excel compatible)
- JSON (para integración)
- PDF (para presentación)

**Exportar:**
1. Ir a: Report → Select Report
2. Click: "Export"
3. Seleccionar formato
4. Download archivo

---

## Configuración

### Configurar Cuenta

#### Business Settings

1. **Ir a:** Settings → Business
2. **Configurar:**
   - Company name
   - Industry
   - Timezone
   - Currency
   - Date format

#### Team Settings

1. **Ir a:** Settings → Team
2. **Invitar miembro:**
   - Email
   - Role (Admin, Standard, Read-only)
   - Permissions

### Configurar Integraciones

#### Conectar Stripe (Pagos)

1. **Ir a:** Settings → Integrations → Add Integration
2. **Tipo:** Payment Processing
3. **Proveedor:** Stripe
4. **Configurar:**
   - Stripe API keys (publishable + secret)
   - Webhook endpoint
   - Currencies aceptadas

#### Conectar SendGrid (Email)

1. **Ir a:** Settings → Integrations → Add Integration
2. **Tipo:** Email Marketing
3. **Proveedor:** SendGrid
4. **Configurar:**
   - API key
   - Sender email verificado
   - Webhook URL

### Configurar Dominio Custom

#### Para Funnels

1. **Ir a:** Settings → Custom Domains
2. **Agregar dominio:**
   - Tu dominio: `funnels.yoursite.com`
3. **Configurar DNS:**
   ```
   CNAME -> gohighlevel.pages.dev
   ```

#### Para Application

1. **Ir a:** Settings → Custom Domains
2. **Agregar dominio:** `app.yoursite.com`
3. **Actualizar DNS:**
   ```
   A -> 164.90.123.45 (IP address)
   ```

---

## Solución de Problemas

### Problemas Comunes

#### Workflow No Se Ejecuta

**Síntoma:** Contact creado pero workflow no se dispara.

**Soluciones:**
1. **Verificar trigger:**
   - ¿El tipo de trigger coincide con el evento?
   - ¿Los filtros son correctos?

2. **Verificar estado del workflow:**
   - Status debe ser "Active" (no "Draft")
   - Ir a: Workflows → Select Workflow → Check status

3. **Verificar execution logs:**
   - Buscar errores en logs
   - Ir a: Workflows → Select Workflow → Execution Logs

#### Email No Llega

**Síntoma:** Email enviado pero no recibido.

**Soluciones:**
1. **Check spam folder** del recipient
2. **Verificar configuración de email:**
   - Settings → Integrations → Email
   - Test connection
3. **Revisar reputación del dominio:**
   - Usar herramientas como https://mail-tester.com
4. **Verificar logs de envío:**
   - Marketing → Campaigns → Select campaign → Stats

#### Funnel No Convierte

**Síntoma:** Muchas visitas pero pocas conversiones.

**Soluciones:**
1. **Analizar analytics:**
   - ¿Drop-off rate alto en página específica?
   - ¿Tasa de rebote alta?

2. **Optimizar landing page:**
   - Mejorar copy (headline, CTA)
   - Reducir campos en formulario
   - Añadir prueba social (testimonios)

3. **A/B testing:**
   - Probar diferentes variantes
   - Ir a: Funnels → Select funnel → A/B Tests

#### No Puedo Agregar Contact

**Síntoma:** Error al crear contact.

**Soluciones:**
1. **Verificar permisos:**
   - ¿Tu role permite crear contacts?
   - Settings → Team → Your permissions

2. **Validar datos:**
   - Email requerido y debe ser único
   - Campos custom validados correctamente

3. **Verificar límites de cuenta:**
   - ¿Has alcanzado el límite de contacts?
   - Plans → Current plan → Check limits

### Obtener Ayuda

#### Help Center

- **Documentation:** Revisar este manual y la Wiki técnica
- **In-app help:** Click icono "?" en esquina superior derecha
- **Email:** support@gohighlevel.com
- **Chat:** Live chat disponible 24/7 (plan Enterprise)

#### Reportar Bugs

1. **Ir a:** Settings → Help → Report Issue
2. **Completar:**
   - Tipo de problema (Bug, Feature request, Other)
   - Descripción detallada
   - Pasos para reproducir
   - Screenshot (si applicable)

---

## Tips y Mejores Prácticas

### Workflows

✅ **Mantener workflows simples** - Menos de 10 actions cuando sea posible
✅ **Usar nombres descriptivos** - "Welcome Email Sequence" vs "Workflow 1"
✅ **Probar antes de activar** - Siempre usar "Test Workflow"
✅ **Monitorear performance** - Revisar analytics regularmente

### CRM

✅ **Mantener tags organizadas** - Usar convención de nombres (ej: status-*, source-*)
✅ **Usar custom fields estratégicamente** - No crear campos que no usarás
✅ **Revisar pipeline diariamente** - Mover deals para mantener pipeline limpio
✅ **Documentar processes** - Definir cuándo deals avanzan entre stages

### Marketing

✅ **Segmentar lists** - No enviar a toda la lista siempre
✅ **Personalizar contenido** - Usar variables como {{first_name}}
✅ **Respetar frequency caps** - No spammeando contacts
✅ **A/B test siempre** - Probar subject lines, CTAs, diseño

### Funnels

✅ **Menos es más** - Reduce campos en formulario
✅ **Above the fold** - Poner CTA visible sin scroll
✅ **Mobile-first** - Optimizar para móviles primero
✅ **Usar video** - Los videos aumentan conversión

### Calendarios

✅ **Buffer time** - Dejar espacio entre citas
✅ **Confirmations** - Enviar recordatorios de citas
✅ **Sync calendars** - Conectar con Google/Outlook personal
✅ **Limit availability** - No sobreabrir calendario

---

## Atajos de Teclado

### Navegación Global

| Comando | Acción |
|---------|---------|
| `Cmd/Ctrl + K` | Buscar global |
| `Cmd/Ctrl + /` | Abrir help center |
| `Cmd/Ctrl + N` | Nuevo (contact, deal, etc.) |
| `Esc` | Cerrar modal/sidebar |

### En Workflows

| Comando | Acción |
|---------|---------|
| `N` | Crear nuevo workflow |
| `E` | Editar workflow seleccionado |
| `Delete` | Eliminar workflow |
| `Cmd/Ctrl + S` | Guardar cambios |

### En CRM

| Comando | Acción |
|---------|---------|
| `N` | Nuevo contact/deal |
| `F` | Búsqueda avanzada |
| `Cmd/Ctrl + K` | Quick actions menu |

---

## Consejos de Seguridad

### Contraseñas

✅ Usar contraseñas únicas por aplicación
✅ Habilitar 2FA (autenticación de dos factores)
✅ Rotar contraseñas cada 90 días
❌ No reuse contraseñas
❌ No compartir credenciales

### API Keys

✅ Guardar API keys en variables de entorno
✅ Rotar keys regularmente
✅ Monitorear uso de API
❌ No commitear keys en repositorios

### Data

✅ Hacer backup regularmente
✅ Exportar datos periódicamente
✅ Usar roles y permissions apropiadamente
❌ No exportar datos sensibles sin encrypt

---

## Recursos Adicionales

### Tutoriales en Video

- [Getting Started](https://help.gohighlevel.com/getting-started) (5 min)
- [Workflow Builder](https://help.gohighlevel.com/workflows) (10 min)
- [CRM Basics](https://help.gohighlevel.com/crm) (15 min)
- [Funnel Building](https://help.gohighlevel.com/funnels) (20 min)

### Webinars

- [Weekly Demo](https://gohighlevel.com/webinars) - Jueves 2 PM EST
- [Q&A Sessions](https://gohighlevel.com/qa) - Primer martes del mes
- [Feature Deep Dives](https://gohighlevel.com/deep-dive) - Tercer miércoles

### Community

- [Facebook Group](https://facebook.com/groups/gohighlevel-users)
- [Slack Community](https://gohighlevel.slack.com)
- [Reddit r/gohighlevel](https://reddit.com/r/gohighlevel)

---

## Glosario

| Término | Definición |
|---------|------------|
| **Workflow** | Secuencia de acciones automatizadas |
| **Trigger** | Evento que inicia un workflow |
| **Action** | Paso individual dentro de un workflow |
| **Funnel** | Secuencia de páginas para conversión |
| **Pipeline** | Etapas de proceso de ventas |
| **Deal** | Oportunidad de venta en pipeline |
| **Tag** | Etiqueta para categorizar contacts |
| **Enrollment** | Contact agregado a workflow |
| **Conversion** | Contact que completó acción deseada |
| **Bounce** | Email que no pudo ser entregado |

---

## Contacto y Soporte

### Soporte Técnico

- **Email:** support@gohighlevel.com
- **Chat:** Disponible en app
- **Phone:** +1 (555) 123-4567 (9-5 PM EST)
- **Response Time:** < 2 horas durante business hours

### Ventas

- **Email:** sales@gohighlevel.com
- **Calendario:** Book demo call
- **Phone:** +1 (555) 987-6543

### Emergencias

- **System Status:** https://status.gohighlevel.com
- **Incident Updates:** @gohighlevel-status en Twitter

---

**Manual de Usuario v1.0** - © 2026 GoHighLevel Clone
**Última actualización:** 2026-02-07
