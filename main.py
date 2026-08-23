"""
Punto de entrada principal del sistema de análisis de bienestar estudiantil.

Uso:
    python main.py --mode manual --file data/raw/encuesta.csv
    python main.py --mode manual  # Conecta con Google Forms
    python main.py --mode auto    # Monitoreo automático
    python main.py --mode scheduled --time 08:00
    python main.py --dashboard    # Ejecuta el dashboard
"""

import argparse
import sys

from src.orchestrator import AgentOrchestrator
from src.utils.logger import get_logger

logger = get_logger(__name__)


def run_analysis(args):
    """Ejecuta el análisis."""
    orchestrator = AgentOrchestrator()

    if args.file:
        logger.info(f"Modo manual - Archivo: {args.file}")
        results = orchestrator.run_full_analysis(
            data_source="file",
            file_path=args.file,
            send_notification=not args.no_email,
            generate_report=not args.no_report,
        )
    else:
        logger.info("Modo manual - Conectando con Google Forms")
        results = orchestrator.run_full_analysis(
            data_source="api",
            send_notification=not args.no_email,
            generate_report=not args.no_report,
        )

    return results


def run_dashboard():
    """Ejecuta el dashboard Streamlit."""
    import subprocess
    import os

    dashboard_path = os.path.join(
        os.path.dirname(__file__),
        "src",
        "visualization",
        "dashboard.py",
    )

    logger.info("Iniciando dashboard Streamlit...")
    subprocess.run(["streamlit", "run", dashboard_path])


def main():
    """Función principal."""
    parser = argparse.ArgumentParser(
        description="Agente de Análisis de Bienestar Psicológico Estudiantil - UST"
    )

    # Modos de ejecución
    mode_group = parser.add_mutually_exclusive_group(required=True)
    mode_group.add_argument(
        "--mode",
        choices=["manual", "auto", "scheduled"],
        help="Modo de ejecución del análisis",
    )
    mode_group.add_argument(
        "--dashboard",
        action="store_true",
        help="Ejecuta el dashboard Streamlit",
    )

    # Opciones adicionales
    parser.add_argument("--file", type=str, help="Ruta al archivo CSV de entrada")
    parser.add_argument("--time", type=str, default="08:00", help="Hora para análisis programado")
    parser.add_argument("--no-email", action="store_true", help="No enviar notificación por correo")
    parser.add_argument("--no-report", action="store_true", help="No generar reporte PDF")

    args = parser.parse_args()

    logger.info("=" * 60)
    logger.info("Sistema de Análisis de Bienestar Psicológico Estudiantil")
    logger.info("Universidad Santo Tomás")
    logger.info("=" * 60)

    try:
        if args.dashboard:
            run_dashboard()
        elif args.mode == "manual":
            results = run_analysis(args)
            logger.info(f"Análisis completado. Estado: {results.get('status')}")
            logger.info(f"Total de respuestas: {results.get('total_responses')}")
        elif args.mode == "auto":
            orchestrator = AgentOrchestrator()
            orchestrator.start_automatic_monitoring()
        elif args.mode == "scheduled":
            orchestrator = AgentOrchestrator()
            orchestrator.start_scheduled_analysis(args.time)

    except KeyboardInterrupt:
        logger.info("Operación cancelada por el usuario")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Error fatal: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
