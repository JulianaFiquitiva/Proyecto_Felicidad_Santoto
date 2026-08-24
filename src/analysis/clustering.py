"""
Módulo de clustering para perfiles de estudiantes.
"""

from typing import Optional
from dataclasses import dataclass

import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score
from sklearn.decomposition import PCA

from src.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class ClusterProfile:
    """Perfil de cluster."""

    cluster_id: int
    size: int
    percentage: float
    centroid: dict
    label: str


class ClusteringAnalysis:
    """Análisis de clustering para identificar perfiles de estudiantes."""

    def __init__(self, config: dict):
        """
        Inicializa el análisis.

        Args:
            config: Configuración del proyecto
        """
        self.analysis_config = config.get("analysis", {})
        clustering_config = self.analysis_config.get("clustering", {})
        self.method = clustering_config.get("method", "kmeans")
        self.max_clusters = clustering_config.get("max_clusters", 8)
        self.random_state = clustering_config.get("random_state", 42)
        self.dimensions = config.get("survey", {}).get("dimensions", [])

        self.scaler = StandardScaler()
        self.model = None
        self.n_clusters = None

    def find_optimal_clusters(self, df: pd.DataFrame) -> dict:
        """
        Encuentra el número óptimo de clusters usando el método del codo
        y el coeficiente de silueta.

        Args:
            df: DataFrame con puntajes por dimensión

        Returns:
            Resultados del análisis
        """
        X = self._prepare_features(df)

        if len(X) < self.max_clusters:
            self.max_clusters = len(X) - 1

        inertias = []
        silhouette_scores = []
        K_range = range(2, self.max_clusters + 1)

        for k in K_range:
            kmeans = KMeans(n_clusters=k, random_state=self.random_state, n_init=10)
            labels = kmeans.fit_predict(X)
            inertias.append(kmeans.inertia_)
            silhouette_scores.append(silhouette_score(X, labels))

        # Encontrar k óptimo por silueta máxima
        optimal_k = list(K_range)[np.argmax(silhouette_scores)]

        result = {
            "k_range": list(K_range),
            "inertias": [round(float(i), 2) for i in inertias],
            "silhouette_scores": [round(float(s), 4) for s in silhouette_scores],
            "optimal_k": int(optimal_k),
            "best_silhouette": round(float(max(silhouette_scores)), 4),
        }

        logger.info(f"Óptimo de clusters: k={optimal_k} (silueta={max(silhouette_scores):.4f})")
        return result

    def fit_clusters(self, df: pd.DataFrame, n_clusters: Optional[int] = None) -> pd.DataFrame:
        """
        Ajusta el modelo de clustering.

        Args:
            df: DataFrame con puntajes por dimensión
            n_clusters: Número de clusters (None = automático)

        Returns:
            DataFrame con etiquetas de cluster
        """
        # Preparar features y obtener índices válidos
        score_columns = [f"score_{d['id']}" for d in self.dimensions]
        score_columns = [col for col in score_columns if col in df.columns]

        df_clean = df[score_columns].dropna()
        valid_indices = df_clean.index

        X = self.scaler.fit_transform(df_clean.values)

        if n_clusters is None:
            optimal_result = self.find_optimal_clusters(df)
            n_clusters = optimal_result["optimal_k"]

        self.n_clusters = n_clusters

        # Ajustar modelo
        self.model = KMeans(
            n_clusters=n_clusters,
            random_state=self.random_state,
            n_init=10,
        )

        df_result = df.copy()
        df_result["cluster"] = np.nan

        # Asignar clusters solo a filas válidas
        df_result.loc[valid_indices, "cluster"] = self.model.fit_predict(X)

        # Calcular silueta
        silhouette = silhouette_score(X, df_result.loc[valid_indices, "cluster"])
        logger.info(f"Clustering ajustado: {n_clusters} clusters, silueta={silhouette:.4f}")

        return df_result

    def get_cluster_profiles(self, df: pd.DataFrame) -> list[ClusterProfile]:
        """
        Obtiene los perfiles de cada cluster.

        Args:
            df: DataFrame con etiquetas de cluster

        Returns:
            Lista de perfiles
        """
        if "cluster" not in df.columns:
            logger.warning("No hay columna 'cluster' en el DataFrame")
            return []

        profiles = []

        score_columns = [f"score_{d['id']}" for d in self.dimensions]
        score_columns = [col for col in score_columns if col in df.columns]

        # Filtrar NaN en cluster
        df_valid = df.dropna(subset=["cluster"])

        for cluster_id in sorted(df_valid["cluster"].unique()):
            cluster_data = df_valid[df_valid["cluster"] == cluster_id]

            # Centroides (promedios)
            centroid = {}
            for col in score_columns:
                dim_name = col.replace("score_", "")
                centroid[dim_name] = round(float(cluster_data[col].mean()), 3)

            # Calcular perfil (etiqueta basada en dimensiones más altas)
            label = self._generate_cluster_label(centroid)

            profile = ClusterProfile(
                cluster_id=int(cluster_id),
                size=int(len(cluster_data)),
                percentage=round(float(len(cluster_data) / len(df) * 100), 1),
                centroid=centroid,
                label=label,
            )

            profiles.append(profile)

        logger.info(f"Perfiles generados para {len(profiles)} clusters")
        return profiles

    def reduce_dimensions_pca(self, df: pd.DataFrame, n_components: int = 2) -> pd.DataFrame:
        """
        Reduce dimensionalidad con PCA para visualización.

        Args:
            df: DataFrame con puntajes
            n_components: Número de componentes

        Returns:
            DataFrame con componentes principales
        """
        X = self._prepare_features(df)

        pca = PCA(n_components=n_components, random_state=self.random_state)
        components = pca.fit_transform(X)

        df_pca = pd.DataFrame()
        for i in range(n_components):
            df_pca[f"PC{i+1}"] = components[:, i]

        variance_explained = pca.explained_variance_ratio_

        logger.info(
            f"PCA: {n_components} componentes explican "
            f"{sum(variance_explained)*100:.1f}% de varianza"
        )

        return df_pca, variance_explained

    def _prepare_features(self, df: pd.DataFrame) -> np.ndarray:
        """Prepara las features para clustering."""
        score_columns = [f"score_{d['id']}" for d in self.dimensions]
        score_columns = [col for col in score_columns if col in df.columns]

        X = df[score_columns].dropna().values
        X_scaled = self.scaler.fit_transform(X)

        return X_scaled

    def _generate_cluster_label(self, centroid: dict) -> str:
        """Genera una etiqueta descriptiva para el cluster."""
        if not centroid:
            return "Sin perfil"

        # Encontrar dimensiones con mayor puntuación
        sorted_dims = sorted(centroid.items(), key=lambda x: x[1], reverse=True)
        top_dims = [d[0] for d in sorted_dims[:2]]

        dim_names = {d["id"]: d["name"] for d in self.dimensions}

        labels = []
        for dim_id in top_dims:
            if dim_id in dim_names:
                labels.append(dim_names[dim_id])

        return " - ".join(labels) if labels else "Perfil mixto"
