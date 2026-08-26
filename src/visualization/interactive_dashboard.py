"""
Dashboard interactivo con Plotly.
Genera visualizaciones interactivas de alta calidad.
"""

import os
from datetime import datetime
from typing import Optional

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

from src.utils.logger import get_logger

logger = get_logger(__name__)


class InteractiveDashboard:
    """Dashboard interactivo con Plotly."""

    def __init__(self, config: dict):
        """
        Inicializa el dashboard.

        Args:
            config: Configuración del proyecto
        """
        self.config = config
        self.dimensions = config.get("survey", {}).get("dimensions", [])
        self.colors = {
            "primary": "#003366",
            "secondary": "#4A90D9",
            "success": "#27AE60",
            "warning": "#F39C12",
            "danger": "#E74C3C",
            "info": "#3498DB",
        }

    def generate_full_dashboard(
        self,
        results: dict,
        df: pd.DataFrame = None,
        output_path: Optional[str] = None,
    ) -> str:
        """
        Genera un dashboard completo interactivo.

        Args:
            results: Resultados del análisis
            df: DataFrame original (opcional)
            output_path: Ruta de salida

        Returns:
            Ruta del HTML generado
        """
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = os.path.join(
                self.config.get("paths", {}).get("reports", "reports"),
                f"dashboard_interactivo_{timestamp}.html"
            )

        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Crear HTML con Plotly
        html_content = self._build_dashboard_html(results, df)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        logger.info(f"Dashboard interactivo generado: {output_path}")
        return output_path

    def _build_dashboard_html(self, results: dict, df: pd.DataFrame = None) -> str:
        """Construye el HTML del dashboard."""
        # Crear figuras
        fig_descriptive = self._create_descriptive_chart(results)
        fig_radar = self._create_radar_chart(results)
        fig_correlation = self._create_correlation_heatmap(results)
        fig_clusters = self._create_cluster_chart(results)
        fig_regression = self._create_regression_chart(results)
        fig_distribution = self._create_distribution_chart(results)

        # Convertir figuras a HTML
        fig_descriptive_html = fig_descriptive.to_html(full_html=False, include_plotlyjs=False)
        fig_radar_html = fig_radar.to_html(full_html=False, include_plotlyjs=False)
        fig_correlation_html = fig_correlation.to_html(full_html=False, include_plotlyjs=False)
        fig_clusters_html = fig_clusters.to_html(full_html=False, include_plotlyjs=False)
        fig_regression_html = fig_regression.to_html(full_html=False, include_plotlyjs=False)
        fig_distribution_html = fig_distribution.to_html(full_html=False, include_plotlyjs=False)

        # Metadata
        total = results.get("total_responses", 0)
        global_mean = results.get("global_mean", 0)

        html = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard de Bienestar Psicológico - UST</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}
        .header {{
            background: white;
            border-radius: 15px;
            padding: 30px;
            margin-bottom: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            text-align: center;
        }}
        .header h1 {{
            color: #003366;
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        .header .subtitle {{
            color: #666;
            font-size: 1.2em;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }}
        .stat-card {{
            background: white;
            border-radius: 15px;
            padding: 25px;
            text-align: center;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            transition: transform 0.3s;
        }}
        .stat-card:hover {{
            transform: translateY(-5px);
        }}
        .stat-card .value {{
            font-size: 2.5em;
            font-weight: bold;
            color: #003366;
        }}
        .stat-card .label {{
            color: #666;
            font-size: 0.9em;
            margin-top: 5px;
        }}
        .chart-grid {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 20px;
            margin-bottom: 20px;
        }}
        .chart-card {{
            background: white;
            border-radius: 15px;
            padding: 20px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }}
        .chart-card.full-width {{
            grid-column: span 2;
        }}
        .chart-card h3 {{
            color: #003366;
            margin-bottom: 15px;
            font-size: 1.3em;
            border-bottom: 2px solid #4A90D9;
            padding-bottom: 10px;
        }}
        .footer {{
            text-align: center;
            color: white;
            padding: 20px;
            margin-top: 20px;
        }}
        @media (max-width: 768px) {{
            .chart-grid {{
                grid-template-columns: 1fr;
            }}
            .chart-card.full-width {{
                grid-column: span 1;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Dashboard de Bienestar Psicológico</h1>
            <p class="subtitle">Universidad Santo Tomás - Análisis Interactivo</p>
        </div>

        <div class="stats-grid">
            <div class="stat-card">
                <div class="value">{total}</div>
                <div class="label">Participantes</div>
            </div>
            <div class="stat-card">
                <div class="value">{global_mean:.2f}</div>
                <div class="label">Bienestar Global</div>
            </div>
            <div class="stat-card">
                <div class="value">6</div>
                <div class="label">Dimensiones</div>
            </div>
            <div class="stat-card">
                <div class="value">29</div>
                <div class="label">Ítems</div>
            </div>
        </div>

        <div class="chart-grid">
            <div class="chart-card">
                <h3>Estadísticas Descriptivas</h3>
                {fig_descriptive_html}
            </div>
            <div class="chart-card">
                <h3>Perfil de Bienestar (Radar)</h3>
                {fig_radar_html}
            </div>
            <div class="chart-card">
                <h3>Distribución de Puntuaciones</h3>
                {fig_distribution_html}
            </div>
            <div class="chart-card">
                <h3>Análisis de Regresión</h3>
                {fig_regression_html}
            </div>
            <div class="chart-card full-width">
                <h3>Matriz de Correlaciones</h3>
                {fig_correlation_html}
            </div>
            <div class="chart-card full-width">
                <h3>Perfiles de Estudiantes (Clustering)</h3>
                {fig_clusters_html}
            </div>
        </div>

        <div class="footer">
            <p>Dashboard generado automáticamente el {datetime.now().strftime("%d/%m/%Y %H:%M")}</p>
            <p>Sistema de Análisis de Bienestar Psicológico Estudiantil</p>
        </div>
    </div>
</body>
</html>
"""
        return html

    def _create_descriptive_chart(self, results: dict) -> go.Figure:
        """Crea gráfico de barras descriptivo."""
        dimensions = results.get("dimension_stats", [])

        if not dimensions:
            return go.Figure()

        names = [d.get("dimension", "")[:10] for d in dimensions]
        means = [d.get("mean", 0) for d in dimensions]
        stds = [d.get("std", 0) for d in dimensions]

        fig = go.Figure()

        fig.add_trace(go.Bar(
            x=names,
            y=means,
            error_y=dict(type='data', array=stds),
            marker_color=self.colors["primary"],
            text=[f"{m:.2f}" for m in means],
            textposition='auto',
        ))

        fig.update_layout(
            yaxis_title="Puntuación Promedio",
            yaxis_range=[0, 6],
            showlegend=False,
            height=400,
        )

        return fig

    def _create_radar_chart(self, results: dict) -> go.Figure:
        """Crea gráfico radar."""
        dimensions = results.get("dimension_stats", [])

        if not dimensions:
            return go.Figure()

        names = [d.get("dimension", "") for d in dimensions]
        means = [d.get("mean", 0) for d in dimensions]

        # Cerrar el radar
        names.append(names[0])
        means.append(means[0])

        fig = go.Figure()

        fig.add_trace(go.Scatterpolar(
            r=means,
            theta=names,
            fill='toself',
            name='Bienestar',
            line_color=self.colors["primary"],
            fillcolor=self.colors["secondary"],
        ))

        fig.update_layout(
            polar=dict(
                radialaxis=dict(range=[0, 6]),
            ),
            height=400,
            showlegend=False,
        )

        return fig

    def _create_correlation_heatmap(self, results: dict) -> go.Figure:
        """Crea heatmap de correlaciones."""
        correlations = results.get("correlations", [])

        if not correlations:
            return go.Figure()

        # Construir matriz
        dim_names = list(set(
            [c.get("var1", "") for c in correlations] +
            [c.get("var2", "") for c in correlations]
        ))

        n = len(dim_names)
        matrix = np.zeros((n, n))

        for c in correlations:
            i = dim_names.index(c.get("var1", ""))
            j = dim_names.index(c.get("var2", ""))
            r = c.get("correlation", 0)
            matrix[i, j] = r
            matrix[j, i] = r

        np.fill_diagonal(matrix, 1)

        fig = go.Figure(data=go.Heatmap(
            z=matrix,
            x=dim_names,
            y=dim_names,
            colorscale='RdBu_r',
            zmin=-1,
            zmax=1,
            text=np.round(matrix, 2),
            texttemplate='%{text}',
            textfont=dict(size=10),
        ))

        fig.update_layout(
            height=400,
            yaxis=dict(autorange="reversed"),
        )

        return fig

    def _create_cluster_chart(self, results: dict) -> go.Figure:
        """Crea gráfico de clusters."""
        clusters = results.get("clusters", [])

        if not clusters:
            return go.Figure()

        labels = [f"Cluster {c.get('id', 0)}" for c in clusters]
        sizes = [c.get("size", 0) for c in clusters]
        percentages = [c.get("percentage", 0) for c in clusters]

        colors = [self.colors["primary"], self.colors["secondary"],
                  self.colors["success"], self.colors["warning"],
                  self.colors["danger"], self.colors["info"]]

        fig = go.Figure(data=[go.Pie(
            labels=labels,
            values=sizes,
            hole=0.3,
            marker=dict(colors=colors[:len(clusters)]),
            textinfo='label+percent',
            textposition='inside',
        )])

        fig.update_layout(
            height=400,
            showlegend=True,
        )

        return fig

    def _create_regression_chart(self, results: dict) -> go.Figure:
        """Crea gráfico de regresión."""
        regression = results.get("regression", {})

        if not regression:
            return go.Figure()

        factors = regression.get("factors", [])
        if not factors:
            return go.Figure()

        names = [f.get("factor", "")[:15] for f in factors]
        coefficients = [f.get("std_coefficient", 0) for f in factors]
        significant = [f.get("significant", False) for f in factors]

        colors = [self.colors["success"] if s else self.colors["danger"]
                  for s in significant]

        fig = go.Figure()

        fig.add_trace(go.Bar(
            x=names,
            y=coefficients,
            marker_color=colors,
            text=[f"{c:.3f}" for c in coefficients],
            textposition='auto',
        ))

        fig.update_layout(
            yaxis_title="Coeficiente Estandarizado",
            showlegend=False,
            height=400,
        )

        return fig

    def _create_distribution_chart(self, results: dict) -> go.Figure:
        """Crea gráfico de distribución."""
        dimensions = results.get("dimension_stats", [])

        if not dimensions:
            return go.Figure()

        fig = go.Figure()

        for dim in dimensions:
            mean = dim.get("mean", 0)
            std = dim.get("std", 0)
            name = dim.get("dimension", "")

            # Generar datos simulados
            x = np.linspace(1, 6, 100)
            y = (1 / (std * np.sqrt(2 * np.pi))) * np.exp(-0.5 * ((x - mean) / std) ** 2)

            fig.add_trace(go.Scatter(
                x=x,
                y=y,
                mode='lines',
                name=name[:15],
            ))

        fig.update_layout(
            xaxis_title="Puntuación",
            yaxis_title="Densidad",
            height=400,
        )

        return fig
