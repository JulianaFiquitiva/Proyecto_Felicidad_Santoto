"""
Módulo orquestador principal del agente de IA.
Integra el agente autónomo con el análisis tradicional.
"""

import os
import json
import time
from datetime import datetime
from typing import Optional

import yaml
import schedule
import pandas as pd
import numpy as np

from src.data.collector import GoogleFormsCollector, load_local_csv
from src.data.processor import DataProcessor
from src.analysis.statistics import StatisticalAnalysis
from src.analysis.correlations import CorrelationAnalysis
from src.analysis.clustering import ClusteringAnalysis
from src.analysis.factors import FactorAnalysis
from src.reports.generator import ReportGenerator
from src.notifications.email import EmailNotifier
from src.ai.interpreter import AIInterpreter
from src.ai.agent import AutonomousAgent
from src.utils.logger import get_logger

logger = get_logger(__name__)


class AgentOrchestrator:
    """Orquestador principal del agente de análisis."""

    def __init__(self, config_path: str = "configs/config.yaml"):
        """
        Inicializa el orquestador.

        Args:
            config_path: Ruta al archivo de configuración
        """
        self.config = self._load_config(config_path)
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        # Inicializar componentes tradicionales
        self.collector = GoogleFormsCollector(self.config.get("google_forms", {}))
        self.processor = DataProcessor(self.config)
        self.stats_analysis = StatisticalAnalysis(self.config)
        self.correlation_analysis = CorrelationAnalysis(self.config)
        self.clustering_analysis = ClusteringAnalysis(self.config)
        self.factor_analysis = FactorAnalysis(self.config)
        self.report_generator = ReportGenerator(self.config)
        self.email_notifier = EmailNotifier(self.config.get("email", {}))
        self.ai_interpreter = AIInterpreter(self.config)

        # Inicializar agente autónomo
        self.autonomous_agent = AutonomousAgent(self.config)

        # Estado
        self.last_check = None
        self.history = self._load_history()

    def _load_config(self, config_path: str) -> dict:
        """Carga la configuración desde YAML."""
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Error al cargar configuración: {e}")
            return {}

    def _load_history(self) -> list:
        """Carga el histórico de ejecuciones."""
        history_path = self.config.get("orchestrator", {}).get(
            "history_file", "data/processed/analysis_history.json"
        )

        if os.path.exists(history_path):
            try:
                with open(history_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return []

        return []

    def _save_history(self, entry: dict):
        """Guarda una entrada en el histórico."""
        class CustomEncoder(json.JSONEncoder):
            def default(self, obj):
                if isinstance(obj, (bool, np.bool_)):
                    return bool(obj)
                if isinstance(obj, np.integer):
                    return int(obj)
                if isinstance(obj, np.floating):
                    return float(obj)
                if isinstance(obj, np.ndarray):
                    return obj.tolist()
                return super().default(obj)

        history_path = self.config.get("orchestrator", {}).get(
            "history_file", "data/processed/analysis_history.json"
        )

        os.makedirs(os.path.dirname(history_path), exist_ok=True)

        self.history.append(entry)

        with open(history_path, "w", encoding="utf-8") as f:
            json.dump(self.history, f, indent=2, ensure_ascii=False, cls=CustomEncoder)

    def run_full_analysis(
        self,
        data_source: str = "api",
        file_path: Optional[str] = None,
        send_notification: bool = True,
        generate_report: bool = True,
        use_autonomous_agent: bool = True,
    ) -> dict:
        """
        Ejecuta el análisis completo con agente autónomo.

        Args:
            data_source: Fuente de datos ("api" o "file")
            file_path: Ruta al archivo CSV (si data_source="file")
            send_notification: Enviar notificación por correo
            generate_report: Generar reporte PDF
            use_autonomous_agent: Usar el agente autónomo (recomendado)

        Returns:
            Resultados del análisis
        """
        logger.info("=== INICIANDO ANÁLISIS COMPLETO ===")
        start_time = time.time()

        results = {
            "timestamp": datetime.now().isoformat(),
            "status": "in_progress",
            "total_responses": 0,
            "mode": "autonomous" if use_autonomous_agent else "traditional",
        }

        try:
            # 1. Recopilar datos
            logger.info("Paso 1: Recopilando datos...")
            if data_source == "file" and file_path:
                df_raw = load_local_csv(file_path)
            else:
                df_raw = self.collector.extract_responses()

            if df_raw.empty:
                logger.warning("No hay datos para analizar")
                results["status"] = "no_data"
                return results

            results["total_responses"] = len(df_raw)

            # 2. Procesar datos
            logger.info("Paso 2: Procesando datos...")
            df_processed, validation_report = self.processor.prepare_analysis_data(df_raw)

            if not validation_report.is_valid:
                logger.warning(
                    f"Advertencias de validación: {len(validation_report.warnings)}"
                )

            # Si se usa el agente autónomo, delegar el análisis
            if use_autonomous_agent:
                logger.info("Usando AGENTE AUTÓNOMO para análisis...")
                return self._run_autonomous_analysis(
                    df_processed, df_raw, results, start_time,
                    send_notification, generate_report
                )

            # Análisis tradicional (sin agente autónomo)
            return self._run_traditional_analysis(
                df_processed, results, start_time,
                send_notification, generate_report
            )

        except Exception as e:
            logger.error(f"Error durante el análisis: {e}")
            results["status"] = "error"
            results["error"] = str(e)
            return results

    def _run_autonomous_analysis(
        self,
        df_processed: pd.DataFrame,
        df_raw: pd.DataFrame,
        initial_results: dict,
        start_time: float,
        send_notification: bool,
        generate_report: bool,
    ) -> dict:
        """
        Ejecuta análisis usando el agente autónomo.

        Args:
            df_processed: Datos procesados
            df_raw: Datos originales
            initial_results: Resultados iniciales
            start_time: Tiempo de inicio
            send_notification: Enviar notificación
            generate_report: Generar reporte

        Returns:
            Resultados del análisis autónomo
        """
        # Preparar datos para el agente
        data_for_agent = {
            "df_processed": df_processed,
            "df_raw": df_raw,
            "total_rows": len(df_processed),
            "columns": list(df_processed.columns),
        }

        # Ejecutar ciclo autónomo
        agent_results = self.autonomous_agent.run_autonomous_cycle(data_for_agent)

        # Combinar resultados
        results = initial_results.copy()
        results.update(agent_results.get("phases", {}).get("analysis", {}))

        # Agregar resultados del agente
        results["autonomous_agent"] = {
            "status": agent_results.get("status"),
            "summary": agent_results.get("summary"),
            "decisions": agent_results.get("phases", {}).get("decisions", {}),
            "recommendations": agent_results.get("phases", {}).get("recommendations", {}),
            "learning": agent_results.get("phases", {}).get("learning", {}),
            "ai_report": agent_results.get("phases", {}).get("ai_report", {}),
        }

        # Generar reporte PDF si se solicita
        pdf_path = None
        if generate_report:
            logger.info("Generando reporte PDF...")
            pdf_path = self._generate_report(results, results.get("clusters", []))

        # Enviar notificación si se solicita
        if send_notification:
            logger.info("Enviando notificación...")
            self._send_notification(results, pdf_path)

        # Guardar en histórico
        results["status"] = "completed"
        results["duration_seconds"] = round(time.time() - start_time, 2)
        self._save_history(results)

        logger.info(
            f"=== ANÁLISIS AUTÓNOMO COMPLETADO en {results['duration_seconds']}s ==="
        )

        return results

    def _run_traditional_analysis(
        self,
        df_processed: pd.DataFrame,
        initial_results: dict,
        start_time: float,
        send_notification: bool,
        generate_report: bool,
    ) -> dict:
        """
        Ejecuta análisis tradicional (sin agente autónomo).

        Args:
            df_processed: Datos procesados
            initial_results: Resultados iniciales
            start_time: Tiempo de inicio
            send_notification: Enviar notificación
            generate_report: Generar reporte

        Returns:
            Resultados del análisis tradicional
        """
        results = initial_results.copy()

        # Estadísticas descriptivas
        dimension_stats = self.stats_analysis.descriptive_statistics(df_processed)
        results["dimension_stats"] = [
            {
                "dimension": s.dimension,
                "mean": s.mean,
                "std": s.std,
                "min": s.min,
                "max": s.max,
                "n": s.n,
            }
            for s in dimension_stats
        ]

        # Estadísticas globales
        if "wellbeing_global" in df_processed.columns:
            results["global_mean"] = float(df_processed["wellbeing_global"].mean())
            results["global_std"] = float(df_processed["wellbeing_global"].std())

        # Correlaciones
        global_corr = self.correlation_analysis.correlate_with_global(df_processed)
        results["correlations"] = [
            {
                "var1": c.var1,
                "var2": c.var2,
                "correlation": c.correlation,
                "p_value": c.p_value,
                "significant": c.significant,
            }
            for c in global_corr
        ]

        # Regresión
        regression_results = self.factor_analysis.regression_analysis(df_processed)
        results["regression"] = {
            "r_squared": regression_results.get("r_squared", 0),
            "factors": [
                {
                    "factor": f.factor,
                    "std_coefficient": f.std_coefficient,
                    "p_value": f.p_value,
                    "significant": f.significant,
                }
                for f in regression_results.get("factors", [])
            ],
        }

        # Clustering
        df_clustered = self.clustering_analysis.fit_clusters(df_processed)
        cluster_profiles = self.clustering_analysis.get_cluster_profiles(df_clustered)
        results["clusters"] = [
            {
                "id": p.cluster_id,
                "size": p.size,
                "percentage": p.percentage,
                "label": p.label,
            }
            for p in cluster_profiles
        ]

        # Guardar datos procesados
        output_path = os.path.join(
            self.base_dir,
            self.config.get("paths", {}).get("data_processed", "data/processed"),
            f"resultados_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        )
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        df_clustered.to_csv(output_path, index=False, encoding="utf-8-sig")

        # Generar reporte PDF
        pdf_path = None
        if generate_report:
            pdf_path = self._generate_report(results, cluster_profiles)

        # Interpretación IA
        ai_interpretation = self.ai_interpreter.interpret_results(results)
        ai_summary = self.ai_interpreter.generate_executive_summary(results)
        ai_recommendations = self.ai_interpreter.generate_recommendations(results)

        results["ai_interpretation"] = ai_interpretation
        results["ai_summary"] = ai_summary
        results["ai_recommendations"] = ai_recommendations

        # Enviar notificación
        if send_notification:
            self._send_notification(results, pdf_path)

        # Guardar en histórico
        results["status"] = "completed"
        results["duration_seconds"] = round(time.time() - start_time, 2)
        self._save_history(results)

        logger.info(
            f"=== ANÁLISIS TRADICIONAL COMPLETADO en {results['duration_seconds']}s ==="
        )

        return results

    def _generate_report(self, results: dict, cluster_profiles: list) -> str:
        """Genera reporte PDF."""
        pdf_path = os.path.join(
            self.base_dir,
            self.config.get("paths", {}).get("reports", "reports"),
            f"reporte_ejecutivo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
        )

        # Convertir cluster_profiles a objetos ClusterProfile si son diccionarios
        from src.analysis.clustering import ClusterProfile
        processed_profiles = []
        for p in cluster_profiles:
            if isinstance(p, dict):
                profile = ClusterProfile(
                    cluster_id=p.get("id", p.get("cluster_id", 0)),
                    size=p.get("size", 0),
                    percentage=p.get("percentage", 0),
                    label=p.get("label", ""),
                    centroid=p.get("centroid", {}),
                )
                processed_profiles.append(profile)
            else:
                processed_profiles.append(p)

        self.report_generator.generate_executive_report(
            output_path=pdf_path,
            summary_stats=results,
            dimension_stats=results.get("dimension_stats", []),
            correlations=results.get("correlations", []),
            regression_results=results.get("regression", {}),
            cluster_profiles=processed_profiles,
            total_responses=results.get("total_responses", 0),
        )

        return pdf_path

    def _send_notification(self, results: dict, pdf_path: Optional[str] = None):
        """Envía notificación por correo."""
        notification_stats = {
            "total_responses": results.get("total_responses", 0),
            "global_mean": results.get("global_mean", 0),
            "global_std": results.get("global_std", 0),
            "dimensions": results.get("dimension_stats", []),
            "analysis_date": datetime.now().strftime("%d/%m/%Y %H:%M"),
            "ai_summary": results.get("ai_summary", ""),
        }

        # Agregar resumen del agente autónomo si está disponible
        if "autonomous_agent" in results:
            agent_summary = results["autonomous_agent"].get("summary", {})
            notification_stats["agent_summary"] = agent_summary

        self.email_notifier.send_analysis_notification(
            stats=notification_stats,
            pdf_path=pdf_path,
        )

    def get_agent_status(self) -> dict:
        """Obtiene el estado del agente autónomo."""
        return self.autonomous_agent.get_agent_status()

    def get_agent_insights(self) -> list[str]:
        """Obtiene insights del agente autónomo."""
        return self.autonomous_agent.memory.get_insights()

    def get_agent_patterns(self) -> list[dict]:
        """Obtiene patrones detectados por el agente."""
        return self.autonomous_agent.memory.detect_patterns()

    def check_for_new_responses(self) -> bool:
        """
        Verifica si hay nuevas respuestas.

        Returns:
            True si hay nuevas respuestas
        """
        return self.collector.has_new_responses(self.last_check)

    def start_automatic_monitoring(self):
        """Inicia el monitoreo automático con agente autónomo."""
        interval = self.config.get("orchestrator", {}).get("check_interval_minutes", 30)

        logger.info(f"Iniciando monitoreo autónomo (cada {interval} minutos)")

        # Obtener timestamp de última respuesta actual para evitar análisis innecesario
        last_response_timestamp = self.collector.get_last_response_timestamp()
        if last_response_timestamp:
            self.last_check = last_response_timestamp
            logger.info(f"Última respuesta conocida: {last_response_timestamp}")

        def check_and_analyze():
            try:
                if self.check_for_new_responses():
                    logger.info("Nuevas respuestas detectadas, ejecutando análisis autónomo...")
                    self.run_full_analysis(
                        send_notification=True,
                        use_autonomous_agent=True,
                    )
                    # Actualizar timestamp de última respuesta
                    self.last_check = self.collector.get_last_response_timestamp()
                    logger.info(f"Análisis completado. Próxima verificación en {interval} minutos.")
                else:
                    logger.info(f"No hay nuevas respuestas. Próxima verificación en {interval} minutos.")
            except Exception as e:
                logger.error(f"Error en verificación: {e}")

        # Programar verificación periódica
        schedule.every(interval).minutes.do(check_and_analyze)

        # Ejecutar inmediatamente
        logger.info("Ejecutando primera verificación...")
        check_and_analyze()

        # Mantener ejecutándose
        logger.info("Monitoreo autónomo en ejecución. Presiona Ctrl+C para detener.")
        while True:
            schedule.run_pending()
            time.sleep(60)

    def start_scheduled_analysis(self, time_str: str = "08:00"):
        """
        Programa análisis diario autónomo.

        Args:
            time_str: Hora de ejecución (formato HH:MM)
        """
        logger.info(f"Programando análisis autónomo diario a las {time_str}")

        schedule.every().day.at(time_str).do(
            self.run_full_analysis,
            send_notification=True,
            use_autonomous_agent=True,
        )

        logger.info("Programación autónoma activa. Presiona Ctrl+C para detener.")
        while True:
            schedule.run_pending()
            time.sleep(60)


def main():
    """Función principal para ejecución directa."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Agente Autónomo de Análisis de Bienestar Estudiantil"
    )
    parser.add_argument(
        "--mode",
        choices=["manual", "auto", "scheduled", "status", "insights", "patterns"],
        default="manual",
        help="Modo de ejecución",
    )
    parser.add_argument("--file", type=str, help="Ruta al archivo CSV (modo manual)")
    parser.add_argument("--time", type=str, default="08:00", help="Hora de análisis programado")
    parser.add_argument(
        "--no-agent",
        action="store_true",
        help="Deshabilitar agente autónomo (usar análisis tradicional)",
    )

    args = parser.parse_args()

    orchestrator = AgentOrchestrator()

    if args.mode == "manual":
        orchestrator.run_full_analysis(
            data_source="file" if args.file else "api",
            file_path=args.file,
            use_autonomous_agent=not args.no_agent,
        )
    elif args.mode == "auto":
        orchestrator.start_automatic_monitoring()
    elif args.mode == "scheduled":
        orchestrator.start_scheduled_analysis(args.time)
    elif args.mode == "status":
        status = orchestrator.get_agent_status()
        print(json.dumps(status, indent=2, ensure_ascii=False))
    elif args.mode == "insights":
        insights = orchestrator.get_agent_insights()
        print("\n=== INSIGHTS DEL AGENTE ===")
        for i, insight in enumerate(insights, 1):
            print(f"{i}. {insight}")
    elif args.mode == "patterns":
        patterns = orchestrator.get_agent_patterns()
        print("\n=== PATRONES DETECTADOS ===")
        for p in patterns:
            print(f"- {p.get('message', 'Patrón detectado')}")


if __name__ == "__main__":
    main()
