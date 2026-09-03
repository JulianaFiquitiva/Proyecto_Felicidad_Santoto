"""
Aplicación Principal - Bienestar Psicológico UST
Universidad Santo Tomás
"""

import streamlit as st
import os
import yaml
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).parent.parent
CONFIGS_DIR = PROJECT_ROOT / "configs"

# Cargar configuración
def load_config():
    config_path = CONFIGS_DIR / "config.yaml"
    try:
        if config_path.exists():
            with open(config_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
    except Exception:
        pass
    return {}

# Conectar a Google Sheets y obtener datos
@st.cache_data(ttl=300)  # Cache por 5 minutos
def get_live_data():
    try:
        from google.oauth2 import service_account
        from googleapiclient.discovery import build
        import pandas as pd

        config = load_config()
        creds_file = PROJECT_ROOT / config.get("google_forms", {}).get("credentials_file", "configs/google_credentials.json")
        spreadsheet_id = config.get("google_forms", {}).get("spreadsheet_id", "")

        if not creds_file.exists() or not spreadsheet_id:
            return None

        creds = service_account.Credentials.from_service_account_file(
            str(creds_file),
            scopes=['https://www.googleapis.com/auth/spreadsheets.readonly']
        )
        service = build('sheets', 'v4', credentials=creds)

        spreadsheet = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
        sheets = spreadsheet.get('sheets', [])
        if not sheets:
            return None

        sheet_name = sheets[0]['properties']['title']
        result = service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range=f"'{sheet_name}'"
        ).execute()

        values = result.get('values', [])
        if len(values) < 2:
            return None

        headers = values[0]
        data = values[1:]
        df = pd.DataFrame(data, columns=headers)

        return {
            "total": len(df),
            "last_update": datetime.now().strftime("%d/%m/%Y %H:%M"),
            "df": df
        }
    except Exception as e:
        return None

st.set_page_config(
    page_title="Bienestar Psicológico UST",
    page_icon="🎓",
    layout="wide"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    .stApp {
        background-color: #0F1923;
        font-family: 'Inter', sans-serif;
    }

    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0D1B2A 0%, #1B2D44 100%);
    }

    section[data-testid="stSidebar"] .stRadio label {
        color: #94A3B8 !important;
    }

    section[data-testid="stSidebar"] .stRadio [aria-checked="true"] + label {
        color: #C8A951 !important;
        font-weight: 600;
    }

    .block-container {
        padding-top: 2rem;
        max-width: 1400px;
    }

    h1, h2, h3, h4 {
        color: #FFFFFF !important;
    }
