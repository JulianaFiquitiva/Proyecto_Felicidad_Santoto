"""
Script de ejecución nocturna para Railway
Ejecuta el análisis completo y envía reporte por correo
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.orchestrator import AgentOrchestrator

def main():
    print("=" * 50)
    print("  ANÁLISIS NOCTURNO DE BIENESTAR")
    print("  Universidad Santo Tomás")
    print("=" * 50)
    print()

    orchestrator = AgentOrchestrator()

    print("Ejecutando análisis completo...")
    results = orchestrator.run_full_analysis(
        data_source="api",
        send_notification=True,
        generate_report=True,
        use_autonomous_agent=True,
    )

    print()
    print("=" * 50)
    print(f"Estado: {results.get('status', 'desconocido')}")
    print(f"Respuestas: {results.get('total_responses', 0)}")
    print(f"Duración: {results.get('duration_seconds', 0)} segundos")
    print("=" * 50)

if __name__ == "__main__":
    main()
