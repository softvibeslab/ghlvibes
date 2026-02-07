#!/usr/bin/env python3
"""
Verificador de estado de agentes en background.
Muestra el progreso de todos los agentes activos.
"""

import os
import subprocess
from pathlib import Path
from datetime import datetime

# Lista de agentes en background
BACKGROUND_AGENTS = [
    {"id": "ab7cd97", "name": "Frontend Workflows (8-15)", "file": "ab7cd97.output"},
    {"id": "a90c8c6", "name": "CRM Backend", "file": "a90c8c6.output"},
    {"id": "ab5ec33", "name": "CRM Frontend", "file": "ab5ec33.output"},
    {"id": "a9a8a9f", "name": "Infraestructura", "file": "a9a8a9f.output"},
    {"id": "aea9e68", "name": "Marketing Backend", "file": "aea9e68.output"},
    {"id": "a6c6cd8", "name": "Funnels Backend", "file": "a6c6cd8.output"},
    {"id": "a6a940d", "name": "Frontends Restantes", "file": "a6a940d.output"},
    {"id": "a0a1f5d", "name": "Testing Suite", "file": "a0a1f5d.output"},
    {"id": "a9b6fa1", "name": "Memberships Backend", "file": "a9b6fa1.output"},
    {"id": "aafe874", "name": "Calendars Backend", "file": "aafe874.output"},
    {"id": "a6bdb16", "name": "Documentación Final", "file": "a6bdb16.output"},
]

def check_agent_status(agent_info: dict) -> dict:
    """Verifica el estado de un agente."""
    output_file = Path(f"/tmp/claude-911/-config-workspace-gohighlevel-clone/tasks/{agent_info['file']}")

    if not output_file.exists():
        return {
            "status": "❌ ARCHIVO NO ENCONTRADO",
            "size": 0
        }

    size = output_file.stat().st_size
    modified = datetime.fromtimestamp(output_file.stat().st_mtime)

    # Leer últimas líneas para ver si está activo
    try:
        with open(output_file, 'r') as f:
            lines = f.readlines()
            recent_lines = lines[-5:] if len(lines) >= 5 else lines
            has_activity = any("tool use" in line for line in recent_lines)
            return {
                "status": "⏳ ACTIVO" if has_activity and size > 0 else "✅ COMPLETADO",
                "size": size,
                "modified": modified,
                "lines": len(lines)
            }
    except:
        return {
            "status": "⚠️  ERROR LEYENDO",
            "size": size,
            "modified": modified
        }

def print_dashboard():
    """Muestra dashboard de agentes."""
    print("\n" + "="*80)
    print("📊 DASHBOARD DE AGENTES - GoHighLevel Clone")
    print("="*80)
    print(f"🕒 Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"👥 Total Agentes: {len(BACKGROUND_AGENTS)}")
    print("-"*80)

    active_count = 0
    completed_count = 0
    total_size = 0

    for i, agent in enumerate(BACKGROUND_AGENTS, 1):
        status_info = check_agent_status(agent)
        status = status_info["status"]
        size = status_info["size"]
        modified = status_info.get("modified", "N/A")

        if "ACTIVO" in status:
            active_count += 1
        elif "COMPLETADO" in status:
            completed_count += 1

        total_size += size

        print(f"\n{i}. {agent['name']}")
        print(f"   ID: {agent['id']}")
        print(f"   Estado: {status}")
        print(f"   Tamaño: {size:,} bytes")
        print(f"   Modificado: {modified}")

    print("\n" + "-"*80)
    print(f"⏳ Activos: {active_count}")
    print(f"✅ Completados: {completed_count}")
    print(f"📁 Tamaño Total: {total_size:,} bytes ({total_size/1024/1024:.2f} MB)")
    print("="*80)

    # Enviar resumen a Slack si está configurado
    try:
        from slack_notifier import SlackNotifier
        slack = SlackNotifier()
        if slack.enabled:
            slack.notify_progress_update(
                total_agents=len(BACKGROUND_AGENTS),
                completed=completed_count,
                current_phase="Desarrollo Autónomo",
                overall_progress=(completed_count / len(BACKGROUND_AGENTS)) * 100
            )
    except:
        pass  # Slack no configurado, ignorar

if __name__ == "__main__":
    print_dashboard()