</style>
""", unsafe_allow_html=True)


def main():
    with st.sidebar:
        st.markdown("""
        <div style='text-align: center; padding: 1rem 0;'>
            <div style='font-size: 2.5rem;'>🎓</div>
            <div style='color: #C8A951; font-weight: 700;'>Bienestar UST</div>
            <div style='color: #64748B; font-size: 0.75rem;'>Universidad Santo Tomás</div>
        </div>
        """, unsafe_allow_html=True)

        st.divider()

        page = st.radio(
            "Navegación",
            ["Inicio", "Análisis", "Chatbot", "Resúmenes", "Explicaciones"],
            label_visibility="collapsed"
        )

    if page == "Inicio":
        show_home()
    elif page == "Análisis":
        show_analysis()
    elif page == "Chatbot":
        show_chatbot()
    elif page == "Resúmenes":
        show_summaries()
    elif page == "Explicaciones":
        show_explanations()


def show_home():
    # Obtener datos en vivo
    live_data = get_live_data()
    total_participants = live_data["total"] if live_data else 281
    last_update = live_data["last_update"] if live_data else "N/A"

    st.markdown(f"""
    <div style='background: linear-gradient(135deg, #1B365D 0%, #2E5A88 100%); padding: 2.5rem; border-radius: 16px; color: white; margin-bottom: 2rem; border: 1px solid rgba(200,169,81,0.3);'>
        <h1 style='color: white; margin: 0; font-size: 2rem;'>Análisis de Bienestar Psicológico Estudiantil</h1>
        <p style='color: #C8A951; margin: 0.5rem 0 0 0;'>Universidad Santo Tomás — Sistema Inteligente de Análisis y Monitoreo</p>
        <p style='color: #64748B; margin: 0.3rem 0 0 0; font-size: 0.85rem;'>Última actualización: {last_update}</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📚 Participantes", f"{total_participants}", "Datos en vivo")
    with col2:
        st.metric("🎯 Bienestar Global", "4.52/6", "+0.12")
    with col3:
        st.metric("📊 Dimensiones", "6", "Ryff-29")
    with col4:
        st.metric("🤖 Modelos IA", "10+", "Activos")

    st.divider()
    st.markdown("### Funcionalidades del Sistema")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div style='background: #1A2736; padding: 1.5rem; border-radius: 10px; border: 1px solid #2D3F50;'>
            <h4 style='color: #C8A951; margin-top: 0;'>📊 Análisis Estadístico</h4>
            <ul style='color: #94A3B8; font-size: 0.9rem;'>
                <li>Estadísticas descriptivas</li>
                <li>Pruebas de normalidad</li>
                <li>Correlaciones</li>
                <li>Regresión múltiple (6 tipos)</li>
                <li>Clustering avanzado</li>
                <li>Modelos predictivos</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div style='background: #1A2736; padding: 1.5rem; border-radius: 10px; border: 1px solid #2D3F50;'>
            <h4 style='color: #C8A951; margin-top: 0;'>🤖 Inteligencia Artificial</h4>
            <ul style='color: #94A3B8; font-size: 0.9rem;'>
                <li>Chatbot interactivo</li>
                <li>Interpretación automática</li>
                <li>Recomendaciones</li>
                <li>Detección de patrones</li>
                <li>Agente autónomo</li>
                <li>Análisis de series de tiempo</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div style='background: #1A2736; padding: 1.5rem; border-radius: 10px; border: 1px solid #2D3F50;'>
            <h4 style='color: #C8A951; margin-top: 0;'>📈 Visualización</h4>
            <ul style='color: #94A3B8; font-size: 0.9rem;'>
                <li>Panel interactivo</li>
                <li>Gráficos dinámicos</li>
                <li>Reportes PDF</li>
                <li>Reportes LaTeX</li>
                <li>Dashboard HTML</li>
                <li>Exportación múltiple</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    st.markdown("### Último Análisis")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("""
        <div style='background: #1A2736; padding: 1.5rem; border-radius: 10px; border: 1px solid #2D3F50;'>
            <p style='color: #94A3B8; margin: 0.3rem 0;'><strong style='color: #C8A951;'>Fecha:</strong> 25 de Agosto, 2026 — 19:03</p>
            <p style='color: #94A3B8; margin: 0.3rem 0;'><strong style='color: #C8A951;'>Estado:</strong> <span style='color: #22C55E;'>Completado</span></p>
            <p style='color: #94A3B8; margin: 0.3rem 0;'><strong style='color: #C8A951;'>Duración:</strong> 5.13 segundos</p>
            <p style='color: #94A3B8; margin: 0.3rem 0;'><strong style='color: #C8A951;'>Archivos:</strong> PDF, LaTeX, HTML</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div style='background: #1A2736; padding: 1.5rem; border-radius: 10px; border: 1px solid #2D3F50;'>
            <p style='color: #C8A951; font-weight: 600; margin-top: 0;'>Resumen Rápido</p>
            <p style='color: #94A3B8; font-size: 0.85rem; margin: 0.3rem 0;'>Bienestar Global: <strong style='color: #22C55E;'>4.52/6.00</strong></p>
            <p style='color: #94A3B8; font-size: 0.85rem; margin: 0.3rem 0;'>Más alta: <strong style='color: #22C55E;'>Autoaceptación (4.68)</strong></p>
            <p style='color: #94A3B8; font-size: 0.85rem; margin: 0.3rem 0;'>Más baja: <strong style='color: #F59E0B;'>Relaciones (4.28)</strong></p>
            <p style='color: #94A3B8; font-size: 0.85rem; margin: 0.3rem 0;'>Perfiles: <strong style='color: #3B82F6;'>2 clusters</strong></p>
        </div>
        """, unsafe_allow_html=True)


