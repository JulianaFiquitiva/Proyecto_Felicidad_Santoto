"""
Módulo de interpretación inteligente con Google Gemini.
"""

import google.generativeai as genai
from typing import Optional

from src.utils.logger import get_logger

logger = get_logger(__name__)


class AIInterpreter:
    """Intérprete de resultados usando Google Gemini."""

    def __init__(self, config: dict):
        """
        Inicializa el intérprete de IA.

        Args:
            config: Configuración del proyecto (sección ai)
        """
        self.config = config.get("ai", {})
        self.enabled = self.config.get("enabled", False)
        self.model_name = self.config.get("model", "gemini-1.5-flash")
        self.temperature = self.config.get("temperature", 0.7)
        self.max_tokens = self.config.get("max_tokens", 2000)
        self.model = None

        if self.enabled:
            self._configure()

    def _configure(self):
        """Configura la conexión con Google Gemini."""
        api_key = self.config.get("api_key", "")

        if not api_key:
            logger.warning("API key de Gemini no configurada")
            self.enabled = False
            return

        try:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel(
                model_name=self.model_name,
                generation_config=genai.types.GenerationConfig(
                    temperature=self.temperature,
                    max_output_tokens=self.max_tokens,
                )
            )
            logger.info(f"Gemini configurado: {self.model_name}")
        except Exception as e:
            logger.error(f"Error al configurar Gemini: {e}")
            self.enabled = False

    def interpret_results(self, analysis_results: dict) -> str:
        """
        Genera una interpretación inteligente de los resultados.

        Args:
            analysis_results: Resultados del análisis estadístico

        Returns:
            Texto interpretativo generado por IA
        """
        if not self.enabled or not self.model:
            return self._generate_basic_interpretation(analysis_results)

        prompt = self._build_interpretation_prompt(analysis_results)

        try:
            response = self.model.generate_content(prompt)
            interpretation = response.text
            logger.info("Interpretación generada por IA")
            return interpretation
        except Exception as e:
            logger.error(f"Error al generar interpretación: {e}")
            return self._generate_basic_interpretation(analysis_results)

    def generate_executive_summary(self, analysis_results: dict) -> str:
        """
        Genera un resumen ejecutivo con IA.

        Args:
            analysis_results: Resultados del análisis

        Returns:
            Resumen ejecutivo
        """
        if not self.enabled or not self.model:
            return self._generate_basic_summary(analysis_results)

        prompt = self._build_summary_prompt(analysis_results)

        try:
            response = self.model.generate_content(prompt)
            summary = response.text
            logger.info("Resumen ejecutivo generado por IA")
            return summary
        except Exception as e:
            logger.error(f"Error al generar resumen: {e}")
            return self._generate_basic_summary(analysis_results)

    def generate_recommendations(self, analysis_results: dict) -> list[str]:
        """
        Genera recomendaciones inteligentes.

        Args:
            analysis_results: Resultados del análisis

        Returns:
            Lista de recomendaciones
        """
        if not self.enabled or not self.model:
            return self._generate_basic_recommendations(analysis_results)

        prompt = self._build_recommendations_prompt(analysis_results)

        try:
            response = self.model.generate_content(prompt)
            recommendations = [r.strip() for r in response.text.split("\n") if r.strip() and not r.startswith("#")]
            logger.info("Recomendaciones generadas por IA")
            return recommendations
        except Exception as e:
            logger.error(f"Error al generar recomendaciones: {e}")
            return self._generate_basic_recommendations(analysis_results)

    def _build_interpretation_prompt(self, results: dict) -> str:
        """Construye el prompt para interpretación."""
        dimensions = results.get("dimension_stats", [])
        global_mean = results.get("global_mean", 0)
        global_std = results.get("global_std", 0)
        correlations = results.get("correlations", [])
        regression = results.get("regression", {})
        clusters = results.get("clusters", [])

        dim_text = "\n".join([
            f"- {d['dimension']}: Media={d['mean']:.2f}, DE={d['std']:.2f}"
            for d in dimensions
        ])

        corr_text = "\n".join([
            f"- {c['var1']} ↔ {c['var2']}: r={c['correlation']:.3f} (p={c['p_value']:.4f})"
            for c in correlations if c.get('significant')
        ])

        prompt = f"""
Eres un psicólogo experto en bienestar estudiantil analizando datos de la Escala de Ryff.

RESULTADOS DEL ANÁLISIS:
- Total de participantes: {results.get('total_responses', 0)}
- Bienestar global: {global_mean:.2f} / 6.00 (DE: {global_std:.2f})

RESULTADOS POR DIMENSIÓN:
{dim_text}

CORRELACIONES SIGNIFICATIVAS:
{corr_text if corr_text else "No se encontraron correlaciones significativas"}

MODELO PREDICTOR (R² = {regression.get('r_squared', 0):.3f}):
{chr(10).join([f"- {f['factor']}: β={f['std_coefficient']:.3f} (p={f['p_value']:.4f})" for f in regression.get('factors', [])[:5]])}

PERFILES IDENTIFICADOS: {len(clusters)} grupos

INSTRUCCIONES:
Interpara estos resultados como un profesional de la psicología. Explica qué significan los hallazgos
para el bienestar de los estudiantes de la Universidad Santo Tomás. Sé claro, profesional y práctico.
"""
        return prompt

    def _build_summary_prompt(self, results: dict) -> str:
        """Construye el prompt para resumen ejecutivo."""
        return f"""
Genera un resumen ejecutivo para gerencia de la Universidad Santo Tomás sobre el análisis
de bienestar psicológico de sus estudiantes.

DATOS:
- Participantes: {results.get('total_responses', 0)}
- Bienestar global promedio: {results.get('global_mean', 0):.2f} / 6.00
- Dimensiones analizadas: {len(results.get('dimension_stats', []))}
- Perfiles identificados: {len(results.get('clusters', []))}

El resumen debe:
1. Ser máximo 200 palabras
2. Destacar los hallazgos más importantes
3. Incluir implicaciones prácticas
4. Ser escrito para audiencia no técnica
"""

    def _build_recommendations_prompt(self, results: dict) -> str:
        """Construye el prompt para recomendaciones."""
        dimensions = results.get("dimension_stats", [])
        weakest = min(dimensions, key=lambda x: x['mean']) if dimensions else None
        
        weakest_name = weakest['dimension'] if weakest else 'N/A'
        weakest_mean = f"{weakest['mean']:.2f}" if weakest else "0"
        global_mean = f"{results.get('global_mean', 0):.2f}"

        return f"""
Basado en el análisis de bienestar psicológico de estudiantes de la Universidad Santo Tomás:

Dimensión más baja: {weakest_name} ({weakest_mean}/6.00)
Bienestar global: {global_mean}/6.00

Genera 5 recomendaciones específicas, accionables y priorizadas para mejorar el bienestar
estudiantil. Formato: lista numerada.
"""

    def _generate_basic_interpretation(self, results: dict) -> str:
        """Genera interpretación básica sin IA."""
        dimensions = results.get("dimension_stats", [])
        global_mean = results.get("global_mean", 0)

        interp = f"Análisis de {results.get('total_responses', 0)} estudiantes.\n"
        interp += f"El bienestar global promedio es {global_mean:.2f} sobre 6.00.\n\n"
        interp += "Resultados por dimensión:\n"

        for d in dimensions:
            interp += f"- {d['dimension']}: {d['mean']:.2f}\n"

        return interp

    def _generate_basic_summary(self, results: dict) -> str:
        """Genera resumen básico sin IA."""
        return f"""
RESUMEN EJECUTIVO
Análisis de Bienestar Psicológico - Universidad Santo Tomás

Participantes: {results.get('total_responses', 0)}
Bienestar global: {results.get('global_mean', 0):.2f}/6.00

El análisis revela los niveles de bienestar en las seis dimensiones de la escala de Ryff.
Se identificaron {len(results.get('clusters', []))} perfiles diferenciados de estudiantes.
        """

    def _generate_basic_recommendations(self, results: dict) -> list[str]:
        """Genera recomendaciones básicas sin IA."""
        recommendations = [
            "Fortalecer programas de bienestar en dimensiones con menor puntuación",
            "Implementar talleres de desarrollo personal",
            "Crear espacios de apoyo emocional para estudiantes",
            "Diseñar intervenciones diferenciadas por perfiles de estudiantes",
            "Realizar seguimiento periódico del bienestar estudiantil",
        ]
        return recommendations
