"""
Punto de entrada principal del sistema de análisis de bienestar estudiantil.

Uso:
    python main.py --mode manual --file data/raw/encuesta.csv
    python main.py --mode manual  # Conecta con Google Forms
    python main.py --mode auto    # Monitoreo automático
    python main.py --mode scheduled --time 08:00
    python main.py --mode status  # Estado del agente autónomo
    python main.py --mode insights # Insights del agente
    python main.py --mode patterns # Patrones detectados
    python main.py --mode chat    # Chatbot interactivo
    python main.py --dashboard    # Ejecuta el dashboard
"""

import argparse
import json
import sys
import os

import yaml

from src.orchestrator import AgentOrchestrator
from src.utils.logger import get_logger

logger = get_logger(__name__)


def run_analysis(args):
    """Ejecuta el análisis con agente autónomo."""
    orchestrator = AgentOrchestrator()

    use_agent = not args.no_agent

    if args.file:
        logger.info(f"Modo manual - Archivo: {args.file}")
        logger.info(f"Agente autónomo: {'ACTIVADO' if use_agent else 'DESACTIVADO'}")
        results = orchestrator.run_full_analysis(
            data_source="file",
            file_path=args.file,
            send_notification=not args.no_email,
            generate_report=not args.no_report,
            use_autonomous_agent=use_agent,
        )
    else:
        logger.info("Modo manual - Conectando con Google Forms")
        logger.info(f"Agente autónomo: {'ACTIVADO' if use_agent else 'DESACTIVADO'}")
        results = orchestrator.run_full_analysis(
            data_source="api",
            send_notification=not args.no_email,
            generate_report=not args.no_report,
            use_autonomous_agent=use_agent,
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


def show_status():
    """Muestra el estado del agente autónomo."""
    orchestrator = AgentOrchestrator()
    status = orchestrator.get_agent_status()

    print("\n" + "=" * 60)
    print("ESTADO DEL AGENTE AUTÓNOMO")
    print("=" * 60)
    print(f"Estado: {status.get('status', 'desconocido')}")
    print(f"Último análisis: {status.get('last_analysis', 'nunca')}")
    print(f"Total de análisis: {status.get('total_analyses', 0)}")
    print(f"Entradas en memoria: {status.get('memory_size', 0)}")
    print(f"Decisiones tomadas: {status.get('decisions_count', 0)}")
    print("=" * 60)


def show_insights():
    """Muestra los insights del agente."""
    orchestrator = AgentOrchestrator()
    insights = orchestrator.get_agent_insights()

    print("\n" + "=" * 60)
    print("INSIGHTS DEL AGENTE AUTÓNOMO")
    print("=" * 60)

    if not insights:
        print("No hay insights disponibles (primero ejecuta un análisis)")
    else:
        for i, insight in enumerate(insights, 1):
            print(f"{i}. {insight}")

    print("=" * 60)


def show_patterns():
    """Muestra los patrones detectados."""
    orchestrator = AgentOrchestrator()
    patterns = orchestrator.get_agent_patterns()

    print("\n" + "=" * 60)
    print("PATRONES DETECTADOS POR EL AGENTE")
    print("=" * 60)

    if not patterns:
        print("No hay patrones detectados (se necesitan al menos 3 análisis)")
    else:
        for p in patterns:
            print(f"- {p.get('message', 'Patrón detectado')}")

    print("=" * 60)


def run_chatbot():
    """Ejecuta el chatbot interactivo."""
    from src.ai.chatbot import WellbeingChatbot

    print("\n" + "=" * 60)
    print("BIENVENIDO A BIENESTARBOT")
    print("Tu asistente de análisis de bienestar psicológico")
    print("=" * 60)
    print("Escribe 'salir' para terminar la conversación")
    print("=" * 60 + "\n")

    # Inicializar chatbot
    config = yaml.safe_load(open("configs/config.yaml", encoding="utf-8"))
    chatbot = WellbeingChatbot(config)

    # Intentar cargar último análisis
    try:
        orchestrator = AgentOrchestrator()
        history = orchestrator.history
        if history:
            last_analysis = history[-1]
            chatbot.load_analysis_results(last_analysis)
            print("[OK] Último análisis cargado en el chatbot\n")
    except Exception as e:
        print(f"[!] No se pudo cargar el análisis: {e}\n")

    # Mostrar preguntas sugeridas
    suggestions = chatbot.get_suggested_questions()
    print("PREGUNTAS SUGERIDAS:")
    for i, q in enumerate(suggestions[:5], 1):
        print(f"  {i}. {q}")
    print()

    # Bucle de conversación
    while True:
        try:
            user_input = input("Tú: ").strip()

            if not user_input:
                continue

            if user_input.lower() in ["salir", "exit", "quit", "adiós"]:
                print("\n¡Hasta luego! Que tengas un excelente día.")
                break

            if user_input.lower() == "ayuda":
                print("\nComandos disponibles:")
                print("  - Escribe cualquier pregunta sobre bienestar")
                print("  - 'sugerir' - Ver preguntas sugeridas")
                print("  - 'limpiar' - Limpiar historial")
                print("  - 'salir' - Terminar conversación\n")
                continue

            if user_input.lower() == "sugerir":
                suggestions = chatbot.get_suggested_questions()
                print("\nPREGUNTAS SUGERIDAS:")
                for i, q in enumerate(suggestions, 1):
                    print(f"  {i}. {q}")
                print()
                continue

            if user_input.lower() == "limpiar":
                chatbot.clear_history()
                print("[OK] Historial limpiado\n")
                continue

            # Obtener respuesta
            response = chatbot.chat(user_input)
            print(f"\nBienestarBot: {response}\n")

        except KeyboardInterrupt:
            print("\n\n¡Hasta luego!")
            break
        except Exception as e:
            print(f"\nError: {e}\n")


def main():
    """Función principal."""
    parser = argparse.ArgumentParser(
        description="Agente Autónomo de Análisis de Bienestar Psicológico Estudiantil - UST"
    )

    # Modos de ejecución
    mode_group = parser.add_mutually_exclusive_group(required=True)
    mode_group.add_argument(
        "--mode",
        choices=["manual", "auto", "scheduled", "status", "insights", "patterns", "chat"],
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
    parser.add_argument(
        "--no-agent",
        action="store_true",
        help="Deshabilitar agente autónomo (usar análisis tradicional)",
    )

    args = parser.parse_args()

    logger.info("=" * 60)
    logger.info("Agente Autónomo de Análisis de Bienestar Psicológico Estudiantil")
    logger.info("Universidad Santo Tomás")
    logger.info("=" * 60)

    try:
        if args.dashboard:
            run_dashboard()
        elif args.mode == "manual":
            results = run_analysis(args)
            if results:
                logger.info(f"Análisis completado. Estado: {results.get('status')}")
                logger.info(f"Total de respuestas: {results.get('total_responses')}")

                # Mostrar resumen del agente autónomo si está disponible
                if "autonomous_agent" in results:
                    agent_summary = results["autonomous_agent"].get("summary", {})
                    if agent_summary:
                        logger.info("--- Resumen del Agente Autónomo ---")
                        logger.info(f"Decisiones tomadas: {agent_summary.get('decisions_made', 0)}")
                        logger.info(f"Acciones ejecutadas: {agent_summary.get('actions_executed', 0)}")
                        logger.info(f"Reporte IA generado: {agent_summary.get('ai_generated', False)}")

        elif args.mode == "auto":
            orchestrator = AgentOrchestrator()
            orchestrator.start_automatic_monitoring()
        elif args.mode == "scheduled":
            orchestrator = AgentOrchestrator()
            orchestrator.start_scheduled_analysis(args.time)
        elif args.mode == "status":
            show_status()
        elif args.mode == "insights":
            show_insights()
        elif args.mode == "patterns":
            show_patterns()
        elif args.mode == "chat":
            run_chatbot()

    except KeyboardInterrupt:
        logger.info("Operación cancelada por el usuario")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Error fatal: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