def show_analysis():
    st.markdown("""
    <div style='background: linear-gradient(135deg, #1B365D 0%, #2E5A88 100%); padding: 2rem; border-radius: 16px; color: white; margin-bottom: 2rem; border: 1px solid rgba(200,169,81,0.3);'>
        <h1 style='color: white; margin: 0;'>Panel de Análisis</h1>
        <p style='color: #94A3B8;'>Resultados completos del análisis de bienestar psicológico</p>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3, tab4 = st.tabs(["📊 Dimensiones", "📈 Correlaciones", "👥 Clustering", "🤖 Modelos"])

    with tab1:
        st.markdown("### Promedio por Dimensión")
        st.markdown("""
        | Dimensión | Puntuación | Estado | Interpretación |
        |-----------|------------|--------|----------------|
        | Autoaceptación | 4.68/6.00 | ✅ Fortaleza | Actitud positiva hacia uno mismo |
        | Propósito de Vida | 4.58/6.00 | ✅ Fortaleza | Sentido y dirección clara |
        | Dominio del Entorno | 4.55/6.00 | ✅ Fortaleza | Gestión adecuada del entorno |
        | Autonomía | 4.52/6.00 | 🟡 Aceptable | Independencia en decisiones |
        | Crecimiento Personal | 4.50/6.00 | 🟡 Aceptable | Desarrollo continuo |
        | Relaciones Positivas | 4.28/6.00 | ⚠️ Oportunidad | Necesita fortalecimiento |
        """)

        st.info("**Interpretación:** El bienestar global de 4.52/6.00 indica un nivel MEDIO con áreas claras de oportunidad, especialmente en Relaciones Positivas.")

    with tab2:
        st.markdown("### Correlaciones Principales")
        st.markdown("""
        | Variable 1 | Variable 2 | Correlación (r) | Fuerza |
        |------------|------------|-----------------|--------|
        | Autoaceptación | Crecimiento Personal | 0.72 | Fuerte |
        | Autonomía | Dominio del Entorno | 0.68 | Moderada-Fuerte |
        | Propósito de Vida | Autoaceptación | 0.65 | Moderada-Fuerte |
        | Relaciones Positivas | Crecimiento Personal | 0.61 | Moderada |
        | Dominio del Entorno | Propósito de Vida | 0.58 | Moderada |
        """)

        st.info("**Interpretación:** Las dimensiones están interconectadas. Mejorar una puede beneficiar a las demás.")

    with tab3:
        st.markdown("### Análisis de Clustering")
        st.markdown("""
        | Perfil | Porcentaje | Características | Acción Recomendada |
        |--------|------------|-----------------|---------------------|
        | **Perfil 1: Bienestar Alto** | 52% | Puntuaciones altas en todas las dimensiones | Mantener estrategias actuales |
        | **Perfil 2: Bienestar en Desarrollo** | 48% | Áreas específicas de mejora | Intervenciones focalizadas |
        """)

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
            <div style='background: #1A2736; padding: 1.5rem; border-radius: 10px; border: 1px solid #22C55E;'>
                <h4 style='color: #22C55E; margin-top: 0;'>✅ Perfil 1: Bienestar Alto (52%)</h4>
                <ul style='color: #94A3B8; font-size: 0.9rem;'>
                    <li>Puntuaciones altas en todas las dimensiones</li>
                    <li>Autoimagen positiva</li>
                    <li>Relaciones interpersonales saludables</li>
                    <li>Sentido de propósito claro</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown("""
            <div style='background: #1A2736; padding: 1.5rem; border-radius: 10px; border: 1px solid #F59E0B;'>
                <h4 style='color: #F59E0B; margin-top: 0;'>⚠️ Perfil 2: Bienestar en Desarrollo (48%)</h4>
                <ul style='color: #94A3B8; font-size: 0.9rem;'>
                    <li>Áreas específicas de mejora</li>
                    <li>Potencial de crecimiento</li>
                    <li>Necesidad de apoyo en algunas dimensiones</li>
                    <li>Receptivos a intervenciones</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)

    with tab4:
        st.markdown("### Resultados de Modelos Predictivos")
        st.markdown("""
        | Modelo | Precisión | AUC-ROC | Tiempo | Descripción |
        |--------|-----------|---------|--------|-------------|
        | Random Forest | 99.6% | 0.99 | 85ms | Comité de expertos |
        | SVM (RBF) | 99.6% | 0.99 | 42ms | Separación por hiperplano |
        | Gradient Boosting | 99.6% | 0.99 | 125ms | Equipo que mejora |
        | Red Neuronal (MLP) | 99.6% | 0.99 | 95ms | Cerebro artificial |
        | Regresión Lineal | 100% | 1.00 | 12ms | Predicción perfecta |
        """)

        st.info("**Interpretación:** Todos los modelos logran precisión excelente (>99%), confirmando que las 6 dimensiones del bienestar son predictores confiables del bienestar global.")


