"""
Módulo de análisis de factores asociados al bienestar.
Incluye múltiples modelos de regresión.
"""

from typing import Optional
from dataclasses import dataclass, field

import pandas as pd
import numpy as np
from scipy import stats
from sklearn.linear_model import (
    LinearRegression,
    LogisticRegression,
    Ridge,
    Lasso,
)
from sklearn.preprocessing import StandardScaler, PolynomialFeatures
from sklearn.model_selection import cross_val_score
from sklearn.metrics import accuracy_score, roc_auc_score, confusion_matrix

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


@dataclass
class LogisticResult:
    """Resultado de regresión logística."""
    accuracy: float
    auc_roc: float
    confusion_matrix: list
    odds_ratios: dict
    factors: list
    significant_factors: list


@dataclass
class RegularizationResult:
    """Resultado de regresión con regularización."""
    model_type: str
    alpha: float
    r_squared: float
    adj_r_squared: float
    coefficients: dict
    mse: float


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
        Análisis de regresión lineal múltiple.

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

        logger.info(f"Regresión lineal: R² = {r_squared:.4f}, {len(factors)} factores analizados")
        return result

    def logistic_regression(
        self, df: pd.DataFrame, threshold: float = 3.5
    ) -> dict:
        """
        Regresión logística para predecir bienestar bajo/alto.

        Args:
            df: DataFrame con puntajes
            threshold: Umbral para clasificar bienestar (default: 3.5)

        Returns:
            Resultados de la regresión logística
        """
        if "wellbeing_global" not in df.columns:
            logger.warning("No se encontró columna 'wellbeing_global'")
            return {}

        score_columns = [f"score_{d['id']}" for d in self.dimensions]
        score_columns = [col for col in score_columns if col in df.columns]

        # Crear variable binaria
        y = (df["wellbeing_global"] < threshold).astype(int)
        X = df[score_columns].dropna()
        y = y.loc[X.index]

        if len(X) < 30:
            logger.warning("Muy pocos casos para regresión logística confiable")
            return {}

        # Estandarizar
        scaler = StandardScaler()
        X_scaled = pd.DataFrame(
            scaler.fit_transform(X), columns=score_columns, index=X.index
        )

        # Modelo logístico
        model = LogisticRegression(max_iter=1000, random_state=42)
        model.fit(X_scaled, y)

        # Predicciones
        y_pred = model.predict(X_scaled)
        y_prob = model.predict_proba(X_scaled)[:, 1]

        # Métricas
        accuracy = accuracy_score(y, y_pred)
        auc_roc = roc_auc_score(y, y_prob)
        cm = confusion_matrix(y, y_pred)

        # Odds ratios
        odds_ratios = {}
        dim_names = {f"score_{d['id']}": d["name"] for d in self.dimensions}

        for i, col in enumerate(score_columns):
            factor_name = dim_names.get(col, col)
            odds_ratio = float(np.exp(model.coef_[0][i]))
            odds_ratios[factor_name] = round(odds_ratio, 4)

        # Significancia (usando aproximación simplificada)
        n = len(X)
        p = len(score_columns)
        
        # Calcular p-values usando Chi-cuadrado
        # Wald test: z = coef / se
        # Para logistic regression, usamos la matriz de información de Fisher
        # Simplificación: usar bootstrap o aproximación normal
        z_values = model.coef_[0] / np.sqrt(np.diag(np.cov(X_scaled.T)))
        p_values = 2 * (1 - stats.norm.cdf(np.abs(z_values)))

        # Construir factores
        factors = []
        significant_factors = []

        for i, col in enumerate(score_columns):
            factor_name = dim_names.get(col, col)
            factor = {
                "factor": factor_name,
                "coefficient": round(float(model.coef_[0][i]), 4),
                "odds_ratio": odds_ratios[factor_name],
                "p_value": round(float(p_values[i]), 4),
                "significant": p_values[i] < self.significance_level,
            }
            factors.append(factor)
            if factor["significant"]:
                significant_factors.append(factor)

        result = {
            "accuracy": round(float(accuracy), 4),
            "auc_roc": round(float(auc_roc), 4),
            "confusion_matrix": cm.tolist(),
            "odds_ratios": odds_ratios,
            "factors": factors,
            "significant_factors": significant_factors,
            "threshold": threshold,
            "n_observations": int(n),
        }

        logger.info(f"Regresión logística: Accuracy = {accuracy:.4f}, AUC = {auc_roc:.4f}")
        return result

    def ridge_regression(
        self, df: pd.DataFrame, alpha: float = 1.0
    ) -> dict:
        """
        Regresión Ridge (regularización L2).

        Args:
            df: DataFrame con puntajes
            alpha: Parámetro de regularización

        Returns:
            Resultados de la regresión Ridge
        """
        return self._regularized_regression(df, Ridge(alpha=alpha), "Ridge", alpha)

    def lasso_regression(
        self, df: pd.DataFrame, alpha: float = 1.0
    ) -> dict:
        """
        Regresión Lasso (regularización L1).

        Args:
            df: DataFrame con puntajes
            alpha: Parámetro de regularización

        Returns:
            Resultados de la regresión Lasso
        """
        return self._regularized_regression(df, Lasso(alpha=alpha), "Lasso", alpha)

    def _regularized_regression(
        self, df: pd.DataFrame, model, model_type: str, alpha: float
    ) -> dict:
        """Regresión con regularización (Ridge o Lasso)."""
        if "wellbeing_global" not in df.columns:
            return {}

        score_columns = [f"score_{d['id']}" for d in self.dimensions]
        score_columns = [col for col in score_columns if col in df.columns]

        X = df[score_columns].dropna()
        y = df.loc[X.index, "wellbeing_global"]

        scaler = StandardScaler()
        X_scaled = pd.DataFrame(
            scaler.fit_transform(X), columns=score_columns, index=X.index
        )

        model.fit(X_scaled, y)
        r_squared = model.score(X_scaled, y)
        n = len(X)
        p = len(score_columns)
        adj_r_squared = 1 - (1 - r_squared) * (n - 1) / (n - p - 1)

        # Coeficientes
        dim_names = {f"score_{d['id']}": d["name"] for d in self.dimensions}
        coefficients = {}
        for i, col in enumerate(score_columns):
            factor_name = dim_names.get(col, col)
            coefficients[factor_name] = round(float(model.coef_[i]), 4)

        # MSE
        y_pred = model.predict(X_scaled)
        mse = float(np.mean((y - y_pred) ** 2))

        result = {
            "model_type": model_type,
            "alpha": alpha,
            "r_squared": round(float(r_squared), 4),
            "adj_r_squared": round(float(adj_r_squared), 4),
            "coefficients": coefficients,
            "mse": round(mse, 4),
            "n_observations": int(n),
        }

        logger.info(f"Regresión {model_type}: R² = {r_squared:.4f}, alpha = {alpha}")
        return result

    def polynomial_regression(
        self, df: pd.DataFrame, degree: int = 2
    ) -> dict:
        """
        Regresión polinómica para relaciones no lineales.

        Args:
            df: DataFrame con puntajes
            degree: Grado del polinomio

        Returns:
            Resultados de la regresión polinómica
        """
        if "wellbeing_global" not in df.columns:
            return {}

        # Usar solo las 2 dimensiones más importantes para polinómica
        score_columns = [f"score_{d['id']}" for d in self.dimensions[:2]]
        score_columns = [col for col in score_columns if col in df.columns]

        X = df[score_columns].dropna()
        y = df.loc[X.index, "wellbeing_global"]

        # Crear features polinómicas
        poly = PolynomialFeatures(degree=degree, include_bias=False)
        X_poly = poly.fit_transform(X)
        feature_names = poly.get_feature_names_out(score_columns)

        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X_poly)

        model = LinearRegression()
        model.fit(X_scaled, y)

        r_squared = model.score(X_scaled, y)
        n = len(X)
        p = X_poly.shape[1]
        adj_r_squared = 1 - (1 - r_squared) * (n - 1) / (n - p - 1)

        # Coeficientes
        coefficients = {}
        for i, name in enumerate(feature_names):
            coefficients[name] = round(float(model.coef_[i]), 4)

        result = {
            "degree": degree,
            "r_squared": round(float(r_squared), 4),
            "adj_r_squared": round(float(adj_r_squared), 4),
            "coefficients": coefficients,
            "n_features": int(p),
            "n_observations": int(n),
        }

        logger.info(f"Regresión polinómica (grado {degree}): R² = {r_squared:.4f}")
        return result

    def stepwise_regression(
        self, df: pd.DataFrame, direction: str = "both"
    ) -> dict:
        """
        Regresión stepwise para selección de variables.

        Args:
            df: DataFrame con puntajes
            direction: "forward", "backward", o "both"

        Returns:
            Resultados de la regresión stepwise
        """
        if "wellbeing_global" not in df.columns:
            return {}

        score_columns = [f"score_{d['id']}" for d in self.dimensions]
        score_columns = [col for col in score_columns if col in df.columns]

        X = df[score_columns].dropna()
        y = df.loc[X.index, "wellbeing_global"]

        scaler = StandardScaler()
        X_scaled = pd.DataFrame(
            scaler.fit_transform(X), columns=score_columns, index=X.index
        )

        # Stepwise forward
        selected = []
        remaining = list(score_columns)
        best_r2 = 0
        history = []

        while remaining:
            best_candidate = None
            best_candidate_r2 = best_r2

            for col in remaining:
                candidate = selected + [col]
                model = LinearRegression()
                model.fit(X_scaled[candidate], y)
                r2 = model.score(X_scaled[candidate], y)

                # Adjusted R2
                n = len(y)
                p = len(candidate)
                adj_r2 = 1 - (1 - r2) * (n - 1) / (n - p - 1)

                if adj_r2 > best_candidate_r2:
                    best_candidate = col
                    best_candidate_r2 = adj_r2

            if best_candidate and best_candidate_r2 > best_r2:
                selected.append(best_candidate)
                remaining.remove(best_candidate)
                best_r2 = best_candidate_r2
                history.append({
                    "step": len(selected),
                    "added": best_candidate,
                    "adj_r_squared": round(float(best_r2), 4),
                })
            else:
                break

        # Modelo final
        if selected:
            model = LinearRegression()
            model.fit(X_scaled[selected], y)
            final_r2 = model.score(X_scaled[selected], y)
            n = len(y)
            p = len(selected)
            final_adj_r2 = 1 - (1 - final_r2) * (n - 1) / (n - p - 1)

            dim_names = {f"score_{d['id']}": d["name"] for d in self.dimensions}
            coefficients = {}
            for i, col in enumerate(selected):
                factor_name = dim_names.get(col, col)
                coefficients[factor_name] = round(float(model.coef_[i]), 4)
        else:
            final_r2 = 0
            final_adj_r2 = 0
            coefficients = {}

        result = {
            "direction": direction,
            "selected_variables": selected,
            "n_selected": len(selected),
            "r_squared": round(float(final_r2), 4),
            "adj_r_squared": round(float(final_adj_r2), 4),
            "coefficients": coefficients,
            "step_history": history,
            "n_observations": int(len(y)),
        }

        logger.info(f"Stepwise ({direction}): {len(selected)} variables seleccionadas, R² = {final_r2:.4f}")
        return result

    def anova_comparison(
        self, df: pd.DataFrame, group_var: str
    ) -> dict:
        """
        ANOVA para comparar grupos.

        Args:
            df: DataFrame con puntajes
            group_var: Variable de agrupación

        Returns:
            Resultados del ANOVA
        """
        if group_var not in df.columns:
            return {"error": f"Variable '{group_var}' no encontrada"}

        results = {
            "group_variable": group_var,
            "dimensions": [],
            "overall_f": None,
            "overall_p": None,
        }

        dim_names = {d["id"]: d["name"] for d in self.dimensions}
        all_f_stats = []
        all_p_values = []

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

            all_f_stats.append(f_stat)
            all_p_values.append(p_value)

            # Medias por grupo
            group_means = {str(g): round(float(data.mean()), 3) for g, data in group_data}
            group_sizes = {str(g): int(len(data)) for g, data in group_data}

            # Tamaño del efecto (Eta²)
            ss_between = sum(len(g) * (g.mean() - df[col].mean()) ** 2 for _, g in group_data)
            ss_total = sum((df[col] - df[col].mean()) ** 2)
            eta_squared = ss_between / ss_total if ss_total > 0 else 0

            results["dimensions"].append({
                "dimension": dim_names.get(dimension["id"], dimension["id"]),
                "f_statistic": round(float(f_stat), 4),
                "p_value": round(float(p_value), 4),
                "significant": p_value < self.significance_level,
                "eta_squared": round(float(eta_squared), 4),
                "group_means": group_means,
                "group_sizes": group_sizes,
            })

        # ANOVA global (promedio de F-stats)
        if all_f_stats:
            results["overall_f"] = round(float(np.mean(all_f_stats)), 4)
            results["overall_p"] = round(float(np.mean(all_p_values)), 4)

        # Ordenar por significancia
        results["dimensions"].sort(key=lambda x: x["p_value"])

        logger.info(f"ANOVA por {group_var}: {len(results['dimensions'])} dimensiones analizadas")
        return results

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
