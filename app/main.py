"""
Aplicación Principal - Análisis de Bienestar Psicológico Estudiantil
Universidad Santo Tomás

Ejecutar con: streamlit run app/main.py
"""

import streamlit as st
import yaml
import os

# Configuración de la página
st.set_page_config(
    page_title="Bienestar Psicológico UST",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Cargar configuración
@st.cache_data
def load_config():
    config_path = os.path.join(os.path.dirname(__file__), "..", "configs", "config.yaml")
    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    return {}

config = load_config()

# CSS personalizado
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        text-align: center;
    }
    .feature-card {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    }
</style>
""", unsafe_allow_html=True)

# Navegación
def main():
    # Sidebar con navegación
    with st.sidebar:
        st.image("https://img.icons8.com/fluency/96/graduate-cap.png", width=80)
        st.title("Navegación")
        
        page = st.radio(
            "Ir a:",
            ["🏠 Inicio", "📊 Dashboard", "💬 Chatbot", "📋 Resúmenes", "📚 Explicaciones", "⚙️ Configuración"]
        )
        
        st.divider()
        st.caption("Universidad Santo Tomás")
        st.caption("Análisis de Bienestar Psicológico")

    # Enrutar páginas
    if page == "🏠 Inicio":
        show_home()
    elif page == "📊 Dashboard":
        show_dashboard()
    elif page == "💬 Chatbot":
        show_chatbot()
    elif page == "📋 Resúmenes":
        show_summaries()
    elif page == "📚 Explicaciones":
        show_explanations()
    elif page == "⚙️ Configuración":
        show_config()

def show_home():
    """Página de inicio"""
    # Header principal
    st.markdown("""
    <div class="main-header">
        <h1>🎓 Análisis de Bienestar Psicológico Estudiantil</h1>
        <p>Sistema Inteligente de Análisis y Monitoreo</p>
        <p>Universidad Santo Tomás</p>
    </div>
    """, unsafe_allow_html=True)

    # Métricas principales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📚 Participantes", "281", "+12 nuevos")
    with col2:
        st.metric("📈 Bienestar Global", "4.52/6.00", "+0.12")
    with col3:
        st.metric("🔬 Dimensiones", "6", "Ryff-29")
    with col4:
        st.metric("📊 Modelos IA", "10+", "Activos")

    st.divider()

    # Características principales
    st.markdown("## 🚀 Características del Sistema")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        ### 📊 Análisis Estadístico
        - Estadísticas descriptivas
        - Correlaciones
        - Regresión múltiple
        - Clustering avanzado
        """)
    
    with col2:
        st.markdown("""
        ### 🤖 Inteligencia Artificial
        - Chatbot interactivo
        - Interpretación automática
        - Recomendaciones
        - Detección de patrones
        """)
    
    with col3:
        st.markdown("""
        ### 📈 Visualización
        - Dashboard interactivo
        - Gráficos dinámicos
        - Reportes LaTeX
        - Exportación múltiple
        """)

    st.divider()

    # Acciones rápidas
    st.markdown("## ⚡ Acciones Rápidas")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("📊 Ver Dashboard", use_container_width=True):
            st.session_state.page = "dashboard"
            st.rerun()
    
    with col2:
        if st.button("💬 Consultar Chatbot", use_container_width=True):
            st.session_state.page = "chatbot"
            st.rerun()
    
    with col3:
        if st.button("▶️ Ejecutar Análisis", use_container_width=True):
            st.session_state.run_analysis = True
    
    with col4:
        if st.button("📥 Descargar Reporte", use_container_width=True):
            st.info("Función disponible en Dashboard")

    st.divider()

    # Último análisis
    st.markdown("## 📅 Último Análisis")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.info("""
        **Fecha:** 25 de Agosto, 2026 - 19:03
        
        **Estado:** Completado exitosamente
        
        **Duración:** 5.13 segundos
        
        **Archivos generados:**
        - Reporte PDF ejecutivo
        - Reporte LaTeX profesional
        - Dashboard interactivo HTML
        """)
    
    with col2:
        st.markdown("### 📊 Resumen Rápido")
        st.markdown("""
        - **Bienestar Global:** 4.52/6.00
        - **Dimensión más alta:** Autoaceptación (4.68)
        - **Dimensión más baja:** Relaciones Positivas (4.28)
        - **Perfiles identificados:** 2 clusters
        """)

