"""
Módulo de análisis de correlaciones.
"""

from typing import Optional
from dataclasses import dataclass

import pandas as pd
import numpy as np
from scipy import stats
import pingouin as pg

from src.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class CorrelationResult:
    """Resultado de correlación entre dos variables."""

    var1: str
    var2: str
    correlation: float
    p_value: float
    significant: bool
    method: str
    n: int


class CorrelationAnalysis:
    """Análisis de correlaciones entre dimensiones."""

    def __init__(self, config: dict):
        """
        Inicializa el análisis.

        Args:
            config: Configuración del proyecto
        """
        self.analysis_config = config.get("analysis", {})
        self.correlation_method = self.analysis_config.get("correlation_method", "spearman")
        self.significance_level = self.analysis_config.get("significance_level", 0.05)
        self.dimensions = config.get("survey", {}).get("dimensions", [])

    def calculate_correlation_matrix(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calcula la matriz de correlaciones entre dimensiones.

        Args:
            df: DataFrame con puntajes por dimensión

        Returns:
            Matriz de correlaciones
        """
        score_columns = [f"score_{d['id']}" for d in self.dimensions]
        score_columns = [col for col in score_columns if col in df.columns]

        if len(score_columns) < 2:
            logger.warning("Menos de 2 dimensiones para calcular correlaciones")
            return pd.DataFrame()

        # Seleccionar solo las columnas de puntajes
        df_scores = df[score_columns].dropna()

        if len(df_scores) < 10:
            logger.warning("Muy pocos casos para correlaciones confiables")

        # Calcular matriz de correlaciones
        corr_matrix = df_scores.corr(method=self.correlation_method)

        # Renombrar columnas y filas
        dim_names = {f"score_{d['id']}": d["name"] for d in self.dimensions}
        corr_matrix = corr_matrix.rename(index=dim_names, columns=dim_names)

        logger.info(f"Matriz de correlaciones calculada ({self.correlation_method})")
        return corr_matrix

    def calculate_pairwise_correlations(
        self, df: pd.DataFrame
    ) -> list[CorrelationResult]:
        """
        Calcula correlaciones pareadas entre dimensiones.

        Args:
            df: DataFrame con puntajes por dimensión

        Returns:
            Lista de resultados de correlación
        """
        results = []
        score_columns = [f"score_{d['id']}" for d in self.dimensions]
        score_columns = [col for col in score_columns if col in df.columns]

        for i in range(len(score_columns)):
            for j in range(i + 1, len(score_columns)):
                col1, col2 = score_columns[i], score_columns[j]

                data = df[[col1, col2]].dropna()

                if len(data) < 10:
                    continue

                if self.correlation_method == "spearman":
                    corr, p_value = stats.spearmanr(data[col1], data[col2])
                else:
                    corr, p_value = stats.pearsonr(data[col1], data[col2])

                dim1_name = col1.replace("score_", "")
                dim2_name = col2.replace("score_", "")

                result = CorrelationResult(
                    var1=dim1_name,
                    var2=dim2_name,
                    correlation=round(float(corr), 4),
                    p_value=round(float(p_value), 4),
                    significant=p_value < self.significance_level,
                    method=self.correlation_method,
                    n=len(data),
                )

                results.append(result)

        logger.info(f"Calculadas {len(results)} correlaciones pareadas")
        return results

    def correlate_with_global(
        self, df: pd.DataFrame
    ) -> list[CorrelationResult]:
        """
        Correlaciona cada dimensión con el puntaje global.

        Args:
            df: DataFrame con puntajes

        Returns:
            Lista de correlaciones con el global
        """
        results = []

        if "wellbeing_global" not in df.columns:
            logger.warning("No se encontró columna 'wellbeing_global'")
            return results

        for dimension in self.dimensions:
            col = f"score_{dimension['id']}"

            if col not in df.columns:
                continue

            data = df[[col, "wellbeing_global"]].dropna()

            if len(data) < 10:
                continue

            if self.correlation_method == "spearman":
                corr, p_value = stats.spearmanr(data[col], data["wellbeing_global"])
            else:
                corr, p_value = stats.pearsonr(data[col], data["wellbeing_global"])

            result = CorrelationResult(
                var1=dimension["name"],
                var2="Bienestar Global",
                correlation=round(float(corr), 4),
                p_value=round(float(p_value), 4),
                significant=p_value < self.significance_level,
                method=self.correlation_method,
                n=len(data),
            )

            results.append(result)

        logger.info(f"Correlaciones con global calculadas: {len(results)}")
        return results

    def interpret_correlation(self, r: float) -> str:
        """
        Interpreta el valor de correlación.

        Args:
            r: Coeficiente de correlación

        Returns:
            Interpretación textual
        """
        r = abs(r)

        if r < 0.1:
            return "Despreciable"
        elif r < 0.3:
            return "Débil"
        elif r < 0.5:
            return "Moderada"
        elif r < 0.7:
            return "Fuerte"
        else:
            return "Muy fuerte"
