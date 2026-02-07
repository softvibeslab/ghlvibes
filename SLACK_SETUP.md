# 🔔 Notificaciones Slack - GoHighLevel Clone

Sistema de notificaciones en tiempo real para el desarrollo autónomo.

---

## 🚀 Configuración en 3 Pasos

### Paso 1: Obtener Webhook de Slack

1. **Abre tu espacio de Slack**
2. **Navega a:** Apps → Buscar "Incoming Webhooks"
3. **Crea Webhook:**
   - Click en "Add to Slack"
   - Selecciona el canal donde recibirás notificaciones (recomiendo #dev-notifications o #general)
   - Click en "Add Incoming Webhooks Integration"
4. **Copia la Webhook URL:**
   ```
   https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXX
   ```

### Paso 2: Configurar Variable de Entorno

**Opción A: Temporal (sesión actual)**
```bash
export SLACK_WEBHOOK_URL="https://hooks.slack.com/services/TU_WEBHOOK_URL"
```

**Opción B: Permanente (recomendado)**
```bash
# Crear archivo .env
echo 'SLACK_WEBHOOK_URL="https://hooks.slack.com/services/TU_WEBHOOK_URL"' >> .env

# O edita .env y agrega la línea
nano .env
```

### Paso 3: Probar Notificación

```bash
cd /config/workspace/gohighlevel-clone

# Enviar mensaje de prueba
python slack_notifier.py --message "✅ Slack notificaciones funcionando!" --emoji "🎉"
```

Deberías recibir el mensaje en tu Slack inmediatamente.

---

## 📊 Uso del Sistema

### Verificar Estado de Agentes

```bash
# Ver dashboard de todos los agentes
python check_agents.py

# Esto muestra:
# - Estado de cada agente (Activo/Completado)
# - Tamaño de archivos generados
# - Última modificación
# - Envía resumen a Slack automáticamente
```

### Notificaciones Automáticas

El sistema enviará notificaciones a Slack cuando:

✅ **Agente Completado:**
- Tipo de agente
- ID del agente
- Archivos creados
- Líneas de código generadas

✅ **Fase Completada:**
- Nombre de la fase
- Agentes completados
- Detalles de implementación

✅ **Actualización de Progreso:**
- Agentes totales vs completados
- Porcentaje de completion
- Fase actual

✅ **Errores:**
- ID del agente que falló
- Tipo de error
- Mensaje de error

---

## 🛠️ Scripts Disponibles

### `slack_notifier.py`
Script principal para enviar notificaciones a Slack.

**Uso:**
```bash
# Mensaje simple
python slack_notifier.py --message "Hola Slack" --emoji "👋"

# Notificación de agente completado
python -c "
from slack_notifier import SlackNotifier
slack = SlackNotifier()
slack.notify_agent_complete(
    agent_id='a90c8c6',
    agent_type='expert-backend',
    description='CRM Backend Module',
    files_created=25,
    lines_of_code=15000
)
"
```

### `check_agents.py`
Verifica el estado de los 11 agentes en background.

**Uso:**
```bash
python check_agents.py

# Output:
# ┌──────────────────────────────────────┐
# │ 📊 DASHBOARD DE AGENTES              │
# ├──────────────────────────────────────┤
# │ 1. Frontend Workflows (8-15)         │
# │    Estado: ⏳ ACTIVO                   │
# │    Tamaño: 92,751 bytes                │
# │                                        │
# │ 2. CRM Backend                        │
# │    Estado: ✅ COMPLETADO                │
# │    Tamaño: 125,430 bytes               │
# └──────────────────────────────────────┘
```

### `agent_wrapper.py`
Wrapper para ejecutar agentes con notificaciones automáticas.

---

## 📱 Ejemplos de Notificaciones Recibirás

### 1. Agente Completado
```
✅ Agente Completado

Tipo: expert-backend
ID: a90c8c6
Descripción: CRM Backend Module

📊 Estadísticas:
• Archivos creados: 25
• Líneas de código: 15,000
• Timestamp: 2026-02-07 14:30:15
```

### 2. Fase Completada
```
🎉 Fase Completada

Fase: Backend CRM Development
Agentes completados: 2

Implementación completa del módulo CRM con:
- Contacts Management
- Pipelines & Deals
- Companies
- Activities & Tasks
- Notes & Communications
```

### 3. Actualización de Progreso
```
📊 Actualización de Progreso

██████████░░░░░░░░░░░░░░░░░░░ 35.0%

Agentes totales: 11
Completados: 2
En ejecución: 9
Fase actual: Desarrollo Autónomo
```

---

## 🎯 Integración con Mi Modo Autónomo

El sistema de notificaciones está integrado con mi ejecución autónoma. Cuando los agentes terminen, recibirás notificaciones automáticas.

**No necesitas hacer nada más** - solo:
1. Configurar SLACK_WEBHOOK_URL
2. Esperar notificaciones
3. Monitorear progreso con `check_agents.py`

---

## 🔧 Solución de Problemas

### No recibo notificaciones

```bash
# 1. Verificar que la variable está configurada
echo $SLACK_WEBHOOK_URL

# 2. Si está vacía, configurarla
export SLACK_WEBHOOK_URL="tu_webhook_url"

# 3. Probar de nuevo
python slack_notifier.py --message "Test"
```

### Recibo mensaje de error en Slack

Los webhooks de Slack tienen un límite de velocidad:
- Máximo 1 mensaje por segundo
- Si excedes, los mensajes se pondrán en cola

**Solución:** El script maneja esto automáticamente, solo espera.

### El formato se ve mal en Slack

Asegúrate de usar un cliente de Slack que soporte Markdown o usa la app móvil.

---

## 📚 Archivos del Sistema

- `slack_notifier.py` - Notificador principal
- `check_agents.py` - Verificador de agentes
- `agent_wrapper.py` - Wrapper con notificaciones
- `SLACK_SETUP.md` - Este archivo

---

## ✅ Estado del Sistema

**Configuración:** ❌ PENDIENTE (esperando tu webhook URL)
**Agentes Activos:** 11 agentes ejecutándose
**Proceso:** Autónomo sin interrupciones

Cuando configures el webhook, recibirás actualizaciones automáticas del progreso.

---

**¿Listo para configurar?** Solo necesitas la Webhook URL de Slack 🚀
