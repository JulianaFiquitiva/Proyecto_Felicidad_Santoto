"""
Agente Autónomo de Análisis de Bienestar Psicológico.
Integra memoria, decisiones y aprendizaje continuo.
"""

import json
from datetime import datetime
from typing import Optional
import numpy as np

from src.ai.memory import AgentMemory
from src.ai.decision_engine import DecisionEngine
from src.ai.interpreter import AIInterpreter
from src.utils.logger import get_logger

logger = get_logger(__name__)


class AutonomousAgent:
    """
    Agente de IA autónomo que:
    1. Analiza datos de bienestar psicológico
    2. Toma decisiones basadas en hallazgos
    3. Aprende de cada análisis
    4. Genera recomendaciones adaptativas
    5. Monitorea tendencias y patrones
    """

    def __init__(self, config: dict):
        """
        Inicializa el agente autónomo.

        Args:
            config: Configuración completa del proyecto
        """
        self.config = config
        self.memory = AgentMemory()
        self.decision_engine = DecisionEngine(memory=self.memory)
        self.interpreter = AIInterpreter(config)
        self.state = {
            "status": "idle",
            "last_analysis": None,
            "total_analyses": len(self.memory.memory.get("analyses", [])),
            "pending_actions": [],
        }

        logger.info("Agente autónomo inicializado")

    def run_autonomous_cycle(self, data: dict, csv_file: Optional[str] = None) -> dict:
        """
        Ejecuta un ciclo autónomo completo:
        1. Analiza los datos
        2. Toma decisiones
        3. Genera recomendaciones
        4. Aprende de los resultados
        5. Ejecuta acciones

        Args:
            data: Datos procesados del cuestionario
            csv_file: Ruta al archivo CSV original (opcional)

        Returns:
            Resultados del ciclo autónomo
        """
        logger.info("=== INICIANDO CICLO AUTÓNOMO ===")
        self.state["status"] = "running"

        results = {
            "timestamp": datetime.now().isoformat(),
            "status": "running",
            "phases": {},
        }

        try:
            # Fase 1: Análisis estadístico
            logger.info("Fase 1: Análisis estadístico...")
            analysis_results = self._phase_analysis(data)
            results["phases"]["analysis"] = analysis_results

            # Fase 2: Toma de decisiones
            logger.info("Fase 2: Toma de decisiones...")
            decisions = self._phase_decisions(analysis_results)
            results["phases"]["decisions"] = decisions

            # Fase 3: Generación de recomendaciones adaptativas
            logger.info("Fase 3: Recomendaciones adaptativas...")
            recommendations = self._phase_recommendations(analysis_results, decisions)
            results["phases"]["recommendations"] = recommendations

            # Fase 4: Aprendizaje y memoria
            logger.info("Fase 4: Aprendizaje...")
            learning = self._phase_learning(analysis_results, decisions)
            results["phases"]["learning"] = learning

            # Fase 5: Ejecución de acciones
            logger.info("Fase 5: Ejecución de acciones...")
            actions = self._phase_actions(decisions, recommendations)
            results["phases"]["actions"] = actions

            # Fase 6: Generación de reporte con IA
            logger.info("Fase 6: Generación de reporte IA...")
            ai_report = self._phase_ai_report(analysis_results, decisions, recommendations)
            results["phases"]["ai_report"] = ai_report

            # Actualizar estado
            self.state["status"] = "completed"
            self.state["last_analysis"] = datetime.now().isoformat()
            self.state["total_analyses"] += 1

            results["status"] = "completed"
            results["summary"] = self._generate_cycle_summary(results)

            logger.info("=== CICLO AUTÓNOMO COMPLETADO ===")

        except Exception as e:
            logger.error(f"Error en ciclo autónomo: {e}")
            self.state["status"] = "error"
            results["status"] = "error"
            results["error"] = str(e)

        return results

    def _phase_analysis(self, data: dict) -> dict:
        """Fase 1: Análisis estadístico de los datos."""
        from src.analysis.statistics import StatisticalAnalysis
        from src.analysis.correlations import CorrelationAnalysis
        from src.analysis.clustering import ClusteringAnalysis
        from src.analysis.factors import FactorAnalysis

        stats_analyzer = StatisticalAnalysis(self.config)
        corr_analyzer = CorrelationAnalysis(self.config)
        cluster_analyzer = ClusteringAnalysis(self.config)
        factor_analyzer = FactorAnalysis(self.config)

        results = {}

        # Obtener DataFrame procesado
        df_processed = data.get("df_processed")
        if df_processed is None:
            logger.error("No se encontró df_processed en los datos")
            return results

        # Estadísticas descriptivas
        dimension_stats = stats_analyzer.descriptive_statistics(df_processed)
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
        else:
            means = [d.get("mean", 0) for d in results["dimension_stats"]]
            results["global_mean"] = float(np.mean(means)) if means else 0
            results["global_std"] = float(np.std(means)) if means else 0

        # Correlaciones
        global_corr = corr_analyzer.correlate_with_global(df_processed)
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

        # Regresión lineal múltiple
        regression_results = factor_analyzer.regression_analysis(df_processed)
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

        # Regresión logística (predecir bienestar bajo)
        logistic_results = factor_analyzer.logistic_regression(df_processed)
        results["logistic_regression"] = logistic_results

        # Regresión Ridge
        ridge_results = factor_analyzer.ridge_regression(df_processed)
        results["ridge_regression"] = ridge_results

        # Regresión Lasso
        lasso_results = factor_analyzer.lasso_regression(df_processed)
        results["lasso_regression"] = lasso_results

        # Regresión polinómica
        poly_results = factor_analyzer.polynomial_regression(df_processed)
        results["polynomial_regression"] = poly_results

        # Regresión stepwise
        stepwise_results = factor_analyzer.stepwise_regression(df_processed)
        results["stepwise_regression"] = stepwise_results

        # ANOVA por género si existe la columna
        if "genero" in df_processed.columns:
            anova_results = factor_analyzer.anova_comparison(df_processed, "genero")
            results["anova_gender"] = anova_results

        # Clustering
        df_clustered = cluster_analyzer.fit_clusters(df_processed)
        cluster_profiles = cluster_analyzer.get_cluster_profiles(df_clustered)
        results["clusters"] = [
            {
                "id": p.cluster_id,
                "size": p.size,
                "percentage": p.percentage,
                "label": p.label,
            }
            for p in cluster_profiles
        ]

        results["total_responses"] = data.get("total_rows", len(df_processed))

        return results

    def _phase_decisions(self, analysis_results: dict) -> dict:
        """Fase 2: Toma de decisiones basada en análisis."""
        decisions = self.decision_engine.analyze_and_decide(analysis_results)
        summary = self.decision_engine.get_action_summary(decisions)

        return {
            "decisions": decisions,
            "summary": summary,
        }

    def _phase_recommendations(self, analysis_results: dict, decisions: dict) -> dict:
        """Fase 3: Generación de recomendaciones adaptativas."""
        recommendations = []

        for decision in decisions.get("decisions", []):
            recommendation = {
                "action": decision.get("action"),
                "reason": decision.get("reason"),
                "recommendation": decision.get("recommendation"),
                "priority": decision.get("priority"),
                "confidence": decision.get("confidence"),
                "adaptive": True,
            }
            recommendations.append(recommendation)

        # Agregar recomendaciones basadas en memoria
        if self.memory:
            insights = self.memory.get_insights()
            for insight in insights[:3]:
                recommendations.append({
                    "action": "insight",
                    "reason": insight,
                    "recommendation": insight,
                    "priority": "info",
                    "confidence": 0.7,
                    "adaptive": True,
                })

        return {
            "recommendations": recommendations,
            "total": len(recommendations),
        }

    def _phase_learning(self, analysis_results: dict, decisions: dict) -> dict:
        """Fase 4: Aprendizaje y actualización de memoria."""
        learning_results = {
            "stored": False,
            "patterns_detected": 0,
            "insights_generated": 0,
        }

        if self.memory:
            # Almacenar análisis
            self.memory.store_analysis(analysis_results)
            learning_results["stored"] = True

            # Detectar patrones
            patterns = self.memory.detect_patterns()
            learning_results["patterns_detected"] = len(patterns)

            # Generar insights
            insights = self.memory.get_insights()
            learning_results["insights_generated"] = len(insights)

            # Obtener métricas de rendimiento
            performance = self.memory.get_performance_metrics()
            learning_results["performance"] = performance

        return learning_results

    def _phase_actions(self, decisions: dict, recommendations: dict) -> dict:
        """Fase 5: Ejecución de acciones."""
        actions_executed = []

        for decision in decisions.get("decisions", []):
            action = decision.get("action")
            priority = decision.get("priority")

            # Determinar si ejecutar la acción
            should_execute = self._should_execute_action(action, priority)

            if should_execute:
                action_result = self._execute_action(decision)
                actions_executed.append({
                    "action": action,
                    "executed": True,
                    "result": action_result,
                })
            else:
                actions_executed.append({
                    "action": action,
                    "executed": False,
                    "reason": "Acción no requerida en este ciclo",
                })

        return {
            "actions_executed": actions_executed,
            "total_executed": sum(1 for a in actions_executed if a.get("executed")),
        }

    def _phase_ai_report(self, analysis_results: dict, decisions: dict, recommendations: dict) -> dict:
        """Fase 6: Generación de reporte con IA."""
        ai_report = {
            "interpretation": "",
            "executive_summary": "",
            "ai_recommendations": [],
        }

        if self.interpreter and self.interpreter.enabled:
            try:
                # Interpretación
                interpretation = self.interpreter.interpret_results(analysis_results)
                ai_report["interpretation"] = interpretation

                # Resumen ejecutivo
                summary = self.interpreter.generate_executive_summary(analysis_results)
                ai_report["executive_summary"] = summary

                # Recomendaciones IA
                ai_recs = self.interpreter.generate_recommendations(analysis_results)
                ai_report["ai_recommendations"] = ai_recs

            except Exception as e:
                logger.error(f"Error en reporte IA: {e}")

        return ai_report

    def _should_execute_action(self, action: str, priority: str) -> bool:
        """Determina si una acción debe ejecutarse."""
        # Ejecutar siempre alertas urgentes
        if priority == "urgent":
            return True

        # Ejecutar acciones de alta prioridad
        if priority == "high":
            return True

        # Para prioridad media, ejecutar solo si es necesario
        if priority == "medium":
            return action in [
                "suggest_intervention",
                "suggest_deep_analysis",
            ]

        # Prioridad baja, no ejecutar
        return False

    def _execute_action(self, decision: dict) -> str:
        """Ejecuta una acción específica."""
        action = decision.get("action")

        # Por ahora, solo registramos la acción
        # En el futuro, aquí se ejecutarían acciones como:
        # - Enviar correos de alerta
        # - Generar reportes especiales
        # - Programar reuniones
        # - Actualizar dashboards

        logger.info(f"Ejecutando acción: {action}")
        return f"Acción '{action}' registrada para ejecución"

    def _generate_cycle_summary(self, results: dict) -> dict:
        """Genera un resumen del ciclo autónomo."""
        phases = results.get("phases", {})

        summary = {
            "total_phases": len(phases),
            "completed_phases": sum(1 for p in phases.values() if p),
            "decisions_made": phases.get("decisions", {}).get("summary", {}).get("total", 0),
            "actions_executed": phases.get("actions", {}).get("total_executed", 0),
            "ai_generated": bool(phases.get("ai_report", {}).get("interpretation")),
        }

        return summary

    def get_agent_status(self) -> dict:
        """Obtiene el estado actual del agente."""
        return {
            "status": self.state["status"],
            "last_analysis": self.state["last_analysis"],
            "total_analyses": self.state["total_analyses"],
            "memory_size": len(self.memory.memory.get("analyses", [])),
            "decisions_count": len(self.memory.memory.get("decisions", [])),
        }

    def get_adaptive_recommendations(self, results: dict) -> list[dict]:
        """
        Genera recomendaciones que se adaptan según el historial.

        Args:
            results: Resultados del análisis actual

        Returns:
            Lista de recomendaciones adaptativas
        """
        recommendations = []

        # Recomendaciones base (de las decisiones)
        decisions = self.decision_engine.analyze_and_decide(results)
        for decision in decisions:
            recommendations.append({
                "type": "decision_based",
                "text": decision.get("recommendation"),
                "priority": decision.get("priority"),
                "source": "decision_engine",
            })

        # Recomendaciones basadas en memoria
        if self.memory:
            patterns = self.memory.detect_patterns()
            for pattern in patterns:
                if pattern.get("type") == "consistently_low":
                    recommendations.append({
                        "type": "pattern_based",
                        "text": f"Mejora sostenida requerida en '{pattern.get('dimension')}' (historial: {pattern.get('avg_score', 0):.2f})",
                        "priority": "high",
                        "source": "memory_pattern",
                    })

            # Recomendaciones basadas en tendencias
            trends = self.memory.get_trends()
            global_trend = trends.get("global_trend", {})
            if global_trend.get("direction") == "improving":
                recommendations.append({
                    "type": "trend_based",
                    "text": "Las estrategias actuales están funcionando. Mantener el enfoque.",
                    "priority": "low",
                    "source": "memory_trend",
                })
            elif global_trend.get("direction") == "declining":
                recommendations.append({
                    "type": "trend_based",
                    "text": "Tendencia negativa detectada. Revisar y ajustar estrategias.",
                    "priority": "high",
                    "source": "memory_trend",
                })

        return recommendations
