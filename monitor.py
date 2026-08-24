"""
Monitoreo automático del sistema de análisis de bienestar.
Ejecuta verificaciones periódicas + reporte diario.
"""

import sys
import os
import time
import schedule
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.orchestrator import AgentOrchestrator
from src.utils.logger import get_logger

logger = get_logger(__name__)

# Cargar configuración
orchestrator = AgentOrchestrator()
last_analysis_time = None


def check_new_responses():
    """Verifica si hay nuevas respuestas y ejecuta análisis."""
    global last_analysis_time

    logger.info("Verificando nuevas respuestas...")

    try:
        # Verificar si hay nuevas respuestas
        from src.data.collector import GoogleFormsCollector

        collector = GoogleFormsCollector(orchestrator.config.get("google_forms", {}))

        if collector.has_new_responses(last_analysis_time):
            logger.info("Nuevas respuestas detectadas, ejecutando análisis...")
            results = orchestrator.run_full_analysis(
                data_source="api",
                send_notification=True,
                generate_report=True,
            )
            last_analysis_time = datetime.now()
            logger.info(f"Análisis completado: {results.get('total_responses')} respuestas")
        else:
            logger.info("No hay nuevas respuestas")
    except Exception as e:
        logger.error(f"Error al verificar respuestas: {e}")


def daily_report():
    """Ejecuta el reporte diario completo."""
    logger.info("Ejecutando reporte diario...")

    try:
        results = orchestrator.run_full_analysis(
            data_source="api",
            send_notification=True,
            generate_report=True,
        )
        logger.info(f"Reporte diario completado: {results.get('total_responses')} respuestas")
    except Exception as e:
        logger.error(f"Error en reporte diario: {e}")


def main():
    """Función principal del monitoreo."""
    logger.info("=" * 60)
    logger.info("MONITOREO AUTOMÁTICO - BIENESTAR ESTUDIANTIL UST")
    logger.info("=" * 60)
    logger.info("Modo: Verificación cada 30 min + Reporte diario a las 8:00 AM")
    logger.info("Presiona Ctrl+C para detener")
    logger.info("=" * 60)

    # Programar verificación cada 30 minutos
    schedule.every(30).minutes.do(check_new_responses)

    # Programar reporte diario a las 8:00 AM
    schedule.every().day.at("08:00").do(daily_report)

    # Ejecutar verificación inmediata
    check_new_responses()

    # Mantener ejecutándose
    while True:
        schedule.run_pending()
        time.sleep(60)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Monitoreo detenido por el usuario")
        sys.exit(0)
