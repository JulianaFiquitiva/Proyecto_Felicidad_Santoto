"""
Módulo de modelos predictivos avanzados.
Incluye Random Forest, SVM, Gradient Boosting y redes neuronales.
"""

from typing import Optional
from dataclasses import dataclass

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.svm import SVC
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, confusion_matrix, classification_report
)

from src.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class PredictiveResult:
    """Resultado de modelo predictivo."""
    model_name: str
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    auc_roc: float
    cv_scores: list
    feature_importance: Optional[dict]
    confusion_matrix: list


class PredictiveModelAnalyzer:
    """Analizador de modelos predictivos."""

    def __init__(self, config: dict):
        """
        Inicializa el analizador.

        Args:
            config: Configuración del proyecto
        """
        self.config = config
        self.dimensions = config.get("survey", {}).get("dimensions", [])
        self.scaler = StandardScaler()

    def random_forest(
        self,
        df: pd.DataFrame,
        target: str = "wellbeing_category",
        threshold: float = 3.5,
    ) -> dict:
        """
        Modelo Random Forest para predecir bienestar.

        Args:
            df: DataFrame con puntajes
            target: Variable objetivo
            threshold: Umbral para categorizar bienestar

        Returns:
            Resultados del modelo
        """
        X, y = self._prepare_data(df, target, threshold)

        if X is None:
            return {"error": "Datos insuficientes"}

        # Split train/test
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )

        # Estandarizar
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)

        # Modelo
        rf = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            n_jobs=-1
        )
        rf.fit(X_train_scaled, y_train)

        # Predicciones
        y_pred = rf.predict(X_test_scaled)
        y_prob = rf.predict_proba(X_test_scaled)[:, 1] if len(np.unique(y)) == 2 else None

        # Métricas
        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred, average='weighted')
        recall = recall_score(y_test, y_pred, average='weighted')
        f1 = f1_score(y_test, y_pred, average='weighted')
        auc_roc = roc_auc_score(y_test, y_prob) if y_prob is not None else 0

        # Validación cruzada
        X_all_scaled = self.scaler.fit_transform(X)
        cv_scores = cross_val_score(rf, X_all_scaled, y, cv=5, scoring='accuracy')

        # Importancia de features
        score_columns = [f"score_{d['id']}" for d in self.dimensions]
        score_columns = [col for col in score_columns if col in df.columns]
        feature_importance = dict(zip(score_columns, rf.feature_importances_))

        result = {
            "model_name": "Random Forest",
            "accuracy": round(float(accuracy), 4),
            "precision": round(float(precision), 4),
            "recall": round(float(recall), 4),
            "f1_score": round(float(f1), 4),
            "auc_roc": round(float(auc_roc), 4),
            "cv_scores": [round(float(s), 4) for s in cv_scores],
            "cv_mean": round(float(cv_scores.mean()), 4),
            "cv_std": round(float(cv_scores.std()), 4),
            "feature_importance": {k: round(float(v), 4) for k, v in feature_importance.items()},
            "confusion_matrix": confusion_matrix(y_test, y_pred).tolist(),
        }

        logger.info(f"Random Forest: Accuracy = {accuracy:.4f}, AUC = {auc_roc:.4f}")
        return result

    def svm(
        self,
        df: pd.DataFrame,
        target: str = "wellbeing_category",
        threshold: float = 3.5,
        kernel: str = "rbf",
    ) -> dict:
        """
        Support Vector Machine para predecir bienestar.

        Args:
            df: DataFrame con puntajes
            target: Variable objetivo
            threshold: Umbral para categorizar
            kernel: Tipo de kernel ("rbf", "linear", "poly")

        Returns:
            Resultados del modelo
        """
        X, y = self._prepare_data(df, target, threshold)

        if X is None:
            return {"error": "Datos insuficientes"}

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )

        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)

        svm_model = SVC(
            kernel=kernel,
            probability=True,
            random_state=42
        )
        svm_model.fit(X_train_scaled, y_train)

        y_pred = svm_model.predict(X_test_scaled)
        y_prob = svm_model.predict_proba(X_test_scaled)[:, 1] if len(np.unique(y)) == 2 else None

        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred, average='weighted')
        recall = recall_score(y_test, y_pred, average='weighted')
        f1 = f1_score(y_test, y_pred, average='weighted')
        auc_roc = roc_auc_score(y_test, y_prob) if y_prob is not None else 0

        X_all_scaled = self.scaler.fit_transform(X)
        cv_scores = cross_val_score(svm_model, X_all_scaled, y, cv=5, scoring='accuracy')

        result = {
            "model_name": f"SVM ({kernel})",
            "accuracy": round(float(accuracy), 4),
            "precision": round(float(precision), 4),
            "recall": round(float(recall), 4),
            "f1_score": round(float(f1), 4),
            "auc_roc": round(float(auc_roc), 4),
            "cv_scores": [round(float(s), 4) for s in cv_scores],
            "cv_mean": round(float(cv_scores.mean()), 4),
            "cv_std": round(float(cv_scores.std()), 4),
            "kernel": kernel,
            "confusion_matrix": confusion_matrix(y_test, y_pred).tolist(),
        }

        logger.info(f"SVM ({kernel}): Accuracy = {accuracy:.4f}")
        return result

    def gradient_boosting(
        self,
        df: pd.DataFrame,
        target: str = "wellbeing_category",
        threshold: float = 3.5,
    ) -> dict:
        """
        Gradient Boosting para predecir bienestar.

        Args:
            df: DataFrame con puntajes
            target: Variable objetivo
            threshold: Umbral para categorizar

        Returns:
            Resultados del modelo
        """
        X, y = self._prepare_data(df, target, threshold)

        if X is None:
            return {"error": "Datos insuficientes"}

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )

        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)

        gb = GradientBoostingClassifier(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=5,
            random_state=42
        )
        gb.fit(X_train_scaled, y_train)

        y_pred = gb.predict(X_test_scaled)
        y_prob = gb.predict_proba(X_test_scaled)[:, 1] if len(np.unique(y)) == 2 else None

        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred, average='weighted')
        recall = recall_score(y_test, y_pred, average='weighted')
        f1 = f1_score(y_test, y_pred, average='weighted')
        auc_roc = roc_auc_score(y_test, y_prob) if y_prob is not None else 0

        X_all_scaled = self.scaler.fit_transform(X)
        cv_scores = cross_val_score(gb, X_all_scaled, y, cv=5, scoring='accuracy')

        score_columns = [f"score_{d['id']}" for d in self.dimensions]
        score_columns = [col for col in score_columns if col in df.columns]
        feature_importance = dict(zip(score_columns, gb.feature_importances_))

        result = {
            "model_name": "Gradient Boosting",
            "accuracy": round(float(accuracy), 4),
            "precision": round(float(precision), 4),
            "recall": round(float(recall), 4),
            "f1_score": round(float(f1), 4),
            "auc_roc": round(float(auc_roc), 4),
            "cv_scores": [round(float(s), 4) for s in cv_scores],
            "cv_mean": round(float(cv_scores.mean()), 4),
            "cv_std": round(float(cv_scores.std()), 4),
            "feature_importance": {k: round(float(v), 4) for k, v in feature_importance.items()},
            "confusion_matrix": confusion_matrix(y_test, y_pred).tolist(),
        }

        logger.info(f"Gradient Boosting: Accuracy = {accuracy:.4f}")
        return result

    def neural_network(
        self,
        df: pd.DataFrame,
        target: str = "wellbeing_category",
        threshold: float = 3.5,
    ) -> dict:
        """
        Red neuronal para predecir bienestar.

        Args:
            df: DataFrame con puntajes
            target: Variable objetivo
            threshold: Umbral para categorizar

        Returns:
            Resultados del modelo
        """
        X, y = self._prepare_data(df, target, threshold)

        if X is None:
            return {"error": "Datos insuficientes"}

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )

        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)

        mlp = MLPClassifier(
            hidden_layer_sizes=(100, 50),
            activation='relu',
            max_iter=500,
            random_state=42
        )
        mlp.fit(X_train_scaled, y_train)

        y_pred = mlp.predict(X_test_scaled)
        y_prob = mlp.predict_proba(X_test_scaled)[:, 1] if len(np.unique(y)) == 2 else None

        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred, average='weighted')
        recall = recall_score(y_test, y_pred, average='weighted')
        f1 = f1_score(y_test, y_pred, average='weighted')
        auc_roc = roc_auc_score(y_test, y_prob) if y_prob is not None else 0

        X_all_scaled = self.scaler.fit_transform(X)
        cv_scores = cross_val_score(mlp, X_all_scaled, y, cv=5, scoring='accuracy')

        result = {
            "model_name": "Neural Network (MLP)",
            "accuracy": round(float(accuracy), 4),
            "precision": round(float(precision), 4),
            "recall": round(float(recall), 4),
            "f1_score": round(float(f1), 4),
            "auc_roc": round(float(auc_roc), 4),
            "cv_scores": [round(float(s), 4) for s in cv_scores],
            "cv_mean": round(float(cv_scores.mean()), 4),
            "cv_std": round(float(cv_scores.std()), 4),
            "architecture": [100, 50],
            "confusion_matrix": confusion_matrix(y_test, y_pred).tolist(),
        }

        logger.info(f"Neural Network: Accuracy = {accuracy:.4f}")
        return result

    def compare_all_models(
        self,
        df: pd.DataFrame,
        target: str = "wellbeing_category",
        threshold: float = 3.5,
    ) -> dict:
        """
        Compara todos los modelos predictivos.

        Args:
            df: DataFrame con puntajes
            target: Variable objetivo
            threshold: Umbral para categorizar

        Returns:
            Comparación de modelos
        """
        models = {
            "Random Forest": self.random_forest(df, target, threshold),
            "SVM (RBF)": self.svm(df, target, threshold, "rbf"),
            "SVM (Linear)": self.svm(df, target, threshold, "linear"),
            "Gradient Boosting": self.gradient_boosting(df, target, threshold),
            "Neural Network": self.neural_network(df, target, threshold),
        }

        # Encontrar mejor modelo
        best_model = max(
            models.items(),
            key=lambda x: x[1].get("accuracy", 0)
        )

        result = {
            "models": models,
            "best_model": best_model[0],
            "best_accuracy": best_model[1].get("accuracy", 0),
            "best_auc_roc": best_model[1].get("auc_roc", 0),
        }

        logger.info(f"Mejor modelo: {result['best_model']} (Accuracy = {result['best_accuracy']:.4f})")
        return result

    def _prepare_data(
        self,
        df: pd.DataFrame,
        target: str,
        threshold: float,
    ):
        """Prepara datos para modelos predictivos."""
        score_columns = [f"score_{d['id']}" for d in self.dimensions]
        score_columns = [col for col in score_columns if col in df.columns]

        if not score_columns or "wellbeing_global" not in df.columns:
            return None, None

        X = df[score_columns].dropna()
        y = (df.loc[X.index, "wellbeing_global"] < threshold).astype(int)

        if len(X) < 30:
            logger.warning("Muy pocos casos para modelos predictivos")
            return None, None

        return X, y
