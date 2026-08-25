"""
Módulo de recolección de datos desde Google Forms/Sheets.
"""

import os
from typing import Optional
from datetime import datetime

import pandas as pd
from google.oauth2 import service_account
from googleapiclient.discovery import build

from src.utils.logger import get_logger

logger = get_logger(__name__)


class GoogleFormsCollector:
    """Cliente para extraer respuestas desde Google Forms/Sheets."""

    def __init__(self, config: dict):
        """
        Inicializa el recolector.

        Args:
            config: Configuración del proyecto (sección google_forms)
        """
        self.config = config
        self.credentials_file = config.get("credentials_file", "")
        self.spreadsheet_id = config.get("spreadsheet_id", "")
        self.scopes = config.get("scopes", [])
        self.service = None

    def _authenticate(self):
        """Autentica con Google API usando credenciales de servicio."""
        if not os.path.exists(self.credentials_file):
            raise FileNotFoundError(
                f"Archivo de credenciales no encontrado: {self.credentials_file}"
            )

        credentials = service_account.Credentials.from_service_account_file(
            self.credentials_file, scopes=self.scopes
        )
        self.service = build("sheets", "v4", credentials=credentials)
        logger.info("Autenticación con Google API exitosa")

    def connect(self):
        """Establece conexión con Google Sheets."""
        try:
            self._authenticate()
            logger.info("Conexión establecida correctamente")
            return True
        except Exception as e:
            logger.error(f"Error al conectar con Google API: {e}")
            return False

    def extract_responses(
        self,
        range_name: str = None,
        max_results: Optional[int] = None,
    ) -> pd.DataFrame:
        """
        Extrae las respuestas de la encuesta.

        Args:
            range_name: Rango de celdas a extraer (None = toda la hoja)
            max_results: Número máximo de resultados (None = todos)

        Returns:
            DataFrame con las respuestas
        """
        if not self.service:
            self._authenticate()

        try:
            # Si no se especifica rango, obtener toda la hoja
            if range_name is None:
                # Primero obtener el nombre de la hoja
                spreadsheet = self.service.spreadsheets().get(
                    spreadsheetId=self.spreadsheet_id
                ).execute()
                sheets = spreadsheet.get('sheets', [])
                if sheets:
                    sheet_name = sheets[0]['properties']['title']
                    range_name = f"'{sheet_name}'"
                else:
                    range_name = "'Respuestas de formulario'"

            result = (
                self.service.spreadsheets()
                .values()
                .get(
                    spreadsheetId=self.spreadsheet_id,
                    range=range_name,
                )
                .execute()
            )

            values = result.get("values", [])

            if not values:
                logger.warning("No se encontraron respuestas")
                return pd.DataFrame()

            # Primera fila como encabezados
            headers = values[0]
            data = values[1:]

            if max_results:
                data = data[:max_results]

            df = pd.DataFrame(data, columns=headers)
            logger.info(f"Extraídas {len(df)} respuestas")
            return df

        except Exception as e:
            logger.error(f"Error al extraer respuestas: {e}")
            return pd.DataFrame()

    def get_last_response_timestamp(self) -> Optional[datetime]:
        """
        Obtiene el timestamp de la última respuesta.

        Returns:
            datetime de la última respuesta o None
        """
        df = self.extract_responses(max_results=1)

        if df.empty:
            return None

        # Buscar columna de timestamp
        timestamp_col = None
        for col in df.columns:
            if "hora" in col.lower() and "inicio" in col.lower():
                timestamp_col = col
                break

        if not timestamp_col:
            timestamp_col = df.columns[0]

        try:
            timestamp_str = df[timestamp_col].iloc[0]
            return datetime.strptime(timestamp_str, "%d/%m/%Y %H:%M:%S")
        except Exception:
            return None

    def has_new_responses(self, last_check: Optional[datetime] = None) -> bool:
        """
        Verifica si hay nuevas respuestas desde la última verificación.

        Args:
            last_check: Timestamp de la última verificación

        Returns:
            True si hay nuevas respuestas
        """
        if last_check is None:
            return True

        current_timestamp = self.get_last_response_timestamp()

        if current_timestamp is None:
            return False

        return current_timestamp > last_check

    def save_raw_data(
        self, df: pd.DataFrame, output_dir: str = "data/raw"
    ) -> str:
        """
        Guarda los datos crudos en formato CSV.

        Args:
            df: DataFrame con las respuestas
            output_dir: Directorio de salida

        Returns:
            Ruta del archivo guardado
        """
        os.makedirs(output_dir, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"encuesta_felicidad_{timestamp}.csv"
        filepath = os.path.join(output_dir, filename)

        df.to_csv(filepath, index=False, encoding="utf-8-sig")
        logger.info(f"Datos guardados en: {filepath}")

        return filepath


def load_local_csv(filepath: str) -> pd.DataFrame:
    """
    Carga un archivo CSV local (para carga manual).

    Args:
        filepath: Ruta al archivo CSV

    Returns:
        DataFrame con los datos
    """
    try:
        df = pd.read_csv(filepath, encoding="utf-8-sig")
        logger.info(f"CSV local cargado: {len(df)} registros")
        return df
    except Exception as e:
        logger.error(f"Error al cargar CSV: {e}")
        return pd.DataFrame()