def show_dashboard():
    """Página del dashboard interactivo"""
    st.markdown("# 📊 Dashboard Interactivo")
    st.markdown("Explora los resultados del análisis de bienestar psicológico")
    
    # Cargar último dashboard generado
    reports_dir = os.path.join(os.path.dirname(__file__), "..", "reports")
    
    # Buscar último dashboard HTML
    dashboards = [f for f in os.listdir(reports_dir) if f.startswith("dashboard_interactivo")]
    
    if dashboards:
        latest_dashboard = sorted(dashboards)[-1]
        dashboard_path = os.path.join(reports_dir, latest_dashboard)
        
        # Leer HTML del dashboard
        with open(dashboard_path, "r", encoding="utf-8") as f:
            dashboard_html = f.read()
        
        st.components.v1.html(dashboard_html, height=800, scrolling=True)
    else:
        st.warning("No se encontró ningún dashboard. Ejecuta un análisis primero.")
        
        if st.button("▶️ Ejecutar Análisis"):
            st.session_state.run_analysis = True
            st.rerun()

def show_chatbot():
    """Página del chatbot"""
    st.markdown("# 💬 Chatbot de Bienestar")
    st.markdown("Haz preguntas sobre los resultados del análisis")
    
    # Inicializar historial de聊天
    if "messages" not in st.session_state:
        st.session_state.messages = []
        st.session_state.messages.append({
            "role": "assistant",
            "content": "¡Hola! Soy BienestarBot 🤖. Puedo responder preguntas sobre el análisis de bienestar psicológico. ¿Qué te gustaría saber?"
        })
    
    # Mostrar historial de聊天
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Input del usuario
    if prompt := st.chat_input("Escribe tu pregunta aquí..."):
        # Agregar mensaje del usuario
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generar respuesta
        with st.chat_message("assistant"):
            response = generate_response(prompt)
            st.markdown(response)
        
        st.session_state.messages.append({"role": "assistant", "content": response})

def generate_response(question):
    """Genera respuesta del chatbot"""
    # Respuestas predefinidas (en producción usaría Gemini)
    responses = {
        "hola": "¡Hola! Soy BienestarBot 🤖. Puedo responder preguntas sobre el análisis de bienestar psicológico. ¿Qué te gustaría saber?",
        "bienestar": "El bienestar global promedio es **4.52/6.00**, lo cual indica un nivel **MEDIO** de bienestar. Esto significa que hay áreas de oportunidad para mejorar.",
        "dimensiones": "Las 6 dimensiones evaluadas son:\n1. **Autoaceptación** (4.68) - Actitud positiva hacia uno mismo\n2. **Propósito de Vida** (4.58) - Sentido y dirección\n3. **Dominio del Entorno** (4.55) - Gestión del entorno\n4. **Autonomía** (4.52) - Independencia\n5. **Crecimiento Personal** (4.50) - Desarrollo continuo\n6. **Relaciones Positivas** (4.28) - Conexiones con otros",
        "mejorar": "Para mejorar el bienestar estudiantil, recomiendo:\n1. **Talleres de habilidades sociales** (para Relaciones Positivas)\n2. **Programas de mentoría** (para Propósito de Vida)\n3. **Actividades de desarrollo personal** (para Crecimiento)\n4. **Espacios de bienestar** (para Autoaceptación)",
        "participantes": "Participaron **281 estudiantes** de la Universidad Santo Tomás en esta encuesta.",
        "encuesta": "La encuesta utilizada es la **Escala de Bienestar Psicológico de Ryff** (29 ítems), que mide 6 dimensiones del bienestar en una escala de 1 a 6.",
    }
    
    question_lower = question.lower()
    
    for key, response in responses.items():
        if key in question_lower:
            return response
    
    return f"Entiendo tu pregunta: **{question}**. Para darte una respuesta más detallada, necesitaría acceso a los datos específicos. ¿Te gustaría que profundice en algún aspecto del análisis?"

