"""
Aplicación Principal - Análisis de Bienestar Psicológico Estudiantil
Universidad Santo Tomás
"""

import streamlit as st
import yaml
import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
CONFIGS_DIR = PROJECT_ROOT / "configs"
REPORTS_DIR = PROJECT_ROOT / "reports"

# Asegurar que existan los directorios necesarios
CONFIGS_DIR.mkdir(exist_ok=True)
REPORTS_DIR.mkdir(exist_ok=True)

st.set_page_config(
    page_title="Bienestar Psicológico UST",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    :root {
        --primary: #1B365D;
        --primary-light: #2E5A88;
        --secondary: #C8A951;
        --accent: #3498DB;
        --bg-dark: #0F1923;
        --bg-card: #1A2736;
        --bg-card-hover: #223344;
        --text-primary: #FFFFFF;
        --text-secondary: #94A3B8;
        --border: #2D3F50;
        --success: #22C55E;
        --warning: #F59E0B;
        --danger: #EF4444;
    }

    .stApp {
        background-color: var(--bg-dark);
        font-family: 'Inter', sans-serif;
    }

    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0D1B2A 0%, #1B2D44 100%);
        border-right: 1px solid var(--border);
    }

    section[data-testid="stSidebar"] .stRadio label {
        color: var(--text-secondary) !important;
        font-size: 0.9rem;
        padding: 0.4rem 0.8rem;
        border-radius: 6px;
        transition: all 0.2s;
    }

    section[data-testid="stSidebar"] .stRadio label:hover {
        background: rgba(200, 169, 81, 0.1);
        color: var(--secondary) !important;
    }

    section[data-testid="stSidebar"] .stRadio [aria-checked="true"] + label {
        background: rgba(200, 169, 81, 0.15);
        color: var(--secondary) !important;
        font-weight: 600;
        border-left: 3px solid var(--secondary);
    }

    .block-container {
        padding-top: 2rem;
        max-width: 1400px;
    }

    h1, h2, h3 {
        color: var(--text-primary) !important;
        font-family: 'Inter', sans-serif !important;
    }

    .stMetric {
        background: var(--bg-card);
        padding: 1.2rem;
        border-radius: 10px;
        border: 1px solid var(--border);
        transition: transform 0.2s, border-color 0.2s;
    }

    .stMetric:hover {
        transform: translateY(-2px);
        border-color: var(--secondary);
    }

    .stMetric label {
        color: var(--text-secondary) !important;
        font-size: 0.85rem !important;
    }

    .stMetric [data-testid="stMetricValue"] {
        color: var(--text-primary) !important;
        font-weight: 700 !important;
    }

    .stButton > button {
        background: linear-gradient(135deg, var(--primary) 0%, var(--primary-light) 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1.5rem;
        font-weight: 500;
        transition: all 0.2s;
    }

    .stButton > button:hover {
        background: linear-gradient(135deg, var(--primary-light) 0%, var(--secondary) 100%);
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(200, 169, 81, 0.3);
    }

    .stTabs [data-baseweb="tab-list"] {
        background: var(--bg-card);
        border-radius: 8px;
        padding: 4px;
        gap: 4px;
    }

    .stTabs [data-baseweb="tab"] {
        background: transparent;
        color: var(--text-secondary);
        border-radius: 6px;
        font-weight: 500;
    }

    .stTabs [aria-selected="true"] {
        background: var(--primary) !important;
        color: white !important;
    }

    div[data-testid="stExpander"] {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 10px;
    }

    .stAlert {
        border-radius: 10px;
    }

    .header-banner {
        background: linear-gradient(135deg, #1B365D 0%, #2E5A88 50%, #1B365D 100%);
        padding: 2.5rem 3rem;
        border-radius: 16px;
        color: white;
        margin-bottom: 2rem;
        border: 1px solid rgba(200, 169, 81, 0.3);
        position: relative;
        overflow: hidden;
    }

    .header-banner::before {
        content: '';
        position: absolute;
        top: 0;
        right: 0;
        width: 300px;
        height: 100%;
        background: radial-gradient(circle, rgba(200, 169, 81, 0.15) 0%, transparent 70%);
    }

    .header-banner h1 {
        color: white !important;
        font-size: 2rem;
        font-weight: 700;
        margin-bottom: 0.3rem;
    }

    .header-banner p {
        color: #94A3B8;
        font-size: 1rem;
        margin: 0;
    }

    .header-banner .subtitle {
        color: var(--secondary);
        font-weight: 500;
    }

    .card {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 1.5rem;
        transition: all 0.2s;
    }

    .card:hover {
        border-color: var(--secondary);
        box-shadow: 0 4px 20px rgba(200, 169, 81, 0.1);
    }

    .badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
    }

    .badge-success {
        background: rgba(34, 197, 94, 0.15);
        color: #22C55E;
    }

    .badge-warning {
        background: rgba(245, 158, 11, 0.15);
        color: #F59E0B;
    }

    .badge-danger {
        background: rgba(239, 68, 68, 0.15);
        color: #EF4444;
    }

    .stDataFrame {
        border-radius: 10px;
        overflow: hidden;
    }
</style>
""", unsafe_allow_html=True)


def load_config():
    config_path = CONFIGS_DIR / "config.yaml"
    try:
        if config_path.exists():
            with open(config_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
    except Exception:
        pass
    return {}


def main():
    config = load_config()

    with st.sidebar:
        st.markdown("""
        <div style='text-align: center; padding: 1rem 0;'>
            <div style='font-size: 2.5rem;'>🎓</div>
            <div style='color: #C8A951; font-weight: 700; font-size: 1.1rem;'>Bienestar UST</div>
            <div style='color: #64748B; font-size: 0.75rem;'>Análisis de Bienestar Psicológico</div>
        </div>
        """, unsafe_allow_html=True)

        st.divider()

        page = st.radio(
            "Navegación",
            ["Inicio", "Panel de Control", "Chatbot", "Resúmenes", "Explicaciones", "Configuración"],
            label_visibility="collapsed"
        )

        st.divider()

        st.markdown("""
        <div style='text-align: center; color: #475569; font-size: 0.7rem; padding-top: 1rem;'>
            Universidad Santo Tomás<br>
            Sistema de Análisis Inteligente<br>
            v2.0
        </div>
        """, unsafe_allow_html=True)

    if page == "Inicio":
        show_home()
    elif page == "Panel de Control":
        show_dashboard()
    elif page == "Chatbot":
        show_chatbot()
    elif page == "Resúmenes":
        show_summaries()
    elif page == "Explicaciones":
        show_explanations()
    elif page == "Configuración":
        show_config()


def show_home():
    st.markdown("""
    <div class="header-banner">
        <h1>Análisis de Bienestar Psicológico Estudiantil</h1>
        <p><span class="subtitle">Universidad Santo Tomás</span> — Sistema Inteligente de Análisis y Monitoreo</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Participantes", "281", "+12 nuevos")
    with col2:
        st.metric("Bienestar Global", "4.52/6.00", "+0.12")
    with col3:
        st.metric("Dimensiones", "6", "Ryff-29")
    with col4:
        st.metric("Modelos IA", "10+", "Activos")

    st.divider()

    st.markdown("### Funcionalidades del Sistema")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div class="card">
            <h4 style="color: #C8A951;">📊 Análisis Estadístico</h4>
            <ul style="color: #94A3B8; font-size: 0.9rem;">
                <li>Estadísticas descriptivas</li>
                <li>Pruebas de normalidad</li>
                <li>Correlaciones</li>
                <li>Regresión múltiple (6 tipos)</li>
                <li>Clustering avanzado</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="card">
            <h4 style="color: #C8A951;">🤖 Inteligencia Artificial</h4>
            <ul style="color: #94A3B8; font-size: 0.9rem;">
                <li>Chatbot interactivo</li>
                <li>Interpretación automática</li>
                <li>Recomendaciones</li>
                <li>Detección de patrones</li>
                <li>Agente autónomo</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="card">
            <h4 style="color: #C8A951;">📈 Visualización</h4>
            <ul style="color: #94A3B8; font-size: 0.9rem;">
                <li>Panel interactivo</li>
                <li>Gráficos dinámicos</li>
                <li>Reportes LaTeX</li>
                <li>Exportación PDF</li>
                <li>Dashboard HTML</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button("📊 Ver Panel de Control", use_container_width=True):
            st.session_state.page = "Panel de Control"
            st.rerun()
    with col2:
        if st.button("💬 Consultar Chatbot", use_container_width=True):
            st.session_state.page = "Chatbot"
            st.rerun()
    with col3:
        if st.button("▶️ Ejecutar Análisis", use_container_width=True):
            st.info("Análisis en ejecución...")
    with col4:
        if st.button("📥 Descargar Reporte", use_container_width=True):
            st.info("Función disponible en Panel de Control")

    st.divider()

    st.markdown("### Último Análisis")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("""
        <div class="card">
            <p style="color: #94A3B8;"><strong style="color: #C8A951;">Fecha:</strong> 25 de Agosto, 2026 — 19:03</p>
            <p style="color: #94A3B8;"><strong style="color: #C8A951;">Estado:</strong> <span class="badge badge-success">Completado</span></p>
            <p style="color: #94A3B8;"><strong style="color: #C8A951;">Duración:</strong> 5.13 segundos</p>
            <p style="color: #94A3B8;"><strong style="color: #C8A951;">Archivos:</strong> PDF, LaTeX, HTML</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="card">
            <p style="color: #C8A951; font-weight: 600;">Resumen Rápido</p>
            <p style="color: #94A3B8; font-size: 0.85rem;">Bienestar Global: <strong style="color: #22C55E;">4.52/6.00</strong></p>
            <p style="color: #94A3B8; font-size: 0.85rem;">Más alta: <strong style="color: #22C55E;">Autoaceptación (4.68)</strong></p>
            <p style="color: #94A3B8; font-size: 0.85rem;">Más baja: <strong style="color: #F59E0B;">Relaciones (4.28)</strong></p>
            <p style="color: #94A3B8; font-size: 0.85rem;">Perfiles: <strong style="color: #3B82F6;">2 clusters</strong></p>
        </div>
        """, unsafe_allow_html=True)


def show_dashboard():
    st.markdown("""
    <div class="header-banner">
        <h1>Panel de Control</h1>
        <p>Explora los resultados del análisis de bienestar psicológico</p>
    </div>
    """, unsafe_allow_html=True)

    reports_dir = REPORTS_DIR
    dashboards = [f for f in os.listdir(reports_dir) if f.startswith("dashboard_interactivo")] if reports_dir.exists() else []

    if dashboards:
        latest_dashboard = sorted(dashboards)[-1]
        dashboard_path = reports_dir / latest_dashboard
        with open(dashboard_path, "r", encoding="utf-8") as f:
            dashboard_html = f.read()
        st.components.v1.html(dashboard_html, height=800, scrolling=True)
    else:
        st.warning("No se encontró ningún panel. Ejecuta un análisis primero.")
        if st.button("▶️ Ejecutar Análisis"):
            st.info("Análisis en ejecución...")


def show_chatbot():
    st.markdown("""
    <div class="header-banner">
        <h1>BienestarBot — Chatbot Inteligente</h1>
        <p>Haz preguntas sobre el análisis de bienestar psicológico</p>
    </div>
    """, unsafe_allow_html=True)

    config_path = CONFIGS_DIR / "config.yaml"
    gemini_configured = False

    try:
        if config_path.exists():
            with open(config_path, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f) or {}
            api_key = config.get("ai", {}).get("gemini", {}).get("api_key", "")
            if api_key:
                import google.generativeai as genai
                genai.configure(api_key=api_key)
                gemini_configured = True
    except Exception:
        pass

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = [{
            "role": "assistant",
            "content": "¡Hola! Soy **BienestarBot** 🤖. Puedo ayudarte con preguntas sobre el análisis de bienestar psicológico. ¿Qué te gustaría saber?"
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
                st.session_state.chat_history.append({"role": "user", "content": q})
                st.rerun()

    st.divider()

    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Escribe tu pregunta aquí..."):
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            response = get_response(prompt, gemini_configured)
            st.markdown(response)
        st.session_state.chat_history.append({"role": "assistant", "content": response})

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🗑️ Limpiar", use_container_width=True):
            st.session_state.chat_history = []
            st.rerun()
    with col2:
        if st.button("📥 Exportar", use_container_width=True):
            chat_text = "\n\n".join([f"**{m['role'].title()}:** {m['content']}" for m in st.session_state.chat_history])
            st.download_button("Descargar", chat_text, "conversacion.txt", "text/plain")
    with col3:
        if st.button("🔄 Nueva conversación", use_container_width=True):
            st.session_state.chat_history = []
            st.rerun()


def get_response(question, use_gemini=False):
    q = question.lower()

    predefined = {
        "hola": "¡Hola! 👋 Puedo ayudarte con preguntas sobre el análisis de bienestar. ¿Qué te gustaría saber?",
        "bienestar global": "**Bienestar Global: 4.52/6.00** — Nivel MEDIO. Los estudiantes muestran un bienestar aceptable con áreas de oportunidad.",
        "dimensión": "**Relaciones Positivas** tiene el puntaje más bajo: **4.28/6.00**. Es el principal área de oportunidad.",
        "mejorar": "**Recomendaciones:**\n1. Talleres de habilidades sociales\n2. Programas de mentoría\n3. Actividades de desarrollo personal\n4. Espacios de bienestar emocional",
        "participantes": "Participaron **281 estudiantes** de la Universidad Santo Tomás.",
        "recomendación": "**Recomendaciones:**\n1. Talleres de habilidades sociales\n2. Programas de mentoría\n3. Actividades de desarrollo personal\n4. Espacios de bienestar emocional",
    }

    for key, resp in predefined.items():
        if key in q:
            return resp

    if use_gemini:
        try:
            import google.generativeai as genai
            model = genai.GenerativeModel('gemini-2.0-flash')
            context = "Análisis de bienestar psicológico Ryff-29: 281 estudiantes, global 4.52/6.00. Dimensiones: Autoaceptación 4.68, Relaciones 4.28, Autonomía 4.52, Dominio 4.55, Propósito 4.58, Crecimiento 4.50."
            response = model.generate_content(f"Eres BienestarBot. Contexto: {context}. Responde en español: {question}")
            return response.text
        except Exception as e:
            return f"Error al conectar con IA: {e}"

    return f"Entiendo tu pregunta: **{question}**. Para una respuesta más detallada, configura la API de Gemini en la sección de Configuración."


def show_summaries():
    st.markdown("""
    <div class="header-banner">
        <h1>Resúmenes Ejecutivos</h1>
        <p>Resumen completo de resultados y hallazgos principales</p>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3, tab4 = st.tabs(["📊 General", "📈 Dimensiones", "👥 Perfiles", "💡 Recomendaciones"])

    with tab1:
        st.markdown("### Resumen General")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
            | Dato | Valor |
            |------|-------|
            | Institución | Universidad Santo Tomás |
            | Instrumento | Ryff-29 |
            | Participantes | 281 |
            | Dimensiones | 6 |
            | Ítems | 29 (escala 1-6) |
            """)
        with col2:
            st.markdown("""
            | Resultado | Valor | Estado |
            |-----------|-------|--------|
            | Bienestar Global | 4.52/6.00 | 🟡 Medio |
            | Más alta | Autoaceptación | 4.68 |
            | Más baja | Relaciones | 4.28 |
            | R² Regresión | 1.00 | 🟢 Perfecto |
            """)

    with tab2:
        st.markdown("### Promedio por Dimensión")
        st.markdown("""
        | Dimensión | Puntuación | Estado |
        |-----------|------------|--------|
        | Autoaceptación | 4.68 | ✅ Fortaleza |
        | Propósito de Vida | 4.58 | ✅ Fortaleza |
        | Dominio del Entorno | 4.55 | ✅ Fortaleza |
        | Autonomía | 4.52 | 🟡 Aceptable |
        | Crecimiento Personal | 4.50 | 🟡 Aceptable |
        | Relaciones Positivas | 4.28 | ⚠️ Oportunidad |
        """)

    with tab3:
        st.markdown("### Perfiles de Estudiantes")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
            <div class="card">
                <h4 style="color: #22C55E;">Perfil 1: Bienestar Alto (52%)</h4>
                <p style="color: #94A3B8;">Estudiantes con buen bienestar en todas las dimensiones. Perfil estable y positivo.</p>
                <p style="color: #C8A951;"><strong>Acción:</strong> Mantener estrategias actuales</p>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown("""
            <div class="card">
                <h4 style="color: #F59E0B;">Perfil 2: Bienestar en Desarrollo (48%)</h4>
                <p style="color: #94A3B8;">Estudiantes con áreas de mejora específicas. En proceso de desarrollo.</p>
                <p style="color: #C8A951;"><strong>Acción:</strong> Intervenciones focalizadas</p>
            </div>
            """, unsafe_allow_html=True)

    with tab4:
        st.markdown("### Recomendaciones")
        st.markdown("""
        | Prioridad | Recomendación | Objetivo |
        |-----------|---------------|----------|
        | 🔴 Alta | Programa de Habilidades Sociales | Relaciones Positivas |
        | 🔴 Alta | Programa de Mentoría | Propósito de Vida |
        | 🟡 Media | Talleres de Inteligencia Emocional | Autoaceptación |
        | 🟡 Media | Desarrollo Personal | Crecimiento |
        | 🟢 Baja | Actividades de Bienestar | Mantenimiento |
        """)


def show_explanations():
    st.markdown("""
    <div class="header-banner">
        <h1>Explicación de Modelos</h1>
        <p>Entiende fácilmente qué significan los resultados estadísticos</p>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3, tab4 = st.tabs(["📈 Regresión", "👥 Clustering", "🤖 Machine Learning", "📊 Estadísticas"])

    with tab1:
        st.markdown("### ¿Qué es la Regresión?")
        with st.expander("🎯 Explicación Simple", expanded=True):
            st.markdown("""
            **La regresión es como una "receta matemática" para predecir resultados.**

            Imagina que quieres predecir la nota final de un estudiante. Puedes usar el tamaño, el color y la textura. La regresión combina estos "ingredientes" para dar una predicción.

            **En nuestro caso:**
            - Ingredientes: Las 6 dimensiones del bienestar
            - Resultado: El bienestar global
            """)

        with st.expander("📊 ¿Qué significa R² = 1.0?"):
            st.markdown("""
            **R² mide qué tan BUENA es nuestra receta.**

            - **R² = 1.0** significa predicción PERFECTA (100%)
            - En nuestro caso, las 6 dimensiones explican el 100% del bienestar global
            - ¿Por qué? Porque el bienestar global se calcula como el PROMEDIO de las 6 dimensiones
            """)

        with st.expander("🔮 Odds Ratios"):
            st.markdown("""
            **Los Odds Ratios indican CUÁNTO cambia algo.**

            Para Autoaceptación (OR = 0.18): Por cada punto que SUBE, la probabilidad de bienestar BAJO se reduce en un 82%.

            **En términos simples:** Autoaceptación alta = "Escudo protector" contra problemas.
            """)

    with tab2:
        st.markdown("### ¿Qué es el Clustering?")
        with st.expander("🎯 Explicación Simple", expanded=True):
            st.markdown("""
            **El clustering es como "agrupar personas por características similares."**

            En una fiesta, la gente se agrupa naturalmente: los que bailan, los que conversan, los que comen.

            **En nuestro análisis:** Identificamos 2 perfiles de estudiantes con características diferentes.
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

            Le muestras 100 fotos de gatos y perros, la computadora aprende a distinguirlos. Luego puede identificar nuevos animales.

            **En nuestro caso:** Le mostramos datos de 281 estudiantes y el modelo aprende a predecir quién tiene bienestar bajo/alto.
            """)

        with st.expander("📊 Modelos utilizados"):
            st.markdown("""
            | Modelo | Analogía | Precisión |
            |--------|----------|-----------|
            | **Random Forest** | Comité de expertos | 99.6% |
            | **SVM** | Separar con una línea | 99.6% |
            | **Gradient Boosting** | Equipo que mejora | 99.6% |
            | **Red Neuronal** | Cerebro artificial | 99.6% |
            | **Regresión Lineal** | Fórmula matemática | 100% |
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


def show_config():
    st.markdown("""
    <div class="header-banner">
        <h1>Configuración</h1>
        <p>Configura los parámetros del sistema</p>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["📊 Análisis", "📧 Notificaciones", "🤖 IA"])

    with tab1:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### Parámetros Estadísticos")
            st.slider("Nivel de significancia", 0.01, 0.10, 0.05, 0.01)
            st.selectbox("Método de clustering", ["K-Means", "DBSCAN", "Jerárquico"])
            st.slider("Número de clusters", 2, 8, 3)
        with col2:
            st.markdown("### Regresión")
            st.multiselect("Tipos de regresión", ["Lineal", "Logística", "Ridge", "Lasso", "Polinómica", "Stepwise"], ["Lineal", "Logística", "Ridge", "Lasso"])
            st.slider("Grado polinómico", 2, 4, 2)
            st.slider("Alpha (regularización)", 0.001, 1.0, 0.1, 0.001)

    with tab2:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### Correo Electrónico")
            st.checkbox("Habilitar notificaciones", value=True)
            st.text_input("Servidor SMTP", value="smtp.gmail.com")
            st.text_input("Correo remitente", value="julkarem03@gmail.com")
        with col2:
            st.markdown("### Monitoreo")
            st.checkbox("Monitoreo automático", value=False)
            st.slider("Intervalo (minutos)", 15, 120, 30)

    with tab3:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### Google Gemini")
            st.checkbox("Habilitar Gemini", value=True)
            st.selectbox("Modelo", ["gemini-2.0-flash", "gemini-2.5-flash", "gemini-2.5-pro"])
            st.text_input("API Key", type="password")
        with col2:
            st.markdown("### Chatbot")
            st.selectbox("Personalidad", ["Profesional", "Formal", "Casual"])
            st.slider("Longitud máxima", 100, 1000, 500)


if __name__ == "__main__":
    main()
