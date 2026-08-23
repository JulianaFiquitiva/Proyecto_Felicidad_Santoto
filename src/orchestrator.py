"""
Módulo orquestador principal del agente de IA.
"""

import os
import json
import time
from datetime import datetime
from typing import Optional

import yaml
import schedule
import pandas as pd

from src.data.collector import GoogleFormsCollector, load_local_csv
from src.data.processor import DataProcessor
from src.analysis.statistics import StatisticalAnalysis
from src.analysis.correlations import CorrelationAnalysis
from src.analysis.clustering import ClusteringAnalysis
from src.analysis.factors import FactorAnalysis
from src.reports.generator import ReportGenerator
from src.notifications.email import EmailNotifier
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

        # Inicializar componentes
        self.collector = GoogleFormsCollector(self.config.get("google_forms", {}))
        self.processor = DataProcessor(self.config)
        self.stats_analysis = StatisticalAnalysis(self.config)
        self.correlation_analysis = CorrelationAnalysis(self.config)
        self.clustering_analysis = ClusteringAnalysis(self.config)
        self.factor_analysis = FactorAnalysis(self.config)
        self.report_generator = ReportGenerator(self.config)
        self.email_notifier = EmailNotifier(self.config.get("email", {}))

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
        history_path = self.config.get("orchestrator", {}).get(
            "history_file", "data/processed/analysis_history.json"
        )

        os.makedirs(os.path.dirname(history_path), exist_ok=True)

        self.history.append(entry)

        with open(history_path, "w", encoding="utf-8") as f:
            json.dump(self.history, f, indent=2, ensure_ascii=False)

    def run_full_analysis(
        self,
        data_source: str = "api",
        file_path: Optional[str] = None,
        send_notification: bool = True,
        generate_report: bool = True,
    ) -> dict:
        """
        Ejecuta el análisis completo.

        Args:
            data_source: Fuente de datos ("api" o "file")
            file_path: Ruta al archivo CSV (si data_source="file")
            send_notification: Enviar notificación por correo
            generate_report: Generar reporte PDF

        Returns:
            Resultados del análisis
        """
        logger.info("=== INICIANDO ANÁLISIS COMPLETO ===")
        start_time = time.time()

        results = {
            "timestamp": datetime.now().isoformat(),
            "status": "in_progress",
            "total_responses": 0,
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

            # 3. Análisis estadístico
            logger.info("Paso 3: Ejecutando análisis estadístico...")

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

            # 4. Correlaciones
            logger.info("Paso 4: Calculando correlaciones...")
            corr_matrix = self.correlation_analysis.calculate_correlation_matrix(df_processed)
            pairwise_corr = self.correlation_analysis.calculate_pairwise_correlations(df_processed)
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

            # 5. Regresión / Factores
            logger.info("Paso 5: Analizando factores predictores...")
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

            # 6. Clustering
            logger.info("Paso 6: Ejecutando clustering...")
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

            # 7. Guardar datos procesados
            logger.info("Paso 7: Guardando resultados...")
            output_path = os.path.join(
                self.base_dir,
                self.config.get("paths", {}).get("data_processed", "data/processed"),
                f"resultados_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            )
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            df_clustered.to_csv(output_path, index=False, encoding="utf-8-sig")

            # 8. Generar reporte PDF
            pdf_path = None
            if generate_report:
                logger.info("Paso 8: Generando reporte PDF...")
                pdf_path = os.path.join(
                    self.base_dir,
                    self.config.get("paths", {}).get("reports", "reports"),
                    f"reporte_ejecutivo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                )

                self.report_generator.generate_executive_report(
                    output_path=pdf_path,
                    summary_stats=results,
                    dimension_stats=results["dimension_stats"],
                    correlations=results["correlations"],
                    regression_results=results["regression"],
                    cluster_profiles=cluster_profiles,
                    total_responses=results["total_responses"],
                )

            # 9. Enviar notificación
            if send_notification:
                logger.info("Paso 9: Enviando notificación...")
                notification_stats = {
                    "total_responses": results["total_responses"],
                    "global_mean": results.get("global_mean", 0),
                    "global_std": results.get("global_std", 0),
                    "dimensions": results["dimension_stats"],
                    "analysis_date": datetime.now().strftime("%d/%m/%Y %H:%M"),
                }
                self.email_notifier.send_analysis_notification(
                    stats=notification_stats,
                    pdf_path=pdf_path,
                )

            # Guardar en histórico
            results["status"] = "completed"
            results["duration_seconds"] = round(time.time() - start_time, 2)
            self._save_history(results)

            logger.info(
                f"=== ANÁLISIS COMPLETADO en {results['duration_seconds']}s ==="
            )

            return results

        except Exception as e:
            logger.error(f"Error durante el análisis: {e}")
            results["status"] = "error"
            results["error"] = str(e)
            return results

    def check_for_new_responses(self) -> bool:
        """
        Verifica si hay nuevas respuestas.

        Returns:
            True si hay nuevas respuestas
        """
        return self.collector.has_new_responses(self.last_check)

    def start_automatic_monitoring(self):
        """Inicia el monitoreo automático."""
        interval = self.config.get("orchestrator", {}).get("check_interval_minutes", 30)

        logger.info(f"Iniciando monitoreo automático (cada {interval} minutos)")

        def check_and_analyze():
            if self.check_for_new_responses():
                logger.info("Nuevas respuestas detectadas, ejecutando análisis...")
                self.run_full_analysis(send_notification=True)
                self.last_check = datetime.now()
            else:
                logger.debug("No hay nuevas respuestas")

        # Programar verificación periódica
        schedule.every(interval).minutes.do(check_and_analyze)

        # Ejecutar inmediatamente
        check_and_analyze()

        # Mantener ejecutándose
        logger.info("Monitoreo en ejecución. Presiona Ctrl+C para detener.")
        while True:
            schedule.run_pending()
            time.sleep(60)

    def start_scheduled_analysis(self, time_str: str = "08:00"):
        """
        Programa análisis diario a una hora específica.

        Args:
            time_str: Hora de ejecución (formato HH:MM)
        """
        logger.info(f"Programando análisis diario a las {time_str}")

        schedule.every().day.at(time_str).do(
            self.run_full_analysis, send_notification=True
        )

        logger.info("Programación activa. Presiona Ctrl+C para detener.")
        while True:
            schedule.run_pending()
            time.sleep(60)


def main():
    """Función principal para ejecución directa."""
    import argparse

    parser = argparse.ArgumentParser(description="Agente de Análisis de Bienestar Estudiantil")
    parser.add_argument(
        "--mode",
        choices=["manual", "auto", "scheduled"],
        default="manual",
        help="Modo de ejecución",
    )
    parser.add_argument("--file", type=str, help="Ruta al archivo CSV (modo manual)")
    parser.add_argument("--time", type=str, default="08:00", help="Hora de análisis programado")

    args = parser.parse_args()

    orchestrator = AgentOrchestrator()

    if args.mode == "manual":
        orchestrator.run_full_analysis(
            data_source="file" if args.file else "api",
            file_path=args.file,
        )
    elif args.mode == "auto":
        orchestrator.start_automatic_monitoring()
    elif args.mode == "scheduled":
        orchestrator.start_scheduled_analysis(args.time)


if __name__ == "__main__":
    main()
