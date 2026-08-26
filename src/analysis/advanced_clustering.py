"""
Módulo de clustering avanzado.
Incluye DBSCAN, clustering jerárquico y métodos ensemble.
"""

from typing import Optional
from dataclasses import dataclass

import pandas as pd
import numpy as np
from sklearn.cluster import DBSCAN, AgglomerativeClustering
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score, calinski_harabasz_score
from scipy.cluster.hierarchy import dendrogram, linkage
from scipy.spatial.distance import pdist

from src.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class AdvancedClusterResult:
    """Resultado de clustering avanzado."""
    method: str
    n_clusters: int
    labels: list
    silhouette: float
    calinski_harabasz: float
    noise_points: int
    cluster_centers: Optional[list]


class AdvancedClusteringAnalyzer:
    """Analizador de clustering avanzado."""

    def __init__(self, config: dict):
        """
        Inicializa el analizador.

        Args:
            config: Configuración del proyecto
        """
        self.config = config
        self.dimensions = config.get("survey", {}).get("dimensions", [])
        self.scaler = StandardScaler()

    def dbscan_clustering(
        self,
        df: pd.DataFrame,
        eps: float = 0.5,
        min_samples: int = 5,
    ) -> dict:
        """
        Clustering DBSCAN (basado en densidad).

        Args:
            df: DataFrame con puntajes
            eps: Radio del vecindario
            min_samples: Mínimo de puntos para formar cluster

        Returns:
            Resultados de DBSCAN
        """
        score_columns = [f"score_{d['id']}" for d in self.dimensions]
        score_columns = [col for col in score_columns if col in df.columns]

        X = df[score_columns].dropna()
        X_scaled = self.scaler.fit_transform(X)

        # DBSCAN
        dbscan = DBSCAN(eps=eps, min_samples=min_samples)
        labels = dbscan.fit_predict(X_scaled)

        n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
        noise_points = list(labels).count(-1)

        # Métricas (excluyendo ruido)
        if n_clusters > 1:
            mask = labels != -1
            silhouette = silhouette_score(X_scaled[mask], labels[mask])
            calinski = calinski_harabasz_score(X_scaled[mask], labels[mask])
        else:
            silhouette = 0
            calinski = 0

        result = {
            "method": "DBSCAN",
            "eps": eps,
            "min_samples": min_samples,
            "n_clusters": n_clusters,
            "noise_points": noise_points,
            "noise_percentage": round(noise_points / len(labels) * 100, 2),
            "silhouette": round(float(silhouette), 4),
            "calinski_harabasz": round(float(calinski), 4),
            "labels": labels.tolist(),
            "cluster_sizes": {
                i: int(np.sum(labels == i))
                for i in range(n_clusters)
            },
        }

        logger.info(f"DBSCAN: {n_clusters} clusters, {noise_points} puntos de ruido")
        return result

    def hierarchical_clustering(
        self,
        df: pd.DataFrame,
        n_clusters: int = 3,
        linkage_method: str = "ward",
    ) -> dict:
        """
        Clustering jerárquico.

        Args:
            df: DataFrame con puntajes
            n_clusters: Número de clusters
            linkage_method: Método de enlace ("ward", "complete", "average", "single")

        Returns:
            Resultados del clustering jerárquico
        """
        score_columns = [f"score_{d['id']}" for d in self.dimensions]
        score_columns = [col for col in score_columns if col in df.columns]

        X = df[score_columns].dropna()
        X_scaled = self.scaler.fit_transform(X)

        # Clustering jerárquico
        hc = AgglomerativeClustering(
            n_clusters=n_clusters,
            linkage=linkage_method
        )
        labels = hc.fit_predict(X_scaled)

        # Métricas
        silhouette = silhouette_score(X_scaled, labels)
        calinski = calinski_harabasz_score(X_scaled, labels)

        # Matriz de enlace para dendrograma
        linkage_matrix = linkage(X_scaled, method=linkage_method)

        # Centros de cluster
        cluster_centers = []
        for i in range(n_clusters):
            mask = labels == i
            center = X_scaled[mask].mean(axis=0)
            cluster_centers.append(center.tolist())

        result = {
            "method": "Hierarchical",
            "linkage": linkage_method,
            "n_clusters": n_clusters,
            "silhouette": round(float(silhouette), 4),
            "calinski_harabasz": round(float(calinski), 4),
            "labels": labels.tolist(),
            "cluster_centers": cluster_centers,
            "cluster_sizes": {
                i: int(np.sum(labels == i))
                for i in range(n_clusters)
            },
        }

        logger.info(f"Hierarchical: {n_clusters} clusters, silhouette = {silhouette:.4f}")
        return result

    def find_optimal_dbscan_params(
        self,
        df: pd.DataFrame,
        eps_range: list = None,
        min_samples_range: list = None,
    ) -> dict:
        """
        Encuentra los mejores parámetros para DBSCAN.

        Args:
            df: DataFrame con puntajes
            eps_range: Rangos de eps a probar
            min_samples_range: Rangos de min_samples a probar

        Returns:
            Mejores parámetros encontrados
        """
        if eps_range is None:
            eps_range = [0.3, 0.5, 0.7, 1.0, 1.5]
        if min_samples_range is None:
            min_samples_range = [3, 5, 7, 10]

        score_columns = [f"score_{d['id']}" for d in self.dimensions]
        score_columns = [col for col in score_columns if col in df.columns]

        X = df[score_columns].dropna()
        X_scaled = self.scaler.fit_transform(X)

        best_score = -1
        best_params = {}

        for eps in eps_range:
            for min_samples in min_samples_range:
                try:
                    dbscan = DBSCAN(eps=eps, min_samples=min_samples)
                    labels = dbscan.fit_predict(X_scaled)

                    n_clusters = len(set(labels)) - (1 if -1 in labels else 0)

                    if n_clusters > 1:
                        mask = labels != -1
                        silhouette = silhouette_score(X_scaled[mask], labels[mask])

                        if silhouette > best_score:
                            best_score = silhouette
                            best_params = {
                                "eps": eps,
                                "min_samples": min_samples,
                                "n_clusters": n_clusters,
                                "silhouette": round(float(silhouette), 4),
                            }
                except:
                    continue

        result = {
            "best_params": best_params,
            "best_silhouette": round(float(best_score), 4),
            "n_combinations_tested": len(eps_range) * len(min_samples_range),
        }

        logger.info(f"Mejores params DBSCAN: {best_params}")
        return result

    def ensemble_clustering(
        self,
        df: pd.DataFrame,
        n_clusters: int = 3,
    ) -> dict:
        """
        Clustering ensemble (combina múltiples métodos).

        Args:
            df: DataFrame con puntajes
            n_clusters: Número de clusters

        Returns:
            Resultados del ensemble
        """
        score_columns = [f"score_{d['id']}" for d in self.dimensions]
        score_columns = [col for col in score_columns if col in df.columns]

        X = df[score_columns].dropna()
        X_scaled = self.scaler.fit_transform(X)

        from sklearn.cluster import KMeans

        # Ejecutar múltiples métodos
        methods = {
            "kmeans": KMeans(n_clusters=n_clusters, random_state=42, n_init=10),
            "hierarchical_ward": AgglomerativeClustering(n_clusters=n_clusters, linkage="ward"),
            "hierarchical_complete": AgglomerativeClustering(n_clusters=n_clusters, linkage="complete"),
        }

        all_labels = {}
        for name, model in methods.items():
            if hasattr(model, 'fit_predict'):
                labels = model.fit_predict(X_scaled)
            else:
                model.fit(X_scaled)
                labels = model.labels_
            all_labels[name] = labels

        # Co-enlace: cuántos métodos coinciden en cada par
        n_samples = len(X)
        co_association = np.zeros((n_samples, n_samples))

        for name, labels in all_labels.items():
            for i in range(n_samples):
                for j in range(i + 1, n_samples):
                    if labels[i] == labels[j]:
                        co_association[i, j] += 1
                        co_association[j, i] += 1

        # Normalizar
        co_association /= len(methods)

        # Clustering jerárquico sobre co-asociación
        from scipy.cluster.hierarchy import fcluster
        from scipy.spatial.distance import squareform

        distance_matrix = 1 - co_association
        np.fill_diagonal(distance_matrix, 0)
        condensed = squareform(distance_matrix)
        linkage_matrix = linkage(condensed, method="average")
        ensemble_labels = fcluster(linkage_matrix, n_clusters, criterion='maxclust')

        # Métricas
        silhouette = silhouette_score(X_scaled, ensemble_labels - 1)
        calinski = calinski_harabasz_score(X_scaled, ensemble_labels - 1)

        result = {
            "method": "Ensemble",
            "n_clusters": n_clusters,
            "methods_used": list(all_labels.keys()),
            "silhouette": round(float(silhouette), 4),
            "calinski_harabasz": round(float(calinski), 4),
            "labels": (ensemble_labels - 1).tolist(),
            "cluster_sizes": {
                i: int(np.sum(ensemble_labels - 1 == i))
                for i in range(n_clusters)
            },
        }

        logger.info(f"Ensemble: {n_clusters} clusters, silhouette = {silhouette:.4f}")
        return result

    def compare_methods(
        self,
        df: pd.DataFrame,
        n_clusters: int = 3,
    ) -> dict:
        """
        Compara diferentes métodos de clustering.

        Args:
            df: DataFrame con puntajes
            n_clusters: Número de clusters para comparar

        Returns:
            Comparación de métodos
        """
        results = {}

        # K-Means
        from sklearn.cluster import KMeans
        score_columns = [f"score_{d['id']}" for d in self.dimensions]
        score_columns = [col for col in score_columns if col in df.columns]
        X = df[score_columns].dropna()
        X_scaled = self.scaler.fit_transform(X)

        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        kmeans_labels = kmeans.fit_predict(X_scaled)
        results["kmeans"] = {
            "silhouette": round(float(silhouette_score(X_scaled, kmeans_labels)), 4),
            "calinski": round(float(calinski_harabasz_score(X_scaled, kmeans_labels)), 4),
        }

        # Hierarchical Ward
        hc_ward = AgglomerativeClustering(n_clusters=n_clusters, linkage="ward")
        hc_labels = hc_ward.fit_predict(X_scaled)
        results["hierarchical_ward"] = {
            "silhouette": round(float(silhouette_score(X_scaled, hc_labels)), 4),
            "calinski": round(float(calinski_harabasz_score(X_scaled, hc_labels)), 4),
        }

        # Hierarchical Complete
        hc_complete = AgglomerativeClustering(n_clusters=n_clusters, linkage="complete")
        hc_labels = hc_complete.fit_predict(X_scaled)
        results["hierarchical_complete"] = {
            "silhouette": round(float(silhouette_score(X_scaled, hc_labels)), 4),
            "calinski": round(float(calinski_harabasz_score(X_scaled, hc_labels)), 4),
        }

        # DBSCAN
        dbscan = DBSCAN(eps=0.5, min_samples=5)
        db_labels = dbscan.fit_predict(X_scaled)
        n_clusters_db = len(set(db_labels)) - (1 if -1 in db_labels else 0)
        if n_clusters_db > 1:
            mask = db_labels != -1
            results["dbscan"] = {
                "silhouette": round(float(silhouette_score(X_scaled[mask], db_labels[mask])), 4),
                "calinski": round(float(calinski_harabasz_score(X_scaled[mask], db_labels[mask])), 4),
                "n_clusters": n_clusters_db,
            }

        # Encontrar mejor método
        best_method = max(results.items(), key=lambda x: x[1].get("silhouette", 0))

        result = {
            "results": results,
            "best_method": best_method[0],
            "best_silhouette": best_method[1].get("silhouette", 0),
        }

        logger.info(f"Mejor método: {result['best_method']}")
        return result
