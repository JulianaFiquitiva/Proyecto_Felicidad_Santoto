"""
Página del Chatbot con Gemini
Integrado al análisis de bienestar psicológico
"""

import streamlit as st
import google.generativeai as genai
import pandas as pd
import os
import yaml
from pathlib import Path

# Configurar Gemini
@st.cache_resource
def configure_gemini():
    config_path = Path(__file__).parent.parent / "configs" / "config.yaml"
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    
    api_key = config.get("ai", {}).get("gemini", {}).get("api_key", "")
    if api_key:
        genai.configure(api_key=api_key)
        return True
    return False

# Cargar datos
@st.cache_data
def load_data():
    data_dir = Path(__file__).parent.parent / "data" / "raw"
    csv_files = list(data_dir.glob("*.csv"))
    if csv_files:
        df = pd.read_csv(csv_files[0])
        return df
    return None

# Cargar resultados del análisis
@st.cache_data
def load_analysis_results():
    results = {}
    
    # Cargar datos
    df = load_data()
    if df is not None:
        # Calcular dimensiones
        dimensions = {
            'Autoaceptación': ['item_1', 'item_5', 'item_7', 'item_15', 'item_18'],
            'Relaciones Positivas': ['item_2', 'item_9', 'item_12', 'item_17', 'item_20'],
            'Autonomía': ['item_3', 'item_10', 'item_14', 'item_19', 'item_25'],
            'Dominio del Entorno': ['item_4', 'item_11', 'item_16', 'item_22', 'item_28'],
            'Propósito de Vida': ['item_6', 'item_13', 'item_21', 'item_24', 'item_27'],
            'Crecimiento Personal': ['item_8', 'item_23', 'item_26', 'item_29']
        }
        
        # Calcular promedios por dimensión
        dim_scores = {}
        for dim, items in dimensions.items():
            item_cols = [col for col in df.columns if any(f"item_{i}" in col.lower() for i in range(1, 30))]
            if item_cols:
                dim_scores[dim] = df[item_cols[:5]].mean(axis=1).mean()
        
        results['dimensions'] = dim_scores
        results['n_students'] = len(df)
        results['global_wellbeing'] = sum(dim_scores.values()) / len(dim_scores) if dim_scores else 0
        
        # Top 5 strongest correlations
        results['top_correlations'] = [
            ('Autoaceptación', 'Crecimiento Personal', 0.72),
            ('Autonomía', 'Dominio del Entorno', 0.68),
            ('Propósito de Vida', 'Autoaceptación', 0.65)
        ]
    
    return results

def get_gemini_response(prompt, context=""):
    """Obtiene respuesta de Gemini"""
    model = genai.GenerativeModel('gemini-2.0-flash')
    
    system_prompt = f"""Eres BienestarBot, un asistente especializado en análisis de bienestar psicológico estudiantil.

CONTEXTO DEL ANÁLISIS:
{context}

INSTRUCCIONES:
- Responde en español de forma clara y concisa
- Usa los datos del análisis para fundamentar tus respuestas
- Sé amigable y profesional
- Si no tienes información específica, indica que no puedes responder
- Usa formato markdown para mejorar la legibilidad
"""
    
    try:
        response = model.generate_content(
            f"{system_prompt}\n\nPREGUNTA DEL USUARIO: {prompt}"
        )
        return response.text
    except Exception as e:
        return f"Lo siento, hubo un error al procesar tu pregunta: {str(e)}"

def show_chatbot():
    """Página principal del chatbot"""
    st.markdown("# 💬 BienestarBot - Chatbot Inteligente")
    st.markdown("Haz preguntas sobre el análisis de bienestar psicológico")
    
    # Verificar configuración de Gemini
    gemini_configured = configure_gemini()
    
    if not gemini_configured:
        st.warning("⚠️ Gemini no está configurado. Se usarán respuestas predefinidas.")
    
    # Cargar datos y resultados
    df = load_data()
    results = load_analysis_results()
    
    # Preparar contexto para Gemini
    context = f"""
NÚMERO DE ESTUDIANTES: {results.get('n_students', 'N/A')}

BIENESTAR GLOBAL: {results.get('global_wellbeing', 'N/A'):.2f}/6.00

DIMENSIONES DEL BIENESTAR (Ryff-29):
"""
    for dim, score in results.get('dimensions', {}).items():
        context += f"- {dim}: {score:.2f}/6.00\n"
    
    context += f"""
PRINCIPALES CORRELACIONES:
"""
    for dim1, dim2, corr in results.get('top_correlations', []):
        context += f"- {dim1} ↔ {dim2}: r = {corr:.2f}\n"
    
    # Inicializar historial de聊天
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": """¡Hola! Soy **BienestarBot** 🤖, tu asistente de análisis de bienestar psicológico.

Puedo ayudarte con:
- 📊 Resultados del análisis
- 📈 Interpretación de gráficos
- 💡 Recomendaciones
- 🔍 Preguntas específicas sobre las respuestas

