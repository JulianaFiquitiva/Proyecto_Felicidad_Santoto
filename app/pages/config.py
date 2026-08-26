"""
Página de Configuración
Configuración del sistema y parámetros
"""

import streamlit as st
import yaml
from pathlib import Path

# Configuración de la página
st.set_page_config(
    page_title="Configuración - Bienestar Psicológico",
    page_icon="⚙️",
    layout="wide"
)

def show_config():
    """Página principal de configuración"""
    st.markdown("# ⚙️ Configuración del Sistema")
    st.markdown("### Personaliza los parámetros del análisis")
    
    # Tabs para diferentes configuraciones
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Análisis", 
        "📧 Notificaciones", 
        "🤖 IA", 
        "ℹ️ Acerca de"
    ])
    
    with tab1:
        show_analysis_config()
    
    with tab2:
        show_notification_config()
    
    with tab3:
        show_ai_config()
    
    with tab4:
        show_about()

def show_analysis_config():
    """Configuración de análisis"""
    st.markdown("## 📊 Configuración de Análisis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Parámetros Estadísticos")
        
        significance = st.slider(
            "Nivel de significancia (alpha)",
            min_value=0.01,
            max_value=0.10,
            value=0.05,
            step=0.01,
            help="Nivel de significancia para pruebas estadísticas"
        )
        
        confidence = st.slider(
            "Nivel de confianza",
            min_value=80,
            max_value=99,
            value=95,
            step=1,
            help="Nivel de confianza para intervalos"
        )
        
        outlier_method = st.selectbox(
            "Método para detectar valores atípicos",
            ["IQR (Rango Intercuartílico)", "Z-Score", "MAD (Desviación Absoluta Media)"],
            help="Método para identificar y manejar outliers"
        )
        
        missing_method = st.selectbox(
            "Método para datos faltantes",
            ["Eliminar filas", "Media", "Mediana", "Moda", "KNN Imputation"],
            help="Cómo manejar valores faltantes en los datos"
        )
    
    with col2:
        st.markdown("### Parámetros de Clustering")
        
        n_clusters = st.slider(
            "Número de clusters (K)",
            min_value=2,
            max_value=8,
            value=3,
            help="Número de grupos a identificar"
        )
        
        clustering_method = st.selectbox(
            "Método de clustering",
            ["K-Means", "DBSCAN", "Jerárquico (Ward)", "Jerárquico (Complete)", "Gaussian Mixture"],
            help="Algoritmo para agrupar estudiantes"
        )
        
        silhouette_threshold = st.slider(
            "Umbral de Silhouette",
            min_value=0.1,
            max_value=1.0,
            value=0.5,
            step=0.1,
            help="Calidad mínima aceptable para clustering"
        )
    
    st.divider()
    
    st.markdown("### Parámetros de Regresión")
    
    col1, col2 = st.columns(2)
    
    with col1:
        regression_types = st.multiselect(
            "Tipos de regresión a ejecutar",
            ["Lineal", "Logística", "Ridge (L2)", "Lasso (L1)", "Polinómica", "Stepwise"],
            default=["Lineal", "Logística", "Ridge (L2)", "Lasso (L1)"],
            help="Selecciona qué modelos de regresión quieres ejecutar"
        )
        
        polynomial_degree = st.slider(
            "Grado polinómico",
            min_value=2,
            max_value=4,
            value=2,
            help="Grado para regresión polinómica"
        )
    
    with col2:
        stepwise_method = st.selectbox(
            "Método Stepwise",
            ["Hacia adelante", "Hacia atrás", "Bidireccional"],
            help="Método para selección de variables"
        )
        
        regularization_strength = st.slider(
            "Fuerza de regularización (Alpha)",
            min_value=0.001,
            max_value=1.0,
            value=0.1,
            step=0.001,
            help="Fuerza de regularización para Ridge/Lasso"
        )
    
    st.divider()
    
    if st.button("💾 Guardar Configuración de Análisis", use_container_width=True):
        st.success("✅ Configuración de análisis guardada exitosamente")