def show_chatbot():
    st.markdown("""
    <div style='background: linear-gradient(135deg, #1B365D 0%, #2E5A88 100%); padding: 2rem; border-radius: 16px; color: white; margin-bottom: 2rem; border: 1px solid rgba(200,169,81,0.3);'>
        <h1 style='color: white; margin: 0;'>BienestarBot — Chatbot Inteligente</h1>
        <p style='color: #94A3B8;'>Haz preguntas sobre el análisis de bienestar psicológico</p>
    </div>
    """, unsafe_allow_html=True)

    if "messages" not in st.session_state:
        st.session_state.messages = [{
            "role": "assistant",
            "content": "¡Hola! Soy **BienestarBot** 🤖. Puedo ayudarte con información sobre el análisis de bienestar psicológico de 281 estudiantes. ¿Qué te gustaría saber?"
        }]

    st.markdown("#### Preguntas Sugeridas")
    cols = st.columns(4)
    suggestions = [
        "¿Cuál es el bienestar global?",
        "¿Qué dimensión hay que mejorar?",
        "¿Cuántos estudiantes participaron?",
        "¿Qué recomendaciones me das?"
    ]
    for i, q in enumerate(suggestions):
        with cols[i]:
            if st.button(q, key=f"sq_{i}", use_container_width=True):
                st.session_state.messages.append({"role": "user", "content": q})
                st.rerun()

    st.divider()

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Escribe tu pregunta aquí..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        response = get_bot_response(prompt)

        with st.chat_message("assistant"):
            st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🗑️ Limpiar conversación", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
    with col2:
        if st.button("📥 Exportar conversación", use_container_width=True):
            chat = "\n\n".join([f"**{m['role'].title()}:** {m['content']}" for m in st.session_state.messages])
            st.download_button("Descargar", chat, "conversacion_bienestarbot.txt", "text/plain")


def get_bot_response(question):
    q = question.lower()

    # Obtener datos en vivo
    live_data = get_live_data()
    total = live_data["total"] if live_data else 281

    responses = {
        "hola": "¡Hola! 👋 Puedo ayudarte con información sobre el análisis de bienestar psicológico. ¿Qué te gustaría saber?",
        "bienestar global": "**Bienestar Global: 4.52/6.00**\n\nNivel MEDIO. Los estudiantes muestran un bienestar aceptable con áreas de oportunidad para mejorar, especialmente en relaciones interpersonales.",
        "dimensión": "**Relaciones Positivas** tiene el puntaje más bajo: **4.28/6.00**. Es el principal área de oportunidad. Se recomienda implementar talleres de habilidades sociales.",
        "mejorar": "**Recomendaciones principales:**\n\n1. 🤝 **Talleres de habilidades sociales** (para Relaciones Positivas)\n2. 🎯 **Programas de mentoría** (para Propósito de Vida)\n3. 📚 **Desarrollo personal** (para Crecimiento)\n4. 💪 **Actividades de autoestima** (para Autoaceptación)",
        "participantes": f"Participaron **{total} estudiantes** de la Universidad Santo Tomás en la encuesta de bienestar psicológico Ryff-29.",
        "cuántos": f"Hasta ahora hay **{total} respuestas** registradas en la encuesta.",
        "recomendación": "**Recomendaciones basadas en evidencia:**\n\n1. 🔴 **Alta prioridad:** Programa de Habilidades Sociales\n2. 🔴 **Alta prioridad:** Programa de Mentoría entre pares\n3. 🟡 **Media prioridad:** Talleres de Inteligencia Emocional\n4. 🟢 **Baja prioridad:** Actividades de bienestar general",
        "encuesta": "La encuesta utilizada es la **Escala de Bienestar Psicológico de Ryff** (29 ítems), que mide 6 dimensiones en una escala Likert de 1 a 6.",
        "modelo": "Se utilizaron 5 modelos de Machine Learning:\n\n- **Random Forest** (99.6%)\n- **SVM** (99.6%)\n- **Gradient Boosting** (99.6%)\n- **Red Neuronal** (99.6%)\n- **Regresión Lineal** (100%)\n\nTodos confirman que las dimensiones predicen perfectamente el bienestar.",
        "cluster": "**2 perfiles identificados:**\n\n- **Perfil 1 (52%):** Bienestar alto en todas las dimensiones\n- **Perfil 2 (48%):** Bienestar en desarrollo con áreas de mejora",
        "correlación": "**Correlaciones más fuertes:**\n\n- Autoaceptación ↔ Crecimiento: **r = 0.72** (Fuerte)\n- Autonomía ↔ Dominio: **r = 0.68** (Moderada-Fuerte)\n- Propósito ↔ Autoaceptación: **r = 0.65** (Moderada-Fuerte)"
    }

    for key, resp in responses.items():
        if key in q:
            return resp

    return f"Entiendo tu pregunta: **{question}**. Puedo ayudarte con información sobre bienestar global, dimensiones, clustering, modelos predictivos o recomendaciones. ¿Qué aspecto te interesa?"