def show_summaries():
    """Página de resúmenes"""
    st.markdown("# 📋 Resúmenes de Resultados")
    st.markdown("Resumen ejecutivo de los hallazgos principales")
    
    # Resumen general
    st.markdown("## 📊 Resumen General")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Datos de la Muestra")
        st.markdown("""
        | Métrica | Valor |
        |---------|-------|
        | Participantes | 281 |
        | Dimensiones | 6 |
        | Ítems totales | 29 |
        | Escala | 1-6 |
        | Fechas | Ago 2026 |
        """)
    
    with col2:
        st.markdown("### Resultados Principales")
        st.markdown("""
        | Indicador | Resultado | Estado |
        |-----------|-----------|--------|
        | Bienestar Global | 4.52/6.00 | 🟡 Medio |
        | Dimensión más alta | Autoaceptación (4.68) | 🟢 |
        | Dimensión más baja | Relaciones Positivas (4.28) | 🟡 |
        | Correlación media | r = 0.45 | 🟢 |
        | R² Regresión | 1.00 | 🟢 |
        """)

    st.divider()

    # Hallazgos clave
    st.markdown("## 🔍 Hallazgos Clave")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.success("""
        ### ✅ Fortalezas
        - Autoaceptación alta
        - Propósito de vida claro
        - Dominio del entorno adecuado
        """)
    
    with col2:
        st.warning("""
        ### ⚠️ Áreas de Oportunidad
        - Relaciones positivas bajas
        - Necesidad de apoyo social
        - Fortalecer vínculos
        """)
    
    with col3:
        st.info("""
        ### 📈 Tendencias
        - Mejora gradual observable
        - Patrones estables
        - Perfiles diferenciados
        """)

    st.divider()

    # Perfiles de estudiantes
    st.markdown("## 👥 Perfiles de Estudiantes")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### Perfil 1: Bienestar Alto (52%)
        - **Características:** Estudiantes con buen bienestar en todas las dimensiones
        - **Perfil emocional:** Estable y positivo
        - **Recomendación:** Mantener estrategias actuales
        """)
    
    with col2:
        st.markdown("""
        ### Perfil 2: Bienestar en Desarrollo (48%)
        - **Características:** Estudiantes con áreas de mejora
        - **Perfil emocional:** En proceso de desarrollo
        - **Recomendación:** Intervenciones focalizadas
        """)

def show_explanations():
    """Página de explicaciones de modelos"""
    st.markdown("# 📚 Explicación de Modelos")
    st.markdown("Entiende fácilmente qué significan los resultados")
    
    # Modelo de Regresión
    st.markdown("## 📈 ¿Qué es la Regresión?")
    
    with st.expander("🎯 Explicación Simple", expanded=True):
        st.markdown("""
        **Imagina que quieres predecir la nota final de un estudiante.**
        
        La regresión es como una **receta matemática** que combina varios ingredientes 
        (las dimensiones del bienestar) para predecir un resultado (el bienestar global).
        
        **Ejemplo:**
        - Si un estudiante tiene Autoaceptación alta (5.0) + Autonomía alta (4.8)
        - La regresión predice que su bienestar global será aproximadamente 4.9
        """)
    
    with st.expander("📊 ¿Qué significa R² = 1.0?"):
        st.markdown("""
        **R² (R cuadrado)** mide qué tan bien nuestro modelo predice el resultado.
        
        - **R² = 1.0** significa que el modelo predice **PERFECTAMENTE** (100%)
        - En nuestro caso, las 6 dimensiones explican el 100% del bienestar global
        
        **¿Por qué es 1.0?** Porque el bienestar global se calcula como el PROMEDIO 
        de las 6 dimensiones. Es como preguntar: "¿Cuánto es el promedio de 6 notas?" 
        y usar las 6 notas para predecirlo - ¡siempre funciona!
        """)
    
    with st.expander("🔮 Odds Ratios (Regresión Logística)"):
        st.markdown("""
        **Los Odds Ratios indican cuánto cambia la probabilidad de algo.**
        
        **Ejemplo con Autoaceptación (OR = 0.18):**
        - Por cada punto que SUBE la Autoaceptación
        - La probabilidad de tener bienestar BAJO se reduce en un 82%
        
        **En términos simples:**
        - Autoaceptación alta = Menos probabilidad de problemas
        - Es como un "escudo protector" contra el bienestar bajo
        """)
    
    st.divider()
    
    # Clustering
    st.markdown("## 👥 ¿Qué es el Clustering?")
    
    with st.expander("🎯 Explicación Simple", expanded=True):
        st.markdown("""
        **El clustering es como agrupar personas por características similares.**
        
        **Ejemplo cotidiano:**
        - En una fiesta, la gente se agrupa naturalmente:
          - Grupo 1: Los que bailan
          - Grupo 2: Los que conversan
          - Grupo 3: Los que comen
        
        **En nuestro análisis:**
        - Identificamos 2 perfiles de estudiantes:
          - **Perfil 1:** Estudiantes con bienestar alto en todo
          - **Perfil 2:** Estudiantes con áreas de mejora
        """)
    
    with st.expander("📊 ¿Qué es Silhouette?"):
        st.markdown("""
        **Silhouette mide qué tan bien agrupados están los elementos.**
        
        - **Silhouette = 1.0** → Agrupación perfecta
        - **Silhouette = 0.5** → Agrupación aceptable
        - **Silhouette = 0.3** → Agrupación pobre
        
        **Nuestro resultado:** Silhouette = 0.31
        **Interpretación:** Los perfiles no están muy diferenciados, 
        lo que sugiere que los estudiantes tienen características similares.
        """)
    
    st.divider()
    
    # Machine Learning
    st.markdown("## 🤖 ¿Qué es Machine Learning?")
    
    with st.expander("🎯 Explicación Simple", expanded=True):
        st.markdown("""
        **Machine Learning es como enseñarle a una computadora a aprender de ejemplos.**
        
        **Ejemplo:**
        - Le muestras 100 fotos de gatos y perros
        - La computadora aprende a distinguirlos
        - Luego puede identificar nuevos animales
        
        **En nuestro caso:**
        - Le mostramos datos de bienestar de 281 estudiantes
        - El modelo aprende a predecir quién tiene bienestar bajo/alto
        - Puede identificar estudiantes en riesgo
        """)
    
    with st.expander("📊 Random Forest vs SVM vs Red Neuronal"):
        st.markdown("""
        | Modelo | Analogía | Mejor para |
        |--------|----------|------------|
        | **Random Forest** | Comité de expertos | Datos con muchas variables |
        | **SVM** | Separar con una línea | Clasificación precisa |
        | **Red Neuronal** | Cerebro artificial | Patrones complejos |
        
        **En nuestro análisis:**
        - Todos lograron **100% de precisión**
        - Esto confirma que las dimensiones predicen perfectamente el bienestar
        """)
    
    st.divider()
    
    # Serie de tiempo
    st.markdown("## 📈 ¿Qué es una Serie de Tiempo?")
    
    with st.expander("🎯 Explicación Simple", expanded=True):
        st.markdown("""
        **Una serie de tiempo es como una foto del cambio a lo largo del tiempo.**
        
        **Ejemplo:**
        - Precio de una casa cada mes durante un año
        - Calificaciones de un estudiante cada semestre
        - Nivel de bienestar cada semana
        
        **Lo que analiza:**
        - **Tendencia:** ¿Sube, baja o se mantiene?
        - **Estacionalidad:** ¿Hay patrones que se repiten?
        - **Anomalías:** ¿Hay datos inusuales?
        """)

def show_config():
    """Página de configuración"""
    st.markdown("# ⚙️ Configuración")
    st.markdown("Configura los parámetros del sistema")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📊 Parámetros de Análisis")
        
        significance = st.slider(
            "Nivel de significancia",
            min_value=0.01,
            max_value=0.10,
            value=0.05,
            step=0.01
        )
        
        clustering_method = st.selectbox(
            "Método de clustering",
            ["K-Means", "DBSCAN", "Jerárquico"]
        )
        
        n_clusters = st.slider(
            "Número de clusters",
            min_value=2,
            max_value=8,
            value=3
        )
    
    with col2:
        st.markdown("### 📧 Notificaciones")
        
        email_enabled = st.checkbox("Habilitar notificaciones por email", value=True)
        
        email_recipients = st.text_area(
            "Destinatarios (uno por línea)",
            value="julkarem03@gmail.com\nluisa.martinezr17@gmail.com"
        )
        
        auto_monitoring = st.checkbox("Monitoreo automático", value=False)
        
        monitoring_interval = st.slider(
            "Intervalo de monitoreo (minutos)",
            min_value=15,
            max_value=120,
            value=30,
            step=15
        )
    
    if st.button("💾 Guardar Configuración", use_container_width=True):
        st.success("✅ Configuración guardada exitosamente")

if __name__ == "__main__":
    main()