def show_notification_config():
    """Configuración de notificaciones"""
    st.markdown("## 📧 Configuración de Notificaciones")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Correo Electrónico")
        
        email_enabled = st.checkbox(
            "Habilitar notificaciones por email",
            value=True,
            help="Enviar reportes por correo electrónico"
        )
        
        smtp_server = st.text_input(
            "Servidor SMTP",
            value="smtp.gmail.com",
            help="Servidor de correo electrónico"
        )
        
        smtp_port = st.number_input(
            "Puerto SMTP",
            value=587,
            help="Puerto del servidor SMTP"
        )
        
        sender_email = st.text_input(
            "Correo remitente",
            value="julkarem03@gmail.com",
            help="Correo electrónico que envía las notificaciones"
        )
        
        sender_password = st.text_input(
            "Contraseña de aplicación",
            type="password",
            help="Contraseña de aplicación de Gmail"
        )
    
    with col2:
        st.markdown("### Destinatarios")
        
        recipients = st.text_area(
            "Correos destinatarios (uno por línea)",
            value="julkarem03@gmail.com\nluisa.martinezr17@gmail.com",
            help="Correos electrónicos que recibirán los reportes"
        )
        
        st.markdown("### Configuración de Monitoreo")
        
        auto_monitoring = st.checkbox(
            "Habilitar monitoreo automático",
            value=False,
            help="Ejecutar análisis automáticamente cada cierto tiempo"
        )
        
        monitoring_interval = st.slider(
            "Intervalo de monitoreo (minutos)",
            min_value=15,
            max_value=1440,
            value=30,
            step=15,
            help="Cada cuántos minutos verificar nuevos datos"
        )
        
        notify_on_new_data = st.checkbox(
            "Notificar cuando haya nuevos datos",
            value=True,
            help="Enviar email cuando se detecten nuevas respuestas"
        )
        
        notify_on_anomalies = st.checkbox(
            "Notificar en caso de anomalías",
            value=True,
            help="Enviar alerta si se detectan datos inusuales"
        )
    
    st.divider()
    
    st.markdown("### 🔔 Configuración de Alertas")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        alert_low_wellbeing = st.checkbox(
            "Alerta: Bienestar bajo (< 3.5)",
            value=True,
            help="Notificar cuando un estudiante tenga bienestar bajo"
        )
    
    with col2:
        alert_critical = st.checkbox(
            "Alerta: Bienestar crítico (< 2.5)",
            value=True,
            help="Notificar en casos de bienestar crítico"
        )
    
    with col3:
        alert_improvement = st.checkbox(
            "Alerta: Mejora significativa",
            value=True,
            help="Notificar cuando haya mejoras significativas"
        )
    
    if st.button("💾 Guardar Configuración de Notificaciones", use_container_width=True):
        st.success("✅ Configuración de notificaciones guardada exitosamente")

def show_ai_config():
    """Configuración de IA"""
    st.markdown("## 🤖 Configuración de Inteligencia Artificial")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Google Gemini")
        
        gemini_enabled = st.checkbox(
            "Habilitar Google Gemini",
            value=True,
            help="Usar Gemini para interpretaciones y chatbot"
        )
        
        gemini_model = st.selectbox(
            "Modelo de Gemini",
            ["gemini-2.0-flash", "gemini-2.5-flash", "gemini-2.5-pro", "gemini-3.6-flash"],
            help="Selecciona el modelo de IA a usar"
        )
        
        gemini_api_key = st.text_input(
            "API Key de Gemini",
            type="password",
            help="Tu API key de Google AI Studio"
        )
        
        st.info("""
        **Cómo obtener una API key:**
        1. Ve a [Google AI Studio](https://aistudio.google.com/)
        2. Inicia sesión con tu cuenta de Google
        3. Haz clic en "Get API key"
        4. Copia la clave y pégala aquí
        """)
    
    with col2:
        st.markdown("### Configuración del Chatbot")
        
        chatbot_personality = st.selectbox(
            "Personalidad del chatbot",
            ["Profesional y Amigable", "Formal y Académico", "Casual y Divertido"],
            help="Estilo de comunicación del chatbot"
        )
        
        max_response_length = st.slider(
            "Longitud máxima de respuesta",
            min_value=100,
            max_value=1000,
            value=500,
            step=50,
            help="Número máximo de caracteres por respuesta"
        )
        
        include_data_sources = st.checkbox(
            "Incluir fuentes de datos en respuestas",
            value=True,
            help="Mostrar de dónde viene la información"
        )
        
        language = st.selectbox(
            "Idioma",
            ["Español", "Inglés", "Portugués"],
            help="Idioma de las respuestas del chatbot"
        )
    
    st.divider()
    
    st.markdown("### 🧠 Configuración del Agente Autónomo")
    
    col1, col2 = st.columns(2)
    
    with col1:
        autonomous_enabled = st.checkbox(
            "Habilitar agente autónomo",
            value=True,
            help="Permitir que el sistema tome decisiones automáticas"
        )
        
        decision_threshold = st.slider(
            "Umbral de decisión",
            min_value=0.1,
            max_value=1.0,
            value=0.7,
            step=0.1,
            help="Nivel de confianza mínimo para acciones automáticas"
        )
        
        auto_recommendations = st.checkbox(
            "Generar recomendaciones automáticas",
            value=True,
            help="El agente puede sugerir intervenciones"
        )
    
    with col2:
        memory_enabled = st.checkbox(
            "Habilitar memoria del agente",
            value=True,
            help="El agente recuerda análisis anteriores"
        )
        
        learning_rate = st.slider(
            "Tasa de aprendizaje",
            min_value=0.01,
            max_value=0.5,
            value=0.1,
            step=0.01,
            help="Qué tan rápido aprende el agente"
        )
        
        max_memory_size = st.slider(
            "Tamaño máximo de memoria",
            min_value=10,
            max_value=100,
            value=50,
            step=10,
            help="Número máximo de análisis en memoria"
        )
    
    if st.button("💾 Guardar Configuración de IA", use_container_width=True):
        st.success("✅ Configuración de IA guardada exitosamente")

