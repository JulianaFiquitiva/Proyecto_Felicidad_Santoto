"""
Módulo de análisis de series de tiempo para bienestar psicológico.
Analiza la evolución del bienestar a lo largo del tiempo.
"""

from typing import Optional
from dataclasses import dataclass

import pandas as pd
import numpy as np
from scipy import stats
from datetime import datetime, timedelta

from src.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class TimeSeriesResult:
    """Resultado de análisis de series de tiempo."""
    trend: str  # "improving", "declining", "stable"
    slope: float
    r_squared: float
    forecast: list
    seasonality: Optional[dict]
    changepoints: list


class TimeSeriesAnalyzer:
    """Analizador de series de tiempo para bienestar."""

    def __init__(self, config: dict):
        """
        Inicializa el analizador.

        Args:
            config: Configuración del proyecto
        """
        self.config = config

    def analyze_trend(
        self,
        df: pd.DataFrame,
        date_column: str = None,
        value_column: str = "wellbeing_global",
    ) -> dict:
        """
        Analiza la tendencia temporal del bienestar.

        Args:
            df: DataFrame con datos
            date_column: Columna con fechas
            value_column: Columna con valores a analizar

        Returns:
            Resultados del análisis de tendencia
        """
        # Detectar columna de fecha
        if date_column is None:
            date_column = self._detect_date_column(df)

        if date_column is None or date_column not in df.columns:
            logger.warning("No se encontró columna de fecha")
            return self._simple_trend(df, value_column)

        # Preparar datos temporales
        df_time = df[[date_column, value_column]].dropna()
        df_time[date_column] = pd.to_datetime(df_time[date_column])
        df_time = df_time.sort_values(date_column)

        if len(df_time) < 3:
            return self._simple_trend(df, value_column)

        # Calcular tendencia
        x = np.arange(len(df_time))
        y = df_time[value_column].values

        # Regresión lineal
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)

        # Determinar tendencia
        if p_value < 0.05:
            if slope > 0.01:
                trend = "improving"
            elif slope < -0.01:
                trend = "declining"
            else:
                trend = "stable"
        else:
            trend = "stable"

        # Detectar puntos de cambio
        changepoints = self._detect_changepoints(y)

        # Pronóstico simple (próximos 5 períodos)
        forecast = []
        last_x = len(df_time) - 1
        for i in range(1, 6):
            pred_x = last_x + i
            pred_y = slope * pred_x + intercept
            # Limitar al rango válido (1-6)
            pred_y = max(1, min(6, pred_y))
            forecast.append({
                "period": i,
                "predicted_value": round(float(pred_y), 3),
            })

        result = {
            "trend": trend,
            "slope": round(float(slope), 6),
            "r_squared": round(float(r_value ** 2), 4),
            "p_value": round(float(p_value), 4),
            "n_periods": len(df_time),
            "date_range": {
                "start": df_time[date_column].min().isoformat(),
                "end": df_time[date_column].max().isoformat(),
            },
            "forecast": forecast,
            "changepoints": changepoints,
        }

        logger.info(f"Tendencia: {trend}, pendiente: {slope:.4f}")
        return result

    def analyze_by_period(
        self,
        df: pd.DataFrame,
        date_column: str = None,
        value_column: str = "wellbeing_global",
        period: str = "monthly",
    ) -> dict:
        """
        Analiza el bienestar por período.

        Args:
            df: DataFrame con datos
            date_column: Columna con fechas
            value_column: Columna con valores
            period: "daily", "weekly", "monthly", "quarterly"

        Returns:
            Estadísticas por período
        """
        if date_column is None:
            date_column = self._detect_date_column(df)

        if date_column is None or date_column not in df.columns:
            return {"error": "No se encontró columna de fecha"}

        df_time = df[[date_column, value_column]].dropna()
        df_time[date_column] = pd.to_datetime(df_time[date_column])

        # Agrupar por período
        if period == "daily":
            df_time["period"] = df_time[date_column].dt.date
        elif period == "weekly":
            df_time["period"] = df_time[date_column].dt.isocalendar().week
        elif period == "monthly":
            df_time["period"] = df_time[date_column].dt.to_period("M")
        elif period == "quarterly":
            df_time["period"] = df_time[date_column].dt.to_period("Q")

        grouped = df_time.groupby("period")[value_column].agg(["mean", "std", "count"])

        result = {
            "period": period,
            "n_periods": len(grouped),
            "statistics": {
                "overall_mean": round(float(df_time[value_column].mean()), 3),
                "overall_std": round(float(df_time[value_column].std()), 3),
                "period_means": grouped["mean"].to_dict(),
                "period_stds": grouped["std"].to_dict(),
                "period_counts": grouped["count"].to_dict(),
            },
        }

        return result

    def detect_anomalies(
        self,
        df: pd.DataFrame,
        value_column: str = "wellbeing_global",
        threshold: float = 2.0,
    ) -> dict:
        """
        Detecta anomalías en los datos.

        Args:
            df: DataFrame con datos
            value_column: Columna a analizar
            threshold: Umbral de desviación estándar

        Returns:
            Anomalías detectadas
        """
        if value_column not in df.columns:
            return {"error": f"Columna {value_column} no encontrada"}

        values = df[value_column].dropna()

        # Calcular estadísticas
        mean = values.mean()
        std = values.std()

        # Detectar outliers
        lower_bound = mean - threshold * std
        upper_bound = mean + threshold * std

        anomalies = df[
            (df[value_column] < lower_bound) | (df[value_column] > upper_bound)
        ]

        result = {
            "mean": round(float(mean), 3),
            "std": round(float(std), 3),
            "threshold": threshold,
            "bounds": {
                "lower": round(float(lower_bound), 3),
                "upper": round(float(upper_bound), 3),
            },
            "n_anomalies": len(anomalies),
            "anomaly_percentage": round(len(anomalies) / len(df) * 100, 2),
        }

        logger.info(f"Anomalías detectadas: {len(anomalies)} ({result['anomaly_percentage']}%)")
        return result

    def compare_periods(
        self,
        df: pd.DataFrame,
        date_column: str = None,
        value_column: str = "wellbeing_global",
        period1_start: str = None,
        period1_end: str = None,
        period2_start: str = None,
        period2_end: str = None,
    ) -> dict:
        """
        Compara el bienestar entre dos períodos.

        Args:
            df: DataFrame con datos
            date_column: Columna con fechas
            value_column: Columna con valores
            period1_start/end: Período 1
            period2_start/end: Período 2

        Returns:
            Comparación entre períodos
        """
        if date_column is None:
            date_column = self._detect_date_column(df)

        if date_column is None:
            return {"error": "No se encontró columna de fecha"}

        df[date_column] = pd.to_datetime(df[date_column])

        # Filtrar períodos
        if period1_start and period1_end:
            mask1 = (df[date_column] >= period1_start) & (df[date_column] <= period1_end)
            period1_data = df.loc[mask1, value_column].dropna()
        else:
            # Usar primera mitad
            mid = len(df) // 2
            period1_data = df.iloc[:mid][value_column].dropna()

        if period2_start and period2_end:
            mask2 = (df[date_column] >= period2_start) & (df[date_column] <= period2_end)
            period2_data = df.loc[mask2, value_column].dropna()
        else:
            # Usar segunda mitad
            mid = len(df) // 2
            period2_data = df.iloc[mid:][value_column].dropna()

        if len(period1_data) < 2 or len(period2_data) < 2:
            return {"error": "Datos insuficientes para comparación"}

        # Test t de muestras independientes
        t_stat, p_value = stats.ttest_ind(period1_data, period2_data)

        # Tamaño del efecto (d de Cohen)
        pooled_std = np.sqrt(
            ((len(period1_data) - 1) * period1_data.std() ** 2 +
             (len(period2_data) - 1) * period2_data.std() ** 2) /
            (len(period1_data) + len(period2_data) - 2)
        )
        cohens_d = (period2_data.mean() - period1_data.mean()) / pooled_std if pooled_std > 0 else 0

        result = {
            "period1": {
                "n": len(period1_data),
                "mean": round(float(period1_data.mean()), 3),
                "std": round(float(period1_data.std()), 3),
            },
            "period2": {
                "n": len(period2_data),
                "mean": round(float(period2_data.mean()), 3),
                "std": round(float(period2_data.std()), 3),
            },
            "comparison": {
                "mean_difference": round(float(period2_data.mean() - period1_data.mean()), 3),
                "t_statistic": round(float(t_stat), 4),
                "p_value": round(float(p_value), 4),
                "cohens_d": round(float(cohens_d), 4),
                "significant": p_value < 0.05,
                "effect_size": self._interpret_cohens_d(cohens_d),
            },
        }

        return result

    def _detect_date_column(self, df: pd.DataFrame) -> Optional[str]:
        """Detecta la columna de fecha automáticamente."""
        date_keywords = ["fecha", "date", "hora", "time", "timestamp", "inicio"]

        for col in df.columns:
            col_lower = col.lower()
            if any(keyword in col_lower for keyword in date_keywords):
                return col

        # Intentar convertir columnas a datetime
        for col in df.columns:
            try:
                pd.to_datetime(df[col].head())
                return col
            except:
                continue

        return None

    def _simple_trend(self, df: pd.DataFrame, value_column: str) -> dict:
        """Análisis de tendencia simple sin fecha."""
        if value_column not in df.columns:
            return {"trend": "unknown"}

        values = df[value_column].dropna()

        return {
            "trend": "stable",
            "mean": round(float(values.mean()), 3),
            "std": round(float(values.std()), 3),
            "min": round(float(values.min()), 3),
            "max": round(float(values.max()), 3),
        }

    def _detect_changepoints(self, values: np.ndarray) -> list:
        """Detecta puntos de cambio en la serie."""
        changepoints = []

        if len(values) < 5:
            return changepoints

        # Usar cambio en pendiente
        for i in range(2, len(values) - 2):
            before = np.mean(values[max(0, i-2):i])
            after = np.mean(values[i:min(len(values), i+2)])

            change = after - before
            if abs(change) > 0.5:  # Umbral de cambio significativo
                changepoints.append({
                    "index": int(i),
                    "change": round(float(change), 3),
                    "direction": "increase" if change > 0 else "decrease",
                })

        return changepoints

    def _interpret_cohens_d(self, d: float) -> str:
        """Interpreta el tamaño del efecto."""
        d = abs(d)
        if d < 0.2:
            return "negligible"
        elif d < 0.5:
            return "pequeño"
        elif d < 0.8:
            return "mediano"
        else:
            return "grande"
