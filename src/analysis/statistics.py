"""
Módulo de análisis estadístico descriptivo e inferencial.
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
class DescriptiveStats:
    """Estadísticas descriptivas por dimensión."""

    dimension: str
    n: int
    mean: float
    std: float
    min: float
    max: float
    median: float
    q25: float
    q75: float
    skewness: float
    kurtosis: float


@dataclass
class ReliabilityAnalysis:
    """Análisis de consistencia interna."""

    dimension: str
    cronbach_alpha: float
    num_items: int
    item_total_corr: dict


class StatisticalAnalysis:
    """Análisis estadístico para la escala de Ryff."""

    def __init__(self, config: dict):
        """
        Inicializa el análisis.

        Args:
            config: Configuración del proyecto
        """
        self.analysis_config = config.get("analysis", {})
        self.significance_level = self.analysis_config.get("significance_level", 0.05)
        self.dimensions = config.get("survey", {}).get("dimensions", [])

    def descriptive_statistics(self, df: pd.DataFrame) -> list[DescriptiveStats]:
        """
        Calcula estadísticas descriptivas por dimensión.

        Args:
            df: DataFrame con puntajes por dimensión

        Returns:
            Lista de estadísticas descriptivas
        """
        results = []

        for dimension in self.dimensions:
            dim_id = dimension["id"]
            col_name = f"score_{dim_id}"

            if col_name not in df.columns:
                continue

            data = df[col_name].dropna()

            if len(data) == 0:
                continue

            stats_result = DescriptiveStats(
                dimension=dimension["name"],
                n=len(data),
                mean=round(float(data.mean()), 3),
                std=round(float(data.std()), 3),
                min=round(float(data.min()), 3),
                max=round(float(data.max()), 3),
                median=round(float(data.median()), 3),
                q25=round(float(data.quantile(0.25)), 3),
                q75=round(float(data.quantile(0.75)), 3),
                skewness=round(float(data.skew()), 3),
                kurtosis=round(float(data.kurtosis()), 3),
            )

            results.append(stats_result)
            logger.debug(f"Estadísticas calculadas para {dimension['name']}")

        logger.info(f"Estadísticas descriptivas calculadas para {len(results)} dimensiones")
        return results

    def test_normality(
        self, df: pd.DataFrame, column: str
    ) -> dict:
        """
        Prueba de normalidad (Shapiro-Wilk).

        Args:
            df: DataFrame
            column: Nombre de la columna a probar

        Returns:
            Resultados de la prueba
        """
        data = df[column].dropna()

        if len(data) < 3:
            return {"test": "Shapiro-Wilk", "statistic": None, "p_value": None, "is_normal": None}

        if len(data) > 5000:
            # Para muestras grandes, usar D'Agostino-Pearson
            stat, p_value = stats.normaltest(data)
            test_name = "D'Agostino-Pearson"
        else:
            stat, p_value = stats.shapiro(data)
            test_name = "Shapiro-Wilk"

        is_normal = p_value > self.significance_level

        result = {
            "test": test_name,
            "statistic": round(float(stat), 4),
            "p_value": round(float(p_value), 4),
            "is_normal": is_normal,
        }

        logger.debug(f"Normalidad {column}: {test_name} = {stat:.4f}, p = {p_value:.4f}")
        return result

    def test_homogeneity_variance(
        self, df: pd.DataFrame, dependent_var: str, group_var: str
    ) -> dict:
        """
        Prueba de homogeneidad de varianzas (Levene).

        Args:
            df: DataFrame
            dependent_var: Variable dependiente
            group_var: Variable de agrupación

        Returns:
            Resultados de la prueba
        """
        groups = df[group_var].unique()
        group_data = [df[df[group_var] == g][dependent_var].dropna() for g in groups]

        # Filtrar grupos con datos
        group_data = [g for g in group_data if len(g) > 0]

        if len(group_data) < 2:
            return {"test": "Levene", "statistic": None, "p_value": None, "homogeneous": None}

        stat, p_value = stats.levene(*group_data)

        result = {
            "test": "Levene",
            "statistic": round(float(stat), 4),
            "p_value": round(float(p_value), 4),
            "homogeneous": p_value > self.significance_level,
        }

        logger.debug(f"Levene: F = {stat:.4f}, p = {p_value:.4f}")
        return result

    def compare_groups(
        self, df: pd.DataFrame, dependent_var: str, group_var: str
    ) -> dict:
        """
        Compara grupos (t-test o ANOVA según número de grupos).

        Args:
            df: DataFrame
            dependent_var: Variable dependiente (puntaje)
            group_var: Variable de agrupación

        Returns:
            Resultados de la comparación
        """
        groups = df[group_var].unique()
        group_data = [df[df[group_var] == g][dependent_var].dropna() for g in groups]
        group_data = [(g, data) for g, data in zip(groups, group_data) if len(data) > 0]

        if len(group_data) < 2:
            return {"test": None, "message": "Menos de 2 grupos con datos"}

        group_names = [g for g, _ in group_data]
        group_values = [data for _, data in group_data]

        # Verificar homogeneidad de varianzas
        levene_result = self.test_homogeneity_variance(df, dependent_var, group_var)

        if len(group_names) == 2:
            # t-test
            stat, p_value = stats.ttest_ind(*group_values)
            test_name = "t-test"

            # Calcular tamaño del efecto (d de Cohen)
            n1, n2 = len(group_values[0]), len(group_values[1])
            pooled_std = np.sqrt(
                ((n1 - 1) * group_values[0].std() ** 2 + (n2 - 1) * group_values[1].std() ** 2)
                / (n1 + n2 - 2)
            )
            effect_size = abs(group_values[0].mean() - group_values[1].mean()) / pooled_std if pooled_std > 0 else 0

            result = {
                "test": test_name,
                "statistic": round(float(stat), 4),
                "p_value": round(float(p_value), 4),
                "significant": p_value < self.significance_level,
                "effect_size": round(float(effect_size), 4),
                "effect_size_interpretation": self._interpret_cohens_d(effect_size),
                "groups": {str(g): round(float(data.mean()), 3) for g, data in group_data},
                "levene": levene_result,
            }

        else:
            # ANOVA
            stat, p_value = stats.f_oneway(*group_values)
            test_name = "ANOVA"

            # Tamaño del efecto (eta cuadrado)
            grand_mean = np.concatenate(group_values).mean()
            ss_between = sum(
                len(g) * (g.mean() - grand_mean) ** 2 for g in group_values
            )
            ss_total = sum(
                np.sum((g - grand_mean) ** 2) for g in group_values
            )
            eta_squared = ss_between / ss_total if ss_total > 0 else 0

            result = {
                "test": test_name,
                "statistic": round(float(stat), 4),
                "p_value": round(float(p_value), 4),
                "significant": p_value < self.significance_level,
                "effect_size": round(float(eta_squared), 4),
                "effect_size_interpretation": self._interpret_eta_squared(eta_squared),
                "groups": {str(g): round(float(data.mean()), 3) for g, data in group_data},
                "levene": levene_result,
            }

        logger.info(f"Comparación {group_var}: {test_name} = {stat:.4f}, p = {p_value:.4f}")
        return result

    def _interpret_cohens_d(self, d: float) -> str:
        """Interpreta el tamaño del efecto d de Cohen."""
        d = abs(d)
        if d < 0.2:
            return "Despreciable"
        elif d < 0.5:
            return "Pequeño"
        elif d < 0.8:
            return "Mediano"
        else:
            return "Grande"

    def _interpret_eta_squared(self, eta: float) -> str:
        """Interpreta eta cuadrado."""
        if eta < 0.01:
            return "Despreciable"
        elif eta < 0.06:
            return "Pequeño"
        elif eta < 0.14:
            return "Mediano"
        else:
            return "Grande"
