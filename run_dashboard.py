"""
Script para ejecutar el dashboard con datos procesados.
"""

import pandas as pd
import yaml
import glob
import sys
import os

# Agregar directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.data.processor import DataProcessor
from src.analysis.statistics import StatisticalAnalysis
from src.analysis.correlations import CorrelationAnalysis
from src.analysis.clustering import ClusteringAnalysis
from src.utils.logger import get_logger

logger = get_logger(__name__)


def load_and_process_data():
    """Carga y procesa los datos para el dashboard."""
    # Cargar configuración
    with open("configs/config.yaml", "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    # Encontrar archivo CSV
    csv_files = glob.glob("data/raw/*.csv")
    if not csv_files:
        logger.error("No se encontraron archivos CSV en data/raw/")
        return None, None, None, None

    # Cargar datos
    logger.info(f"Cargando datos desde: {csv_files[0]}")
    df_raw = pd.read_csv(csv_files[0], encoding="utf-8-sig")

    # Procesar datos
    processor = DataProcessor(config)
    df_processed, report = processor.prepare_analysis_data(df_raw)

    # Correlaciones
    corr_analysis = CorrelationAnalysis(config)
    corr_matrix = corr_analysis.calculate_correlation_matrix(df_processed)

    # Clustering
    cluster_analysis = ClusteringAnalysis(config)
    df_clustered = cluster_analysis.fit_clusters(df_processed)
    profiles = cluster_analysis.get_cluster_profiles(df_clustered)

    return df_clustered, corr_matrix, profiles, config


if __name__ == "__main__":
    import streamlit as st

    st.set_page_config(
        page_title="Bienestar Estudiantil UST",
        page_icon="📊",
        layout="wide",
    )

    # Cargar datos
    df, corr_matrix, profiles, config = load_and_process_data()

    if df is not None:
        # Importar y ejecutar dashboard
        from src.visualization.dashboard import HappinessDashboard

        dashboard = HappinessDashboard(config)
        dashboard.run(df, corr_matrix, profiles)
    else:
        st.error("No se pudieron cargar los datos. Verifica que exista un archivo CSV en data/raw/")
