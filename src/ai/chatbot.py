"""
Chatbot inteligente para consultas sobre bienestar psicológico.
Utiliza Google Gemini para entender y responder preguntas en lenguaje natural.
"""

import json
from typing import Optional
from datetime import datetime

import google.generativeai as genai

from src.utils.logger import get_logger

logger = get_logger(__name__)


class WellbeingChatbot:
    """Chatbot para consultas sobre análisis de bienestar."""

    def __init__(self, config: dict):
        """
        Inicializa el chatbot.

        Args:
            config: Configuración del proyecto
        """
        self.config = config
        ai_config = config.get("ai", {})
        self.api_key = ai_config.get("api_key", "")
        self.model_name = ai_config.get("model", "gemini-3.6-flash")
        self.model = None
        self.conversation_history = []
        self.last_analysis = None

        if self.api_key:
            self._configure()

    def _configure(self):
        """Configura la conexión con Gemini."""
        try:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(
                model_name=self.model_name,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.7,
                    max_output_tokens=1000,
                )
            )
            logger.info(f"Chatbot configurado con {self.model_name}")
        except Exception as e:
            logger.error(f"Error al configurar chatbot: {e}")

    def load_analysis_results(self, results: dict):
        """
        Carga los resultados del último análisis para el chatbot.

        Args:
            results: Resultados del análisis
        """
        self.last_analysis = results
        logger.info("Resultados del análisis cargados en el chatbot")

    def chat(self, user_message: str) -> str:
        """
        Procesa un mensaje del usuario y genera una respuesta.

        Args:
            user_message: Mensaje del usuario

        Returns:
            Respuesta del chatbot
        """
        if not self.model:
            return self._fallback_response(user_message)

        # Construir contexto con los datos del análisis
        context = self._build_context()

        # Prompt del sistema
        system_prompt = f"""Eres un asistente inteligente especializado en análisis de bienestar psicológico 
estudiantil de la Universidad Santo Tomás. Tu nombre es "BienestarBot".

Tu tarea es responder preguntas sobre los datos de bienestar psicológico de los estudiantes 
usando la escala de Ryff (29 ítems, escala 1-6).

CONTEXTO DEL ANÁLISIS:
{context}

INSTRUCCIONES:
1. Responde en español de forma clara y concisa
2. Usa los datos reales del análisis cuando sea posible
3. Si no tienes información suficiente, indícalo
4. Puedes hacer recomendaciones basadas en los datos
5. Sé amigable y profesional
6. Si te preguntan por algo que no está en los datos, di que no tienes esa información

HISTORIAL DE CONVERSACIÓN:
{self._get_history_string()}

PREGUNTA DEL USUARIO: {user_message}

RESPUESTA:"""

        try:
            response = self.model.generate_content(system_prompt)
            answer = response.text

            # Guardar en historial
            self.conversation_history.append({
                "user": user_message,
                "bot": answer,
                "timestamp": datetime.now().isoformat()
            })

            # Mantener solo los últimos 10 intercambios
            if len(self.conversation_history) > 10:
                self.conversation_history = self.conversation_history[-10:]

            return answer

        except Exception as e:
            logger.error(f"Error en chatbot: {e}")
            return f"Lo siento, hubo un error al procesar tu pregunta. Por favor, intenta de nuevo."

    def _build_context(self) -> str:
        """Construye el contexto con los datos del análisis."""
        if not self.last_analysis:
            return "No hay datos de análisis disponibles."

        context_parts = []

        # Datos generales
        total = self.last_analysis.get("total_responses", 0)
        global_mean = self.last_analysis.get("global_mean", 0)
        global_std = self.last_analysis.get("global_std", 0)

        context_parts.append(f"Total de estudiantes encuestados: {total}")
        context_parts.append(f"Bienestar global promedio: {global_mean:.2f}/6.00 (DE: {global_std:.2f})")

        # Dimensiones
        dimensions = self.last_analysis.get("dimension_stats", [])
        if dimensions:
            context_parts.append("\nResultados por dimensión:")
            for dim in dimensions:
                name = dim.get("dimension", "")
                mean = dim.get("mean", 0)
                std = dim.get("std", 0)

                if mean >= 5:
                    level = "ALTO"
                elif mean >= 3.5:
                    level = "MEDIO"
                else:
                    level = "BAJO"

                context_parts.append(f"- {name}: {mean:.2f}/6.00 ({level})")

        # Dimensión más débil
        if dimensions:
            weakest = min(dimensions, key=lambda x: x.get("mean", 6))
            context_parts.append(f"\nDimensión más débil: {weakest.get('dimension', '')} ({weakest.get('mean', 0):.2f})")

        # Correlaciones
        correlations = self.last_analysis.get("correlations", [])
        if correlations:
            context_parts.append("\nPrincipales correlaciones:")
            for corr in correlations[:3]:
                var1 = corr.get("var1", "")
                var2 = corr.get("var2", "")
                r = corr.get("correlation", 0)
                sig = "significativa" if corr.get("significant", False) else "no significativa"
                context_parts.append(f"- {var1} y {var2}: r = {r:.3f} ({sig})")

        # Clustering
        clusters = self.last_analysis.get("clusters", [])
        if clusters:
            context_parts.append(f"\nPerfiles de estudiantes identificados: {len(clusters)}")
            for cluster in clusters:
                cid = cluster.get("id", 0)
                size = cluster.get("size", 0)
                pct = cluster.get("percentage", 0)
                label = cluster.get("label", "")
                context_parts.append(f"- Perfil {cid}: {size} estudiantes ({pct:.1f}%) - {label}")

        # Regresión
        regression = self.last_analysis.get("regression", {})
        if regression:
            r2 = regression.get("r_squared", 0)
            context_parts.append(f"\nModelo de regresión: R² = {r2:.4f}")

            factors = regression.get("factors", [])
            if factors:
                context_parts.append("Predictores más importantes:")
                for f in factors[:3]:
                    name = f.get("factor", "")
                    beta = f.get("std_coefficient", 0)
                    sig = "*" if f.get("significant", False) else ""
                    context_parts.append(f"- {name}: β = {beta:.3f}{sig}")

        return "\n".join(context_parts)

    def _get_history_string(self) -> str:
        """Convierte el historial a string."""
        if not self.conversation_history:
            return "Sin historial previo."

        history_str = ""
        for exchange in self.conversation_history[-5:]:
            history_str += f"Usuario: {exchange['user']}\n"
            history_str += f"Bot: {exchange['bot']}\n\n"

        return history_str

    def _fallback_response(self, user_message: str) -> str:
        """Respuesta cuando Gemini no está disponible."""
        # Respuestas predefinidas para preguntas comunes
        responses = {
            "hola": "¡Hola! Soy BienestarBot, tu asistente de análisis de bienestar psicológico. ¿En qué puedo ayudarte?",
            "adiós": "¡Hasta luego! Que tengas un excelente día.",
            "ayuda": "Puedo responder preguntas sobre:\n- Estadísticas de bienestar\n- Dimensiones evaluadas\n- Resultados por grupo\n- Recomendaciones\n\n¡Pregúntame lo que quieras!",
        }

        user_lower = user_message.lower().strip()

        for key, response in responses.items():
            if key in user_lower:
                return response

        return "Lo siento, no tengo acceso al modelo de IA en este momento. Por favor, configura la API key de Gemini en config.yaml."

    def get_suggested_questions(self) -> list[str]:
        """
        Retorna preguntas sugeridas basadas en los datos.

        Returns:
            Lista de preguntas sugeridas
        """
        suggestions = [
            "¿Cuál es el bienestar global de los estudiantes?",
            "¿Qué dimensión tiene el peor resultado?",
            "¿Cuántos estudiantes participaron?",
            "¿Qué dimensiones están más correlacionadas?",
            "¿Cuáles son los perfiles de estudiantes?",
            "¿Qué factores predicen el bienestar?",
            "Dame recomendaciones para mejorar",
            "Compara las dimensiones entre sí",
        ]

        # Agregar sugerencias específicas si hay datos
        if self.last_analysis:
            dimensions = self.last_analysis.get("dimension_stats", [])
            if dimensions:
                weakest = min(dimensions, key=lambda x: x.get("mean", 6))
                suggestions.append(
                    f"¿Por qué '{weakest.get('dimension', '')}' está bajo?"
                )

        return suggestions

    def clear_history(self):
        """Limpia el historial de conversación."""
        self.conversation_history = []
        logger.info("Historial de conversación limpiado")

    def get_conversation_history(self) -> list[dict]:
        """
        Obtiene el historial de conversación.

        Returns:
            Lista de intercambios
        """
        return self.conversation_history
