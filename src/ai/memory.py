"""
Módulo de memoria del agente de IA.
Almacena análisis pasados y permite aprendizaje continuo.
"""

import json
import os
from datetime import datetime
from typing import Optional
import numpy as np

from src.utils.logger import get_logger

logger = get_logger(__name__)


class AgentMemory:
    """Memoria del agente para aprendizaje continuo."""

    def __init__(self, memory_file: str = "data/processed/agent_memory.json"):
        """
        Inicializa la memoria.

        Args:
            memory_file: Archivo donde se guarda la memoria
        """
        self.memory_file = memory_file
        self.memory = self._load_memory()

    def _load_memory(self) -> dict:
        """Carga la memoria desde disco."""
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error al cargar memoria: {e}")

        return {
            "analyses": [],
            "patterns": {},
            "insights": [],
            "decisions": [],
            "performance": [],
        }

    def save_memory(self):
        """Guarda la memoria en disco."""
        try:
            os.makedirs(os.path.dirname(self.memory_file), exist_ok=True)
            with open(self.memory_file, "w", encoding="utf-8") as f:
                json.dump(self.memory, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error al guardar memoria: {e}")

    def store_analysis(self, results: dict):
        """
        Almacena los resultados de un análisis.

        Args:
            results: Resultados del análisis
        """
        analysis_entry = {
            "timestamp": datetime.now().isoformat(),
            "total_responses": results.get("total_responses", 0),
            "global_mean": results.get("global_mean", 0),
            "global_std": results.get("global_std", 0),
            "dimensions": results.get("dimension_stats", []),
            "clusters": results.get("clusters", []),
            "ai_interpretation": results.get("ai_interpretation", ""),
            "ai_recommendations": results.get("ai_recommendations", []),
        }

        self.memory["analyses"].append(analysis_entry)

        # Mantener solo los últimos 50 análisis
        if len(self.memory["analyses"]) > 50:
            self.memory["analyses"] = self.memory["analyses"][-50:]

        self.save_memory()
        logger.info(f"Análisis almacenado en memoria ({len(self.memory['analyses'])} total)")

    def get_trends(self, dimension: Optional[str] = None) -> dict:
        """
        Obtiene tendencias de análisis pasados.

        Args:
            dimension: Dimensión específica a analizar (None = todas)

        Returns:
            Diccionario con tendencias
        """
        analyses = self.memory["analyses"]

        if len(analyses) < 2:
            return {"trend": "insufficient_data", "message": "Se necesitan al menos 2 análisis"}

        trends = {
            "num_analyses": len(analyses),
            "global_trend": self._calculate_trend([a.get("global_mean", 0) for a in analyses]),
            "dimensions": {},
        }

        if dimension:
            dim_values = []
            for a in analyses:
                for d in a.get("dimensions", []):
                    if d.get("dimension") == dimension:
                        dim_values.append(d.get("mean", 0))
            if dim_values:
                trends["dimensions"][dimension] = self._calculate_trend(dim_values)
        else:
            # Analizar todas las dimensiones
            dim_names = set()
            for a in analyses:
                for d in a.get("dimensions", []):
                    dim_names.add(d.get("dimension"))

            for dim_name in dim_names:
                dim_values = []
                for a in analyses:
                    for d in a.get("dimensions", []):
                        if d.get("dimension") == dim_name:
                            dim_values.append(d.get("mean", 0))
                if dim_values:
                    trends["dimensions"][dim_name] = self._calculate_trend(dim_values)

        return trends

    def detect_patterns(self) -> list[dict]:
        """
        Detecta patrones en los análisis pasados.

        Returns:
            Lista de patrones detectados
        """
        patterns = []
        analyses = self.memory["analyses"]

        if len(analyses) < 3:
            return patterns

        # Patrón 1: Dimensión consistentemente baja
        dim_scores = {}
        for a in analyses:
            for d in a.get("dimensions", []):
                dim_name = d.get("dimension")
                if dim_name not in dim_scores:
                    dim_scores[dim_name] = []
                dim_scores[dim_name].append(d.get("mean", 0))

        for dim_name, scores in dim_scores.items():
            avg_score = np.mean(scores)
            std_score = np.std(scores)

            if avg_score < 3.0 and std_score < 0.5:
                patterns.append({
                    "type": "consistently_low",
                    "dimension": dim_name,
                    "avg_score": round(float(avg_score), 3),
                    "std": round(float(std_score), 3),
                    "confidence": "high",
                    "message": f"La dimensión '{dim_name}' ha sido consistentemente baja (promedio: {avg_score:.2f})"
                })

        # Patrón 2: Mejora o deterioro
        if len(analyses) >= 3:
            recent = analyses[-3:]
            global_means = [a.get("global_mean", 0) for a in recent]

            if all(global_means[i] < global_means[i+1] for i in range(len(global_means)-1)):
                patterns.append({
                    "type": "improving",
                    "metric": "global_mean",
                    "direction": "up",
                    "message": "El bienestar global ha mejorado en los últimos 3 análisis"
                })
            elif all(global_means[i] > global_means[i+1] for i in range(len(global_means)-1)):
                patterns.append({
                    "type": "declining",
                    "metric": "global_mean",
                    "direction": "down",
                    "message": "El bienestar global ha disminuido en los últimos 3 análisis"
                })

        self.memory["patterns"] = patterns
        self.save_memory()

        logger.info(f"Patrones detectados: {len(patterns)}")
        return patterns

    def get_insights(self) -> list[str]:
        """
        Genera insights basados en la memoria.

        Returns:
            Lista de insights
        """
        insights = []
        analyses = self.memory["analyses"]

        if not analyses:
            return ["Sin datos históricos disponibles"]

        latest = analyses[-1]

        # Insight: Total de participantes
        insights.append(f"Se han analizado {latest.get('total_responses', 0)} estudiantes en total")

        # Insight: Bienestar global
        global_mean = latest.get("global_mean", 0)
        if global_mean >= 5:
            insights.append(f"El bienestar global es ALTO ({global_mean:.2f}/6.00)")
        elif global_mean >= 3.5:
            insights.append(f"El bienestar global es MEDIO ({global_mean:.2f}/6.00)")
        else:
            insights.append(f"El bienestar global es BAJO ({global_mean:.2f}/6.00)")

        # Insight: Dimensión más débil
        dimensions = latest.get("dimensions", [])
        if dimensions:
            weakest = min(dimensions, key=lambda x: x.get("mean", 0))
            insights.append(f"La dimensión más débil es '{weakest.get('dimension')}' ({weakest.get('mean', 0):.2f})")

        # Insight: Patrones detectados
        patterns = self.detect_patterns()
        for p in patterns[:3]:
            insights.append(p.get("message", ""))

        self.memory["insights"] = insights
        self.save_memory()

        return insights

    def record_decision(self, decision: dict):
        """
        Registra una decisión tomada por el agente.

        Args:
            decision: Diccionario con la decisión
        """
        decision_entry = {
            "timestamp": datetime.now().isoformat(),
            "action": decision.get("action"),
            "reason": decision.get("reason"),
            "confidence": decision.get("confidence"),
            "outcome": decision.get("outcome", "pending"),
        }

        self.memory["decisions"].append(decision_entry)

        # Mantener solo las últimas 100 decisiones
        if len(self.memory["decisions"]) > 100:
            self.memory["decisions"] = self.memory["decisions"][-100:]

        self.save_memory()
        logger.info(f"Decisión registrada: {decision.get('action')}")

    def get_performance_metrics(self) -> dict:
        """
        Obtiene métricas de rendimiento del agente.

        Returns:
            Métricas de rendimiento
        """
        analyses = self.memory["analyses"]
        decisions = self.memory["decisions"]

        metrics = {
            "total_analyses": len(analyses),
            "total_decisions": len(decisions),
            "avg_response_time": self._calculate_avg_response_time(analyses),
            "success_rate": self._calculate_success_rate(decisions),
        }

        return metrics

    def _calculate_trend(self, values: list) -> dict:
        """Calcula la tendencia de una serie de valores."""
        if len(values) < 2:
            return {"direction": "stable", "change": 0}

        recent = np.mean(values[-3:]) if len(values) >= 3 else values[-1]
        older = np.mean(values[:3]) if len(values) >= 3 else values[0]

        change = recent - older
        pct_change = (change / older * 100) if older != 0 else 0

        if change > 0.1:
            direction = "improving"
        elif change < -0.1:
            direction = "declining"
        else:
            direction = "stable"

        return {
            "direction": direction,
            "change": round(float(change), 3),
            "pct_change": round(float(pct_change), 1),
            "recent_avg": round(float(recent), 3),
            "older_avg": round(float(older), 3),
        }

    def _calculate_avg_response_time(self, analyses: list) -> float:
        """Calcula tiempo promedio de respuesta."""
        # Por ahora retorna 0, se implementaría con timestamps de análisis
        return 0.0

    def _calculate_success_rate(self, decisions: list) -> float:
        """Calcula tasa de éxito de decisiones."""
        if not decisions:
            return 100.0

        successful = sum(1 for d in decisions if d.get("outcome") == "success")
        return round((successful / len(decisions)) * 100, 1)