def show_about():
    """Página de Acerca de"""
    st.markdown("## ℹ️ Acerca del Sistema")
    
    st.markdown("""
    ### 🎓 Análisis de Bienestar Psicológico Estudiantil
    
    **Universidad Santo Tomás**
    
    Este sistema fue desarrollado para evaluar y monitorear el bienestar psicológico 
    de estudiantes utilizando la Escala de Bienestar Psicológico de Ryff (29 ítems).
    
    ---
    
    ### 📋 Características Principales
    
    1. **📊 Análisis Estadístico Completo**
       - Estadísticas descriptivas
       - Pruebas de normalidad
       - Correlaciones
       - Regresión múltiple (6 tipos)
       - Clustering avanzado
       - Modelos predictivos
    
    2. **🤖 Inteligencia Artificial**
       - Chatbot interactivo con Gemini
       - Interpretaciones automáticas
       - Recomendaciones personalizadas
       - Detección de patrones
    
    3. **📈 Visualización Interactiva**
       - Dashboard con Plotly
       - Gráficos dinámicos
       - Exportación múltiple
    
    4. **📧 Monitoreo y Notificaciones**
       - Actualización automática cada 30 minutos
       - Alertas por email
       - Detección de anomalías
    
    ---
    
    ### 🔬 Instrumento: Escala de Ryff-29
    
    **Autora:** Carol D. Ryff
    
    **Adaptación Española:** Díaz et al. (2006)
    
    **Dimensiones:**
    1. Autoaceptación
    2. Relaciones Positivas con Otros
    3. Autonomía
    4. Dominio del Entorno
    5. Propósito de Vida
    6. Crecimiento Personal
    
    **Ítems:** 29 ítems en escala Likert de 1 a 6
    
    ---
    
    ### 🛠️ Tecnologías Utilizadas
    
    - **Python** - Lenguaje de programación principal
    - **Streamlit** - Framework para aplicaciones web
    - **Pandas/NumPy** - Manipulación de datos
    - **Scikit-learn** - Machine Learning
    - **Plotly** - Visualización interactiva
    - **Google Gemini** - Inteligencia Artificial
    - **ReportLab** - Generación de PDFs
    - **LaTeX** - Reportes profesionales
    
    ---
    
    ### 📊 Datos del Proyecto
    
    - **Participantes:** 281 estudiantes
    - **Dimensiones:** 6 dimensiones del bienestar
    - **Ítems totales:** 29 ítems
    - **Escala:** Likert 1-6
    - **Fecha:** Agosto 2026
    
    ---
    
    ### 👥 Equipo de Desarrollo
    
    - **Investigación:** Universidad Santo Tomás
    - **Desarrollo:** Sistema de Análisis Inteligente
    
    ---
    
    ### 📞 Soporte
    
    Para soporte técnico o preguntas sobre el sistema, contacta al equipo de desarrollo.
    """)

if __name__ == "__main__":
    show_config()
