"""
Módulo de dashboard interactivo con Streamlit.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from src.utils.logger import get_logger

logger = get_logger(__name__)


class HappinessDashboard:
    """Dashboard interactivo para análisis de bienestar estudiantil."""

    def __init__(self, config: dict):
        """
        Inicializa el dashboard.

        Args:
            config: Configuración del proyecto
        """
        self.config = config
        self.dimensions = config.get("survey", {}).get("dimensions", [])
        self.scale_range = config.get("survey", {}).get("scale_range", [1, 6])

    def render_header(self):
        """Renderiza el encabezado del dashboard."""
        st.set_page_config(
            page_title="Bienestar Estudiantil UST",
            page_icon="📊",
            layout="wide",
        )

        st.title("📊 Análisis de Bienestar Psicológico Estudiantil")
        st.markdown("**Universidad Santo Tomás** - Escala de Ryff")

    def render_overview(self, df: pd.DataFrame):
        """Renderiza la vista general de datos."""
        st.header("📋 Vista General")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total Respuestas", len(df))

        with col2:
            if "wellbeing_global" in df.columns:
                avg = df["wellbeing_global"].mean()
                st.metric("Bienestar Promedio", f"{avg:.2f}")
            else:
                st.metric("Bienestar Promedio", "N/A")

        with col3:
            if "wellbeing_global" in df.columns:
                std = df["wellbeing_global"].std()
                st.metric("Desviación Estándar", f"{std:.2f}")
            else:
                st.metric("Desviación Estándar", "N/A")

        with col4:
            if "wellbeing_global" in df.columns:
                min_val = df["wellbeing_global"].min()
                max_val = df["wellbeing_global"].max()
                st.metric("Rango", f"{min_val:.2f} - {max_val:.2f}")
            else:
                st.metric("Rango", "N/A")

    def render_dimension_distribution(self, df: pd.DataFrame):
        """Renderiza distribución por dimensiones."""
        st.header("📈 Distribución por Dimensiones")

        score_columns = [f"score_{d['id']}" for d in self.dimensions]
        score_columns = [col for col in score_columns if col in df.columns]

        if not score_columns:
            st.warning("No hay datos de dimensiones disponibles")
            return

        # Box plot
        fig = go.Figure()

        for col in score_columns:
            dim_name = col.replace("score_", "")
            fig.add_trace(
                go.Box(
                    y=df[col],
                    name=dim_name,
                    boxmean=True,
                )
            )

        fig.update_layout(
            title="Distribución de Puntajes por Dimensión",
            yaxis_title="Puntaje",
            xaxis_title="Dimensión",
            height=500,
        )

        st.plotly_chart(fig, use_container_width=True)

        # Tabla resumen
        st.subheader("Estadísticas Descriptivas")

        desc_stats = []
        dim_names = {d["id"]: d["name"] for d in self.dimensions}

        for col in score_columns:
            dim_id = col.replace("score_", "")
            desc_stats.append({
                "Dimensión": dim_names.get(dim_id, dim_id),
                "Media": f"{df[col].mean():.3f}",
                "DE": f"{df[col].std():.3f}",
                "Mín": f"{df[col].min():.2f}",
                "Máx": f"{df[col].max():.2f}",
                "Mediana": f"{df[col].median():.3f}",
            })

        st.dataframe(pd.DataFrame(desc_stats), use_container_width=True)

    def render_global_distribution(self, df: pd.DataFrame):
        """Renderiza distribución del bienestar global."""
        st.header("🎯 Distribución del Bienestar Global")

        if "wellbeing_global" not in df.columns:
            st.warning("No hay datos de bienestar global disponibles")
            return

        col1, col2 = st.columns(2)

        with col1:
            # Histograma
            fig = px.histogram(
                df,
                x="wellbeing_global",
                nbins=30,
                title="Distribución del Índice de Bienestar",
                labels={"wellbeing_global": "Índice de Bienestar"},
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Gauge chart
            avg_wellbeing = df["wellbeing_global"].mean()
            max_score = self.scale_range[1]

            fig = go.Figure(
                go.Indicator(
                    mode="gauge+number",
                    value=avg_wellbeing,
                    title={"text": "Bienestar Promedio"},
                    gauge={
                        "axis": {"range": [self.scale_range[0], max_score]},
                        "bar": {"color": "darkblue"},
                        "steps": [
                            {"range": [self.scale_range[0], max_score * 0.4], "color": "lightcoral"},
                            {"range": [max_score * 0.4, max_score * 0.7], "color": "lightyellow"},
                            {"range": [max_score * 0.7, max_score], "color": "lightgreen"},
                        ],
                    },
                )
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)

    def render_correlation_heatmap(self, corr_matrix: pd.DataFrame):
        """Renderiza mapa de calor de correlaciones."""
        st.header("🔗 Correlaciones entre Dimensiones")

        if corr_matrix.empty:
            st.warning("No hay datos de correlaciones disponibles")
            return

        fig = px.imshow(
            corr_matrix,
            text_auto=".2f",
            color_continuous_scale="RdBu_r",
            zmin=-1,
            zmax=1,
            title="Matriz de Correlaciones",
        )

        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)

    def render_group_comparison(self, df: pd.DataFrame, group_var: str):
        """Renderiza comparación entre grupos."""
        st.header(f"👥 Comparación por {group_var.title()}")

        if group_var not in df.columns:
            st.warning(f"Variable '{group_var}' no disponible en los datos")
            return

        score_columns = [f"score_{d['id']}" for d in self.dimensions]
        score_columns = [col for col in score_columns if col in df.columns]

        if not score_columns:
            st.warning("No hay datos de dimensiones disponibles")
            return

        # Gráfico de barras agrupadas
        fig = go.Figure()

        dim_names = {d["id"]: d["name"] for d in self.dimensions}

        for col in score_columns:
            dim_id = col.replace("score_", "")
            dim_name = dim_names.get(dim_id, dim_id)

            group_means = df.groupby(group_var)[col].mean()
            fig.add_trace(
                go.Bar(
                    name=dim_name,
                    x=group_means.index,
                    y=group_means.values,
                )
            )

        fig.update_layout(
            title=f"Puntaje Promedio por Dimensión y {group_var.title()}",
            barmode="group",
            height=500,
        )

        st.plotly_chart(fig, use_container_width=True)

    def render_clustering_results(self, df: pd.DataFrame, profiles: list):
        """Renderiza resultados de clustering."""
        st.header("🎯 Perfiles de Estudiantes")

        if not profiles:
            st.warning("No hay resultados de clustering disponibles")
            return

        # Tabs para diferentes vistas
        tab1, tab2 = st.tabs(["Resumen", "Detalles"])

        with tab1:
            # Distribución de clusters
            cluster_data = []
            for p in profiles:
                cluster_data.append({
                    "Cluster": f"Perfil {p.cluster_id}",
                    "Cantidad": p.size,
                    "Porcentaje": f"{p.percentage}%",
                    "Etiqueta": p.label,
                })

            st.dataframe(pd.DataFrame(cluster_data), use_container_width=True)

            # Gráfico circular
            fig = px.pie(
                pd.DataFrame(cluster_data),
                values="Cantidad",
                names="Cluster",
                title="Distribución de Perfiles",
            )
            st.plotly_chart(fig, use_container_width=True)

        with tab2:
            # Centroides
            st.subheader("Centroides por Cluster")

            for profile in profiles:
                st.markdown(f"**Perfil {profile.cluster_id}: {profile.label}**")
                centroid_df = pd.DataFrame(
                    [profile.centroid], index=["Promedio"]
                ).T
                st.dataframe(centroid_df, use_container_width=True)

    def render_reports_section(self):
        """Renderiza sección de reportes."""
        st.header("📄 Generación de Reportes")

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Reporte PDF Ejecutivo")
            st.markdown(
                "Genera un documento PDF con el resumen ejecutivo del análisis."
            )
            if st.button("📊 Generar PDF"):
                st.info("Generando reporte PDF...")
                # La generación se hace desde el orquestador

        with col2:
            st.subheader("Exportar Datos")
            st.markdown("Exporta los datos procesados en diferentes formatos.")

            if st.button("📥 Exportar CSV"):
                st.info("Preparando exportación...")

    def run(self, df: pd.DataFrame, corr_matrix: pd.DataFrame = None, profiles: list = None):
        """
        Ejecuta el dashboard completo.

        Args:
            df: DataFrame con datos procesados
            corr_matrix: Matriz de correlaciones
            profiles: Perfiles de clustering
        """
        self.render_header()
        self.render_overview(df)

        st.divider()

        self.render_dimension_distribution(df)
        self.render_global_distribution(df)

        st.divider()

        if corr_matrix is not None and not corr_matrix.empty:
            self.render_correlation_heatmap(corr_matrix)

        st.divider()

        # Comparaciones por grupos
        grouping_vars = self.config.get("grouping_variables", [])
        available_groups = [g for g in grouping_vars if g in df.columns]

        if available_groups:
            selected_group = st.selectbox(
                "Seleccionar variable para comparación:",
                available_groups,
            )
            if selected_group:
                self.render_group_comparison(df, selected_group)

        st.divider()

        if profiles:
            self.render_clustering_results(df, profiles)

        self.render_reports_section()
