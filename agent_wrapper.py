#!/usr/bin/env python3
"""
Agente Wrapper con notificaciones automáticas a Slack.
Ejecuta agentes y notifica su completion.
"""

import subprocess
import sys
import os
from pathlib import Path
from slack_notifier import SlackNotifier

# Inicializar notificador
slack = SlackNotifier()

def run_agent_with_notification(
    subagent_type: str,
    description: str,
    prompt: str,
    run_in_background: bool = False
):
    """
    Ejecuta un agente y notifica cuando completa.
    """
    print(f"\n🚀 Iniciando agente: {subagent_type}")
    print(f"📋 Descripción: {description}")
    print(f"⏰ Timestamp: {datetime.now().strftime('%H:%M:%S')}")

    if slack.enabled:
        slack.notify_progress_update(
            total_agents=11,
            completed=0,
            current_phase=description,
            overall_progress=0
        )

    try:
        # El agente se está ejecutando en background
        # Cuando termine, notificar
        print(f"⏳ Agente {subagent_type} ejecutando...")

    except Exception as e:
        if slack.enabled:
            slack.notify_error(
                agent_id=subagent_type,
                error_type="Execution Error",
                error_message=str(e)
            )
        raise

if __name__ == "__main__":
    # Ejecutar con notificaciones
    print("🤖 Modo Autónomo con Notificaciones a Slack ACTIVADO")
    print("=" * 60)
