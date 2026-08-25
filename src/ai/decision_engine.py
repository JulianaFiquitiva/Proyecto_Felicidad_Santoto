"""
Motor de decisiones del agente de IA.
Toma decisiones autónomas basadas en análisis y memoria.
"""

from datetime import datetime
from typing import Optional
import numpy as np

from src.utils.logger import get_logger

logger = get_logger(__name__)


class DecisionEngine:
    """Motor que toma decisiones autónomas."""

    # Umbrales para decisiones
    THRESHOLDS = {
        "critical_low": 2.5,      # Críticamente bajo
        "low": 3.5,               # Bajo
        "medium": 4.0,            # Medio
        "high": 5.0,              # Alto
        "very_high": 5.5,         # Muy alto
        "significant_change": 0.5, # Cambio significativo
        "urgent_change": 1.0,     # Cambio urgente
        "min_participants": 30,   # Mínimo participantes para análisis válido
    }

    # Acciones posibles
    ACTIONS = {
        "ALERT_URGENT": "alert_urgent",
        "ALERT_WARNING": "alert_warning",
        "SUGGEST_INTERVENTION": "suggest_intervention",
        "SUGGEST_SURVEY": "suggest_survey",
        "SUGGEST_DEEP_ANALYSIS": "suggest_deep_analysis",
        "SUGGEST_COMPARISON": "suggest_comparison",
        "PRAISE_IMPROVEMENT": "praise_improvement",
        "SUGGEST_CELEBRATION": "suggest_celebration",
        "LOG_INSIGHT": "log_insight",
        "NO_ACTION": "no_action",
    }

    def __init__(self, memory=None):
        """
        Inicializa el motor de decisiones.

        Args:
            memory: Instancia de AgentMemory
        """
        self.memory = memory

    def analyze_and_decide(self, results: dict) -> list[dict]:
        """
        Analiza resultados y toma decisiones.

        Args:
            results: Resultados del análisis

        Returns:
            Lista de decisiones tomadas
        """
        decisions = []

        # Analizar bienestar global
        global_decisions = self._analyze_global(results)
        decisions.extend(global_decisions)

        # Analizar dimensiones
        dimension_decisions = self._analyze_dimensions(results)
        decisions.extend(dimension_decisions)

        # Analizar cambios (si hay memoria)
        if self.memory:
            change_decisions = self._analyze_changes(results)
            decisions.extend(change_decisions)

        # Analizar patrones
        pattern_decisions = self._analyze_patterns(results)
        decisions.extend(pattern_decisions)

        # Analizar calidad de datos
        quality_decisions = self._analyze_data_quality(results)
        decisions.extend(quality_decisions)

        # Registrar decisiones
        if self.memory:
            for decision in decisions:
                self.memory.record_decision(decision)

        logger.info(f"Decisiones tomadas: {len(decisions)}")
        return decisions

    def _analyze_global(self, results: dict) -> list[dict]:
        """Analiza el bienestar global."""
        decisions = []
        global_mean = results.get("global_mean", 0)

        if global_mean < self.THRESHOLDS["critical_low"]:
            decisions.append({
                "action": self.ACTIONS["ALERT_URGENT"],
                "reason": f"Bienestar global CRÍTICAMENTE BAJO ({global_mean:.2f}/6.00)",
                "confidence": 0.95,
                "priority": "urgent",
                "recommendation": "Se requiere intervención inmediata. Considerar programs de apoyo psicológico urgente.",
            })
        elif global_mean < self.THRESHOLDS["low"]:
            decisions.append({
                "action": self.ACTIONS["ALERT_WARNING"],
                "reason": f"Bienestar global BAJO ({global_mean:.2f}/6.00)",
                "confidence": 0.9,
                "priority": "high",
                "recommendation": "Desarrollar programas de mejora del bienestar estudiantil.",
            })
        elif global_mean >= self.THRESHOLDS["high"]:
            decisions.append({
                "action": self.ACTIONS["PRAISE_IMPROVEMENT"],
                "reason": f"Bienestar global ALTO ({global_mean:.2f}/6.00)",
                "confidence": 0.85,
                "priority": "low",
                "recommendation": "Mantener las estrategias actuales. Compartir buenas prácticas.",
            })

        return decisions

    def _analyze_dimensions(self, results: dict) -> list[dict]:
        """Analiza cada dimensión individualmente."""
        decisions = []
        dimensions = results.get("dimension_stats", [])

        if not dimensions:
            return decisions

        # Encontrar dimensión más débil
        weakest = min(dimensions, key=lambda x: x.get("mean", 0))
        strongest = max(dimensions, key=lambda x: x.get("mean", 0))

        # Decisión: Dimensión crítica
        if weakest.get("mean", 0) < self.THRESHOLDS["critical_low"]:
            decisions.append({
                "action": self.ACTIONS["ALERT_URGENT"],
                "reason": f"Dimensión '{weakest.get('dimension')}' en nivel CRÍTICO ({weakest.get('mean', 0):.2f})",
                "confidence": 0.95,
                "priority": "urgent",
                "dimension": weakest.get("dimension"),
                "recommendation": f"Diseñar intervención específica para mejorar '{weakest.get('dimension')}'.",
            })
        elif weakest.get("mean", 0) < self.THRESHOLDS["low"]:
            decisions.append({
                "action": self.ACTIONS["SUGGEST_INTERVENTION"],
                "reason": f"Dimensión '{weakest.get('dimension')}' requiere atención ({weakest.get('mean', 0):.2f})",
                "confidence": 0.85,
                "priority": "high",
                "dimension": weakest.get("dimension"),
                "recommendation": f"Crear talleres o actividades enfocadas en '{weakest.get('dimension')}'.",
            })

        # Decisión: Dimensión destacada
        if strongest.get("mean", 0) >= self.THRESHOLDS["very_high"]:
            decisions.append({
                "action": self.ACTIONS["SUGGEST_CELEBRATION"],
                "reason": f"Dimensión '{strongest.get('dimension')}' destacada ({strongest.get('mean', 0):.2f})",
                "confidence": 0.8,
                "priority": "low",
                "dimension": strongest.get("dimension"),
                "recommendation": f"Reconocer y replicar el éxito en '{strongest.get('dimension')}'.",
            })

        # Decisión: Gran disparidad entre dimensiones
        means = [d.get("mean", 0) for d in dimensions]
        if max(means) - min(means) > 2.0:
            decisions.append({
                "action": self.ACTIONS["SUGGEST_DEEP_ANALYSIS"],
                "reason": "Gran disparidad entre dimensiones del bienestar",
                "confidence": 0.8,
                "priority": "medium",
                "recommendation": "Investigar las causas de las diferencias entre dimensiones.",
            })

        return decisions

    def _analyze_changes(self, results: dict) -> list[dict]:
        """Analiza cambios con respecto a análisis anteriores."""
        decisions = []

        if not self.memory:
            return decisions

        trends = self.memory.get_trends()
        global_trend = trends.get("global_trend", {})

        if global_trend.get("direction") == "declining":
            change = abs(global_trend.get("change", 0))

            if change >= self.THRESHOLDS["urgent_change"]:
                decisions.append({
                    "action": self.ACTIONS["ALERT_URGENT"],
                    "reason": f"Bienestar global en DECLIVE URGENTE (cambio: {global_trend.get('change', 0):.3f})",
                    "confidence": 0.9,
                    "priority": "urgent",
                    "recommendation": "Implementar medidas correctivas inmediatas.",
                })
            elif change >= self.THRESHOLDS["significant_change"]:
                decisions.append({
                    "action": self.ACTIONS["ALERT_WARNING"],
                    "reason": f"Bienestar global en declive (cambio: {global_trend.get('change', 0):.3f})",
                    "confidence": 0.85,
                    "priority": "high",
                    "recommendation": "Monitorear de cerca e implementar mejoras.",
                })

        elif global_trend.get("direction") == "improving":
            change = global_trend.get("change", 0)

            if change >= self.THRESHOLDS["significant_change"]:
                decisions.append({
                    "action": self.ACTIONS["PRAISE_IMPROVEMENT"],
                    "reason": f"Bienestar global MEJORANDO significativamente (+{change:.3f})",
                    "confidence": 0.85,
                    "priority": "low",
                    "recommendation": "Documentar las estrategias exitosas para replicarlas.",
                })

        return decisions

    def _analyze_patterns(self, results: dict) -> list[dict]:
        """Analiza patrones detectados."""
        decisions = []

        if not self.memory:
            return decisions

        patterns = self.memory.detect_patterns()

        for pattern in patterns:
            if pattern.get("type") == "consistently_low":
                decisions.append({
                    "action": self.ACTIONS["SUGGEST_INTERVENTION"],
                    "reason": f"Patrón detectado: {pattern.get('message')}",
                    "confidence": 0.85,
                    "priority": "high",
                    "dimension": pattern.get("dimension"),
                    "recommendation": f"Implementar programa de mejora sostenido para '{pattern.get('dimension')}'.",
                })

            elif pattern.get("type") == "declining":
                decisions.append({
                    "action": self.ACTIONS["ALERT_WARNING"],
                    "reason": f"Tendencia negativa detectada: {pattern.get('message')}",
                    "confidence": 0.8,
                    "priority": "high",
                    "recommendation": "Investigar causas del declive y diseñar plan de acción.",
                })

        return decisions

    def _analyze_data_quality(self, results: dict) -> list[dict]:
        """Analiza la calidad de los datos."""
        decisions = []
        total_responses = results.get("total_responses", 0)

        if total_responses < self.THRESHOLDS["min_participants"]:
            decisions.append({
                "action": self.ACTIONS["SUGGEST_SURVEY"],
                "reason": f"Muestra insuficiente ({total_responses} participantes)",
                "confidence": 0.9,
                "priority": "medium",
                "recommendation": f"Se recomienda un mínimo de {self.THRESHOLDS['min_participants']} participantes para resultados confiables.",
            })

        return decisions

    def get_action_summary(self, decisions: list[dict]) -> dict:
        """
        Genera un resumen de las decisiones.

        Args:
            decisions: Lista de decisiones

        Returns:
            Resumen de decisiones
        """
        summary = {
            "total": len(decisions),
            "urgent": sum(1 for d in decisions if d.get("priority") == "urgent"),
            "high": sum(1 for d in decisions if d.get("priority") == "high"),
            "medium": sum(1 for d in decisions if d.get("priority") == "medium"),
            "low": sum(1 for d in decisions if d.get("priority") == "low"),
            "actions": [],
        }

        for decision in decisions:
            summary["actions"].append({
                "action": decision.get("action"),
                "reason": decision.get("reason"),
                "priority": decision.get("priority"),
            })

        return summary
