#!/usr/bin/env python3
"""
Slack Notifier for GoHighLevel Clone Development
Envía notificaciones a Slack cuando los agentes completan tareas.
"""

import os
import requests
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any

class SlackNotifier:
    """Envía notificaciones a Slack durante el desarrollo autónomo."""

    def __init__(self, webhook_url: Optional[str] = None):
        """
        Inicializa el notificador de Slack.

        Args:
            webhook_url: URL del webhook de Slack (de environment variable)
        """
        self.webhook_url = webhook_url or os.getenv("SLACK_WEBHOOK_URL")
        self.enabled = bool(self.webhook_url)

        if not self.enabled:
            print("⚠️  Slack notifications DISABLED (no webhook URL configured)")

    def send_notification(
        self,
        message: str,
        emoji: str = "🚀",
        channel: str = "#dev-notifications",
        username: str = "GoHighLevel Bot",
        attachments: Optional[list] = None
    ) -> bool:
        """
        Envía notificación a Slack.

        Args:
            message: Mensaje a enviar
            emoji: Emoji para el mensaje
            channel: Canal de Slack (opcional)
            username: Nombre del bot
            attachments: Adjuntos del mensaje (bloques, campos, etc.)

        Returns:
            True si se envió correctamente, False si falló
        """
        if not self.enabled:
            return False

        payload = {
            "text": f"{emoji} {message}",
            "username": username,
            "icon_emoji": ":rocket:",
            "attachments": attachments or []
        }

        try:
            response = requests.post(
                self.webhook_url,
                json=payload,
                timeout=10
            )
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            print(f"❌ Error enviando notificación a Slack: {e}")
            return False

    def notify_agent_complete(
        self,
        agent_id: str,
        agent_type: str,
        description: str,
        files_created: int = 0,
        lines_of_code: int = 0
    ):
        """Notifica que un agente ha completado su trabajo."""
        message = f"""
*Agente Completado*

*Tipo:* {agent_type}
*ID:* {agent_id}
*Descripción:* {description}

📊 Estadísticas:
• Archivos creados: {files_created}
• Líneas de código: {lines_of_code:,}
• Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

        return self.send_notification(
            message=message,
            emoji="✅",
            attachments=[{
                "color": "#36a64f",
                "title": f"Agente {agent_type} Completado",
                "text": description,
                "fields": [
                    {
                        "title": "Archivos",
                        "value": str(files_created),
                        "short": True
                    },
                    {
                        "title": "Líneas de Código",
                        "value": f"{lines_of_code:,}",
                        "short": True
                    }
                ],
                "footer": "GoHighLevel Clone - Modo Autónomo",
                "ts": int(datetime.now().timestamp())
            }]
        )

    def notify_phase_complete(
        self,
        phase_name: str,
        agent_count: int,
        details: str
    ):
        """Notifica que una fase del proyecto ha completado."""
        message = f"""
*Fase Completada*

*Fase:* {phase_name}
*Agentes completados:* {agent_count}

{details}
"""

        return self.send_notification(
            message=message,
            emoji="🎉",
            attachments=[{
                "color": "#28a745",
                "title": f"Fase {phase_name} Completada",
                "text": details,
                "footer": "GoHighLevel Clone - Modo Autónomo"
            }]
        )

    def notify_error(
        self,
        agent_id: str,
        error_type: str,
        error_message: str
    ):
        """Notifica que un agente ha fallado."""
        message = f"""
*Error en Agente*

*Agente ID:* {agent_id}
*Tipo de Error:* {error_type}

{error_message}
"""

        return self.send_notification(
            message=message,
            emoji="❌",
            attachments=[{
                "color": "#dc3545",
                "title": f"Error en {agent_id}",
                "text": error_message,
                "footer": "GoHighLevel Clone - Modo Autónomo",
                "ts": int(datetime.now().timestamp())
            }]
        )

    def notify_progress_update(
        self,
        total_agents: int,
        completed: int,
        current_phase: str,
        overall_progress: float
    ):
        """Notifica progreso global del proyecto."""
        progress_bar = "█" * int(overall_progress / 10) + "░" * (10 - int(overall_progress / 10))

        message = f"""
*Actualización de Progreso*

{progress_bar} {overall_progress:.1f}%

*Agentes totales:* {total_agents}
*Completados:* {completed}
*En ejecución:* {total_agents - completed}
*Fase actual:* {current_phase}
"""

        return self.send_notification(
            message=message,
            emoji="📊",
            attachments=[{
                "color": "#17a2b8",
                "title": "Progreso del Proyecto",
                "fields": [
                    {
                        "title": "Completado",
                        "value": f"{completed}/{total_agents} agentes",
                        "short": True
                    },
                    {
                        "title": "Progreso",
                        "value": f"{overall_progress:.1f}%",
                        "short": True
                    }
                ],
                "footer": "GoHighLevel Clone - Modo Autónomo"
            }]
        )


def main():
    """Función principal para probar el notificador."""
    import argparse

    parser = argparse.ArgumentParser(description="Envía notificación de prueba a Slack")
    parser.add_argument("--message", "-m", required=True, help="Mensaje a enviar")
    parser.add_argument("--emoji", "-e", default="🚀", help="Emoji para el mensaje")
    args = parser.parse_args()

    notifier = SlackNotifier()

    if notifier.enabled:
        notifier.send_notification(args.message, args.emoji)
        print("✅ Notificación enviada a Slack")
    else:
        print("⚠️  Slack no configurado. Configura SLACK_WEBHOOK_URL")


if __name__ == "__main__":
    main()