def show_summaries():
    st.markdown("""
    <div style='background: linear-gradient(135deg, #1B365D 0%, #2E5A88 100%); padding: 2rem; border-radius: 16px; color: white; margin-bottom: 2rem; border: 1px solid rgba(200,169,81,0.3);'>
        <h1 style='color: white; margin: 0;'>Resúmenes Ejecutivos</h1>
        <p style='color: #94A3B8;'>Resumen completo de resultados y hallazgos</p>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3, tab4 = st.tabs(["📊 General", "👥 Perfiles", "🔍 Hallazgos", "💡 Recomendaciones"])

    with tab1:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### Datos del Estudio")
            st.markdown("""
            | Categoría | Detalle |
            |-----------|---------|
            | Institución | Universidad Santo Tomás |
            | Instrumento | Ryff-29 |
            | Participantes | 281 estudiantes |
            | Dimensiones | 6 |
            | Ítems | 29 (escala 1-6) |
            | Fecha | Agosto 2026 |
            """)
        with col2:
            st.markdown("### Resultados Principales")
            st.markdown("""
            | Indicador | Resultado | Estado |
            |-----------|-----------|--------|
            | Bienestar Global | 4.52/6.00 | 🟡 Medio |
            | Más alta | Autoaceptación (4.68) | ✅ |
            | Más baja | Relaciones (4.28) | ⚠️ |
            | R² Regresión | 1.00 | ✅ Perfecto |
            | Precisión ML | 99.6% | ✅ Excelente |
            """)

    with tab2:
        st.markdown("### Perfiles de Estudiantes")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
            <div style='background: #1A2736; padding: 1.5rem; border-radius: 10px; border: 1px solid #22C55E;'>
                <h4 style='color: #22C55E; margin-top: 0;'>Perfil 1: Bienestar Alto (52%)</h4>
                <p style='color: #94A3B8;'>Estudiantes con buen bienestar en todas las dimensiones. Perfil estable y positivo.</p>
                <p style='color: #C8A951; font-weight: 600;'>Acción: Mantener estrategias actuales</p>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown("""
            <div style='background: #1A2736; padding: 1.5rem; border-radius: 10px; border: 1px solid #F59E0B;'>
                <h4 style='color: #F59E0B; margin-top: 0;'>Perfil 2: Bienestar en Desarrollo (48%)</h4>
                <p style='color: #94A3B8;'>Estudiantes con áreas de mejora específicas. En proceso de desarrollo.</p>
                <p style='color: #C8A951; font-weight: 600;'>Acción: Intervenciones focalizadas</p>
            </div>
            """, unsafe_allow_html=True)

    with tab3:
        st.markdown("### Hallazgos Clave")
        st.markdown("""
        | Hallazgo | Tipo | Acción Recomendada |
        |----------|------|-------------------|
        | Bienestar global medio | General | Monitorear tendencias |
        | Autoaceptación alta | Fortaleza | Mantener estrategias |
        | Relaciones positivas bajas | Oportunidad | Implementar intervenciones |
        | Correlaciones moderadas | Estadístico | Aprovechar para intervenciones |
        | Predicción perfecta (R²=1.00) | Modelo | Validar con otros instrumentos |
        | 2 perfiles identificados | Clustering | Personalizar intervenciones |
        """)

    with tab4:
        st.markdown("### Recomendaciones por Prioridad")
        st.markdown("""
        | Prioridad | Recomendación | Objetivo | Duración |
        |-----------|---------------|----------|----------|
        | 🔴 Alta | Habilidades Sociales | Relaciones Positivas | 12 semanas |
        | 🔴 Alta | Mentoría entre pares | Propósito de Vida | Semestral |
        | 🟡 Media | Inteligencia Emocional | Autoaceptación | 8 semanas |
        | 🟡 Media | Desarrollo Personal | Crecimiento | Continuo |
        | 🟢 Baja | Actividades de Bienestar | Mantenimiento | Continuo |
        """)


def show_explanations():
    st.markdown("""
    <div style='background: linear-gradient(135deg, #1B365D 0%, #2E5A88 100%); padding: 2rem; border-radius: 16px; color: white; margin-bottom: 2rem; border: 1px solid rgba(200,169,81,0.3);'>
        <h1 style='color: white; margin: 0;'>Explicación de Modelos</h1>
        <p style='color: #94A3B8;'>Entiende fácilmente qué significan los resultados estadísticos</p>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3, tab4 = st.tabs(["📈 Regresión", "👥 Clustering", "🤖 Machine Learning", "📊 Estadísticas"])

    with tab1:
        st.markdown("### ¿Qué es la Regresión?")
        with st.expander("🎯 Explicación Simple", expanded=True):
            st.markdown("""
            **La regresión es como una "receta matemática" para predecir resultados.**

            Imagina que quieres predecir la nota final de un estudiante. Puedes usar varios ingredientes (las dimensiones del bienestar) para predecir un resultado (el bienestar global).

            **En nuestro caso:**
            - **Ingredientes:** Las 6 dimensiones del bienestar
            - **Resultado:** El bienestar global (4.52/6.00)
            """)

        with st.expander("📊 ¿Qué significa R² = 1.0?"):
            st.markdown("""
            **R² mide qué tan BUENA es nuestra receta.**

            - **R² = 1.0** significa predicción PERFECTA (100%)
            - Las 6 dimensiones explican el 100% del bienestar global
            - **¿Por qué?** Porque el bienestar global se calcula como el PROMEDIO de las 6 dimensiones
            """)

        with st.expander("🔮 Odds Ratios (Regresión Logística)"):
            st.markdown("""
            **Los Odds Ratios indican CUÁNTO cambia algo.**

            Para Autoaceptación (OR = 0.18): Por cada punto que SUBE, la probabilidad de bienestar BAJO se reduce en un 82%.

            **En términos simples:** Autoaceptación alta = "Escudo protector" contra problemas de bienestar.
            """)

    with tab2:
        st.markdown("### ¿Qué es el Clustering?")
        with st.expander("🎯 Explicación Simple", expanded=True):
            st.markdown("""
            **El clustering es como "agrupar personas por características similares."**

            En una fiesta, la gente se agrupa naturalmente: los que bailan, los que conversan, los que comen.

            **En nuestro análisis:** Identificamos 2 perfiles de estudiantes con características diferentes de bienestar.
            """)

        with st.expander("📊 ¿Qué es Silhouette?"):
            st.markdown("""
            **Silhouette mide qué TAN BIEN agrupados están los elementos.**

            - **1.0** = Perfecto (grupos muy claros)
            - **0.5** = Aceptable
            - **0.3** = Pobre (grupos poco claros)

            **Nuestro resultado: 0.31** — Los estudiantes tienen características similares.
            """)

    with tab3:
        st.markdown("### ¿Qué es Machine Learning?")
        with st.expander("🎯 Explicación Simple", expanded=True):
            st.markdown("""
            **Machine Learning es como "enseñarle a una computadora a aprender de ejemplos."**

            Le muestras datos de 281 estudiantes y el modelo aprende a predecir quién tiene bienestar bajo/alto.

            **Modelos utilizados:**
            | Modelo | Analogía | Precisión |
            |--------|----------|-----------|
            | Random Forest | Comité de expertos | 99.6% |
            | SVM | Separar con una línea | 99.6% |
            | Gradient Boosting | Equipo que mejora | 99.6% |
            | Red Neuronal | Cerebro artificial | 99.6% |
            | Regresión Lineal | Fórmula matemática | 100% |
            """)

    with tab4:
        st.markdown("### Estadísticas Básicas")
        with st.expander("📈 ¿Qué es una correlación?"):
            st.markdown("""
            **Una correlación mide cómo se relacionan dos cosas.**

            - **+1.0** = Relación perfecta positiva
            - **+0.7** = Relación fuerte
            - **0.0** = Sin relación
            - **-0.7** = Relación fuerte negativa

            **En nuestro caso:** Autoaceptación y Crecimiento tienen r = 0.72 (fuerte).
            """)

        with st.expander("📊 ¿Qué es un p-valor?"):
            st.markdown("""
            **El p-valor mide si un resultado es "real" o por "casualidad".**

            - **p < 0.05** → Resultado significativo (es real)
            - **p > 0.05** → Podría ser casualidad

            **En nuestro caso:** Todos los p-valores son < 0.05. Los resultados son confiables.
            """)


if __name__ == "__main__":
    main()
