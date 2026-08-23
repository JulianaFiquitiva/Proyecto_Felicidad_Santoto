"""
Módulo de notificaciones por correo electrónico.
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from typing import Optional
import os

from src.utils.logger import get_logger

logger = get_logger(__name__)


class EmailNotifier:
    """Sistema de notificaciones por correo electrónico."""

    def __init__(self, config: dict):
        """
        Inicializa el notificador.

        Args:
            config: Configuración del proyecto (sección email)
        """
        self.config = config
        self.smtp_server = config.get("smtp_server", "smtp.gmail.com")
        self.smtp_port = config.get("smtp_port", 587)
        self.sender_email = config.get("sender_email", "")
        self.sender_password = config.get("sender_password", "")
        self.recipients = config.get("recipients", [])
        self.subject_prefix = config.get("subject_prefix", "[Felicidad Estudiantil]")
        self.enabled = config.get("enabled", False)

    def send_email(
        self,
        subject: str,
        body: str,
        recipients: Optional[list] = None,
        attachment_path: Optional[str] = None,
    ) -> bool:
        """
        Envía un correo electrónico.

        Args:
            subject: Asunto del correo
            body: Cuerpo del mensaje
            recipients: Lista de destinatarios (None = usar configuración)
            attachment_path: Ruta al archivo adjunto

        Returns:
            True si se envió correctamente
        """
        if not self.enabled:
            logger.info("Notificaciones por correo deshabilitadas")
            return False

        if not self.sender_email or not self.sender_password:
            logger.error("Credenciales de correo no configuradas")
            return False

        recipients = recipients or self.recipients

        if not recipients:
            logger.error("No hay destinatarios configurados")
            return False

        try:
            # Crear mensaje
            msg = MIMEMultipart()
            msg["From"] = self.sender_email
            msg["To"] = ", ".join(recipients)
            msg["Subject"] = f"{self.subject_prefix} {subject}"

            # Cuerpo del mensaje
            msg.attach(MIMEText(body, "plain", "utf-8"))

            # Adjunto si existe
            if attachment_path and os.path.exists(attachment_path):
                with open(attachment_path, "rb") as f:
                    attachment = MIMEApplication(f.read(), _subtype="pdf")
                    attachment.add_header(
                        "Content-Disposition",
                        "attachment",
                        filename=os.path.basename(attachment_path),
                    )
                    msg.attach(attachment)

            # Conectar y enviar
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(msg)

            logger.info(f"Correo enviado a: {', '.join(recipients)}")
            return True

        except smtplib.SMTPAuthenticationError:
            logger.error("Error de autenticación SMTP. Verificar credenciales.")
            return False
        except Exception as e:
            logger.error(f"Error al enviar correo: {e}")
            return False

    def send_analysis_notification(
        self,
        stats: dict,
        pdf_path: Optional[str] = None,
        new_responses: int = 0,
    ) -> bool:
        """
        Envía notificación con resultados del análisis.

        Args:
            stats: Estadísticas del análisis
            pdf_path: Ruta al PDF del reporte
            new_responses: Número de nuevas respuestas

        Returns:
            True si se envió correctamente
        """
        subject = f"Análisis de Bienestar - {stats.get('total_responses', 0)} respuestas"

        body = self._build_notification_body(stats, new_responses)

        return self.send_email(
            subject=subject,
            body=body,
            attachment_path=pdf_path,
        )

    def send_new_response_notification(
        self,
        total_responses: int,
        new_responses: int,
    ) -> bool:
        """
        Envía notificación de nuevas respuestas.

        Args:
            total_responses: Total de respuestas
            new_responses: Nuevas respuestas detectadas

        Returns:
            True si se envió correctamente
        """
        subject = f"Nuevas respuestas detectadas ({new_responses})"

        body = f"""
Se detectaron {new_responses} nuevas respuestas en la encuesta de bienestar.

Total acumulado de respuestas: {total_responses}

El análisis ha sido actualizado automáticamente.
        """

        return self.send_email(subject=subject, body=body)

    def _build_notification_body(self, stats: dict, new_responses: int) -> str:
        """
        Construye el cuerpo del correo de notificación.

        Args:
            stats: Estadísticas del análisis
            new_responses: Nuevas respuestas

        Returns:
            Texto del correo
        """
        global_mean = stats.get("global_mean", 0)
        global_std = stats.get("global_std", 0)

        # Determinar nivel de bienestar
        if global_mean >= 5:
            nivel = "ALTO"
        elif global_mean >= 3.5:
            nivel = "MEDIO"
        else:
            nivel = "BAJO"

        body = f"""
RESUMEN DEL ANÁLISIS DE BIENESTAR PSICOLÓGICO ESTUDIANTIL
==========================================================
Universidad Santo Tomás

Fecha de análisis: {stats.get('analysis_date', 'N/A')}

RESUMEN EJECUTIVO
-----------------
Total de participantes: {stats.get('total_responses', 0)}
"""
        if new_responses > 0:
            body += f"Nuevas respuestas: {new_responses}\n"

        body += f"""
ÍNDICE GLOBAL DE BIENESTAR
--------------------------
Promedio: {global_mean:.2f} / 6.00
Desviación Estándar: {global_std:.2f}
Nivel: {nivel}

RESULTADOS POR DIMENSIÓN
-------------------------
"""

        for dim in stats.get("dimensions", []):
            body += f"• {dim['name']}: {dim['mean']:.2f}\n"

        body += """
RECOMENDACIONES
---------------
"""
        # Generar recomendaciones básicas
        for dim in stats.get("dimensions", []):
            if dim["mean"] < 3.5:
                body += f"• Fortalecer la dimensión '{dim['name']}' (puntaje: {dim['mean']:.2f})\n"

        body += """
El reporte completo se encuentra adjunto a este correo.

---
Este es un mensaje automático generado por el Sistema de Análisis de Bienestar Estudiantil.
        """

        return body

    def test_connection(self) -> bool:
        """
        Prueba la conexión SMTP.

        Returns:
            True si la conexión es exitosa
        """
        if not self.enabled:
            logger.info("Notificaciones deshabilitadas")
            return False

        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
            logger.info("Conexión SMTP exitosa")
            return True
        except Exception as e:
            logger.error(f"Error de conexión SMTP: {e}")
            return False
