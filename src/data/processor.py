"""
Módulo de procesamiento y validación de datos.
"""

from typing import Tuple, Optional
from dataclasses import dataclass

import pandas as pd
import numpy as np

from src.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class ValidationReport:
    """Reporte de validación de datos."""

    total_records: int
    missing_values: dict
    duplicates: int
    out_of_range: dict
    invalid_types: dict
    reverse_items_applied: list
    is_valid: bool
    warnings: list


class DataProcessor:
    """Procesador de datos de la escala de Ryff."""

    def __init__(self, config: dict):
        """
        Inicializa el procesador.

        Args:
            config: Configuración del proyecto (sección survey)
        """
        self.survey_config = config.get("survey", {})
        self.scale_range = tuple(self.survey_config.get("scale_range", [1, 6]))
        self.num_items = self.survey_config.get("num_items", 29)
        self.dimensions = self.survey_config.get("dimensions", [])
        self.reverse_items = self.survey_config.get("reverse_items", [])

    def validate_data(self, df: pd.DataFrame) -> ValidationReport:
        """
        Valida los datos de la encuesta.

        Args:
            df: DataFrame con las respuestas crudas

        Returns:
            Reporte de validación
        """
        warnings = []
        missing_values = {}
        out_of_range = {}
        invalid_types = {}

        # Verificar valores faltantes
        for col in df.columns:
            missing_count = df[col].isna().sum()
            if missing_count > 0:
                missing_values[col] = int(missing_count)
                warnings.append(f"Columna '{col}': {missing_count} valores faltantes")

        # Verificar duplicados
        duplicates = int(df.duplicated().sum())
        if duplicates > 0:
            warnings.append(f"{duplicates} registros duplicados encontrados")

        # Verificar rango de valores para ítems Likert
        item_columns = self._get_item_columns(df)
        for col in item_columns:
            try:
                values = pd.to_numeric(df[col], errors="coerce")
                invalid_mask = values.isna() & df[col].notna()
                if invalid_mask.any():
                    invalid_types[col] = int(invalid_mask.sum())
                    warnings.append(f"Columna '{col}': valores no numéricos")

                valid_values = values.dropna()
                out_of_range_mask = (valid_values < self.scale_range[0]) | (
                    valid_values > self.scale_range[1]
                )
                if out_of_range_mask.any():
                    out_of_range[col] = int(out_of_range_mask.sum())
                    warnings.append(
                        f"Columna '{col}': {out_of_range_mask.sum()} valores fuera de rango"
                    )
            except Exception as e:
                logger.warning(f"Error al validar columna {col}: {e}")

        is_valid = len(warnings) == 0

        report = ValidationReport(
            total_records=len(df),
            missing_values=missing_values,
            duplicates=duplicates,
            out_of_range=out_of_range,
            invalid_types=invalid_types,
            reverse_items_applied=[],
            is_valid=is_valid,
            warnings=warnings,
        )

        logger.info(
            f"Validación completada: {len(df)} registros, "
            f"{'VÁLIDO' if is_valid else 'INVÁLIDO'}"
        )

        return report

    def clean_data(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, ValidationReport]:
        """
        Limpia y valida los datos.

        Args:
            df: DataFrame con las respuestas crudas

        Returns:
            Tuple de (DataFrame limpio, reporte de validación)
        """
        df_clean = df.copy()
        report = self.validate_data(df)

        # Eliminar duplicados
        if report.duplicates > 0:
            df_clean = df_clean.drop_duplicates()
            logger.info(f"Eliminados {report.duplicates} duplicados")

        # Convertir ítems a numérico
        item_columns = self._get_item_columns(df_clean)
        for col in item_columns:
            df_clean[col] = pd.to_numeric(df_clean[col], errors="coerce")

        return df_clean, report

    def reverse_code_items(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Recodifica ítems invertidos.

        Args:
            df: DataFrame con los datos

        Returns:
            DataFrame con ítems recodificados
        """
        df_recoded = df.copy()
        items_recoded = []

        item_columns = self._get_item_columns(df)

        for col in item_columns:
            # Extraer número del ítem
            item_num = self._extract_item_number(col)

            if item_num in self.reverse_items:
                # Recodificar: (max + 1) - valor_original
                max_val = self.scale_range[1]
                df_recoded[col] = (max_val + 1) - df_recoded[col]
                items_recoded.append(item_num)
                logger.debug(f"Ítem {item_num} recodificado")

        logger.info(f"Recodificados {len(items_recoded)} ítems invertidos")
        return df_recoded

    def calculate_dimension_scores(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calcula los puntajes por dimensión.

        Args:
            df: DataFrame con datos recodificados

        Returns:
            DataFrame con puntajes por dimensión
        """
        df_scores = df.copy()

        for dimension in self.dimensions:
            dim_id = dimension["id"]
            dim_name = dimension["name"]
            item_indices = dimension["items"]

            # Encontrar columnas de ítems
            item_columns = []
            for item_idx in item_indices:
                col = self._find_item_column(df, item_idx)
                if col:
                    item_columns.append(col)

            if item_columns:
                # Calcular promedio de la dimensión
                df_scores[f"score_{dim_id}"] = df[item_columns].mean(axis=1)
                logger.debug(
                    f"Dimensión {dim_name}: calculada con {len(item_columns)} ítems"
                )

        return df_scores

    def calculate_global_score(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calcula el índice global de bienestar.

        Args:
            df: DataFrame con puntajes por dimensión

        Returns:
            DataFrame con puntaje global
        """
        df_global = df.copy()

        score_columns = [col for col in df.columns if col.startswith("score_")]

        if score_columns:
            df_global["wellbeing_global"] = df_global[score_columns].mean(axis=1)
            logger.info(f"Índice global calculado: promedio de {len(score_columns)} dimensiones")

        return df_global

    def prepare_analysis_data(
        self, df: pd.DataFrame
    ) -> Tuple[pd.DataFrame, ValidationReport]:
        """
        Prepara los datos completos para análisis.

        Args:
            df: DataFrame con respuestas crudas

        Returns:
            Tuple de (DataFrame preparado, reporte)
        """
        # Limpiar datos
        df_clean, report = self.clean_data(df)

        # Recodificar ítems invertidos
        df_recoded = self.reverse_code_items(df_clean)

        # Calcular puntajes por dimensión
        df_scores = self.calculate_dimension_scores(df_recoded)

        # Calcular puntaje global
        df_final = self.calculate_global_score(df_scores)

        logger.info("Datos preparados para análisis")
        return df_final, report

    def _get_item_columns(self, df: pd.DataFrame) -> list:
        """Obtiene las columnas que contienen ítems de la escala."""
        item_columns = []
        for col in df.columns:
            item_num = self._extract_item_number(col)
            if item_num and 1 <= item_num <= self.num_items:
                item_columns.append(col)
        return item_columns

    def _extract_item_number(self, column_name: str) -> Optional[int]:
        """Extrae el número del ítem del nombre de la columna."""
        import re

        # Buscar patrones como "1", "1. Texto...", "Ítem 1", "Q1", "Pregunta 1"
        patterns = [
            r"^(\d+)\.\s",  # "1. Cuando repaso..."
            r"^(\d+)$",     # Solo el número
            r"[Íi]tem\s*(\d+)",
            r"[Qq](\d+)",
            r"[Pp]regunta\s*(\d+)",
        ]

        for pattern in patterns:
            match = re.search(pattern, str(column_name))
            if match:
                return int(match.group(1))

        return None

    def _find_item_column(self, df: pd.DataFrame, item_number: int) -> Optional[str]:
        """Encuentra la columna que corresponde a un número de ítem."""
        for col in df.columns:
            if self._extract_item_number(col) == item_number:
                return col
        return None
