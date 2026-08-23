"""
Módulo de análisis de factores asociados al bienestar.
"""

from typing import Optional
from dataclasses import dataclass

import pandas as pd
import numpy as np
from scipy import stats
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler

from src.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class FactorImportance:
    """Importancia de un factor en el modelo predictivo."""

    factor: str
    coefficient: float
    std_coefficient: float
    p_value: float
    significant: bool
    variance_explained: float


class FactorAnalysis:
    """Análisis de factores asociados al bienestar."""

    def __init__(self, config: dict):
        """
        Inicializa el análisis.

        Args:
            config: Configuración del proyecto
        """
        self.analysis_config = config.get("analysis", {})
        self.significance_level = self.analysis_config.get("significance_level", 0.05)
        self.dimensions = config.get("survey", {}).get("dimensions", [])

    def regression_analysis(self, df: pd.DataFrame) -> dict:
        """
        Análisis de regresión para identificar predictores del bienestar.

        Args:
            df: DataFrame con puntajes

        Returns:
            Resultados de la regresión
        """
        if "wellbeing_global" not in df.columns:
            logger.warning("No se encontró columna 'wellbeing_global'")
            return {}

        score_columns = [f"score_{d['id']}" for d in self.dimensions]
        score_columns = [col for col in score_columns if col in df.columns]

        # Preparar datos
        X = df[score_columns].dropna()
        y = df.loc[X.index, "wellbeing_global"]

        if len(X) < 30:
            logger.warning("Muy pocos casos para regresión confiable")

        # Estandarizar variables
        scaler = StandardScaler()
        X_scaled = pd.DataFrame(
            scaler.fit_transform(X), columns=score_columns, index=X.index
        )

        # Regresión lineal
        model = LinearRegression()
        model.fit(X_scaled, y)

        # Coeficientes estandarizados
        std_coefficients = model.coef_

        # Calcular p-values usando t-test
        n = len(X)
        p = len(score_columns)
        residuals = y - model.predict(X_scaled)
        mse = np.sum(residuals ** 2) / (n - p - 1)
        var_coef = mse * np.linalg.inv(X_scaled.T @ X_scaled).diagonal()
        std_errors = np.sqrt(var_coef)
        t_values = model.coef_ / std_errors
        p_values = 2 * (1 - stats.t.cdf(np.abs(t_values), df=n - p - 1))

        # R²
        r_squared = model.score(X_scaled, y)

        # Construir resultados
        factors = []
        dim_names = {f"score_{d['id']}": d["name"] for d in self.dimensions}

        for i, col in enumerate(score_columns):
            factor_name = dim_names.get(col, col)

            factor = FactorImportance(
                factor=factor_name,
                coefficient=round(float(model.coef_[i]), 4),
                std_coefficient=round(float(std_coefficients[i]), 4),
                p_value=round(float(p_values[i]), 4),
                significant=p_values[i] < self.significance_level,
                variance_explained=round(float(std_coefficients[i] ** 2 * 100), 2),
            )
            factors.append(factor)

        # Ordenar por importancia (coeficiente estandarizado absoluto)
        factors.sort(key=lambda x: abs(x.std_coefficient), reverse=True)

        result = {
            "r_squared": round(float(r_squared), 4),
            "r_squared_pct": round(float(r_squared * 100), 2),
            "adj_r_squared": round(float(1 - (1 - r_squared) * (n - 1) / (n - p - 1)), 4),
            "n_observations": int(n),
            "factors": factors,
        }

        logger.info(f"Regresión: R² = {r_squared:.4f}, {len(factors)} factores analizados")
        return result

    def correlation_with_global(self, df: pd.DataFrame) -> list[dict]:
        """
        Correlación de cada dimensión con el puntaje global.

        Args:
            df: DataFrame con puntajes

        Returns:
            Lista de correlaciones
        """
        if "wellbeing_global" not in df.columns:
            return []

        results = []
        dim_names = {d["id"]: d["name"] for d in self.dimensions}

        for dimension in self.dimensions:
            col = f"score_{dimension['id']}"

            if col not in df.columns:
                continue

            data = df[[col, "wellbeing_global"]].dropna()

            if len(data) < 10:
                continue

            corr, p_value = stats.spearmanr(data[col], data["wellbeing_global"])

            results.append({
                "dimension": dim_names.get(dimension["id"], dimension["id"]),
                "correlation": round(float(corr), 4),
                "p_value": round(float(p_value), 4),
                "significant": p_value < self.significance_level,
            })

        # Ordenar por correlación absoluta
        results.sort(key=lambda x: abs(x["correlation"]), reverse=True)

        logger.info(f"Correlaciones con global: {len(results)} dimensiones")
        return results

    def group_comparison_factors(
        self, df: pd.DataFrame, group_var: str
    ) -> list[dict]:
        """
        Compara dimensiones entre grupos para identificar diferencias.

        Args:
            df: DataFrame con puntajes
            group_var: Variable de agrupación

        Returns:
            Lista de comparaciones por dimensión
        """
        results = []

        dim_names = {d["id"]: d["name"] for d in self.dimensions}

        for dimension in self.dimensions:
            col = f"score_{dimension['id']}"

            if col not in df.columns:
                continue

            groups = df[group_var].unique()
            group_data = [df[df[group_var] == g][col].dropna() for g in groups]
            group_data = [(g, data) for g, data in zip(groups, group_data) if len(data) > 0]

            if len(group_data) < 2:
                continue

            # ANOVA
            group_values = [data for _, data in group_data]
            f_stat, p_value = stats.f_oneway(*group_values)

            # Medias por grupo
            group_means = {str(g): round(float(data.mean()), 3) for g, data in group_data}

            results.append({
                "dimension": dim_names.get(dimension["id"], dimension["id"]),
                "f_statistic": round(float(f_stat), 4),
                "p_value": round(float(p_value), 4),
                "significant": p_value < self.significance_level,
                "group_means": group_means,
            })

        # Ordenar por significancia
        results.sort(key=lambda x: x["p_value"])

        logger.info(f"Comparación por {group_var}: {len(results)} dimensiones analizadas")
        return results