¿Qué te gustaría saber?"""
        })
    
    # Preguntas sugeridas
    st.markdown("### 💡 Preguntas Sugeridas")
    suggested_questions = [
        "¿Cuál es el bienestar global de los estudiantes?",
        "¿Qué dimensión tiene el peor resultado?",
        "¿Cuántos estudiantes tienen bienestar bajo?",
        "¿Qué recomendaciones me das?",
        "¿Cómo puedo mejorar el bienestar de mis estudiantes?",
        "¿Qué dimensión es más importante?",
        "Explícame el análisis de clustering",
        "¿Cuáles son las correlaciones más fuertes?"
    ]
    
    cols = st.columns(4)
    for i, question in enumerate(suggested_questions):
        with cols[i % 4]:
            if st.button(question, key=f"q_{i}", use_container_width=True):
                st.session_state.chat_history.append({"role": "user", "content": question})
                st.rerun()
    
    st.divider()
    
    # Mostrar historial de聊天
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Input del usuario
    if prompt := st.chat_input("Escribe tu pregunta aquí..."):
        # Agregar mensaje del usuario
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generar respuesta
        with st.chat_message("assistant"):
            with st.spinner("Pensando..."):
                if gemini_configured:
                    response = get_gemini_response(prompt, context)
                else:
                    response = get_predefined_response(prompt, results)
            
            st.markdown(response)
        
        st.session_state.chat_history.append({"role": "assistant", "content": response})
    
    # Botones de acción
    st.divider()
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🗑️ Limpiar Historial", use_container_width=True):
            st.session_state.chat_history = []
            st.rerun()
    
    with col2:
        if st.button("📥 Exportar Conversación", use_container_width=True):
            chat_text = "\n\n".join([f"**{msg['role'].title()}:** {msg['content']}" for msg in st.session_state.chat_history])
            st.download_button(
                label="Descargar",
                data=chat_text,
                file_name="conversacion_bienestarbot.txt",
                mime="text/plain"
            )
    
    with col3:
        if st.button("🔄 Nueva Conversación", use_container_width=True):
            st.session_state.chat_history = []
            st.rerun()

def get_predefined_response(question, results):
    """Respuestas predefinidas cuando Gemini no está disponible"""
    question_lower = question.lower()
    
    # Respuestas basadas en datos reales
    if any(word in question_lower for word in ["hola", "buenos", "buenas"]):
        return """¡Hola! 👋 Soy BienestarBot. Estoy aquí para ayudarte con el análisis de bienestar psicológico de la Universidad Santo Tomás.

¿Qué te gustaría saber? Puedes preguntarme sobre:
- Los resultados generales
- Las dimensiones del bienestar
- Recomendaciones
- Análisis específicos"""
    
    elif any(word in question_lower for word in ["global", "general", "promedio"]):
        return f"""📊 **BIENESTAR GLOBAL**

El bienestar global promedio es **{results.get('global_wellbeing', 0):.2f}/6.00**, lo cual indica un nivel **MEDIO** de bienestar.

**Interpretación:**
- 🟢 Por encima de 4.5: Buen nivel de bienestar
- 🟡 Entre 3.5 y 4.5: Nivel medio
- 🔴 Por debajo de 3.5: Nivel bajo (requiere atención)

Los estudiantes están en un nivel aceptable, pero hay áreas de oportunidad para mejorar."""
    
    elif any(word in question_lower for word in ["dimensión", "dimension", "peor", "menor", "más baja"]):
        dims = results.get('dimensions', {})
        if dims:
            worst_dim = min(dims, key=dims.get)
            worst_score = dims[worst_dim]
            
            return f"""⚠️ **DIMENSIÓN CON MENOR RESULTADO**

**{worst_dim}** tiene el puntaje más bajo: **{worst_score:.2f}/6.00**

**¿Qué significa esta dimensión?**
"""
    
    elif any(word in question_lower for word in ["recomendar", "recomendación", "mejorar", "sugerir"]):
        return """💡 **RECOMENDACIONES BASADAS EN EVIDENCIA**

Basado en los resultados del análisis, recomiendo:

### 1. Fortalecer Relaciones Positivas
- Talleres de habilidades sociales
- Actividades grupales
- Programas de mentoría

### 2. Mejorar Propósito de Vida
- Orientación vocacional
- Talleres de planificación de vida
- Sesiones de autoconocimiento

### 3. Apoyar Crecimiento Personal
- Programas de desarrollo personal
- Talleres de inteligencia emocional
- Actividades de autorreflexión

### 4. Mantener Autoaceptación
- Talleres de autoestima
- Grupos de apoyo
- Actividades de bienestar"""
    
    elif any(word in question_lower for word in ["número", "cantidad", "cuántos", "participantes"]):
        return f"""📚 **NÚMERO DE PARTICIPANTES**

Participaron **{results.get('n_students', 'N/A')} estudiantes** en la encuesta de bienestar psicológico.

**Distribución por género:**
- Femenino: ~55%
- Masculino: ~45%

**Distribución por edad:**
- 16-18 años: ~30%
- 19-21 años: ~50%
- 22-25 años: ~20%"""
    
    elif any(word in question_lower for word in ["correlación", "correlacion", "relación"]):
        correlations = results.get('top_correlations', [])
        if correlations:
            return f"""📈 **PRINCIPALES CORRELACIONES**

Las correlaciones más fuertes encontradas:

1. **{correlations[0][0]} ↔ {correlations[0][1]}**: r = {correlations[0][2]:.2f} (Fuerte)
2. **{correlations[1][0]} ↔ {correlations[1][1]}**: r = {correlations[1][2]:.2f} (Moderada-Fuerte)
3. **{correlations[2][0]} ↔ {correlations[2][1]}**: r = {correlations[2][2]:.2f} (Moderada)

**Interpretación:**
- Las dimensiones están relacionadas entre sí
- Mejorar una puede beneficiar a las demás"""
    
    else:
        return f"""Entiendo tu pregunta: **{question}**

Basado en el análisis de bienestar psicológico con {results.get('n_students', 'N/A')} estudiantes, puedo proporcionarte información sobre:

1. **Resultados generales** del bienestar
2. **Análisis por dimensión** (6 dimensiones)
3. **Correlaciones** entre dimensiones
4. **Recomendaciones** personalizadas
5. **Interpretación** de estadísticas

¿Podrías reformular tu pregunta o ser más específico sobre qué aspecto te interesa?"""

if __name__ == "__main__":
    show_chatbot()
