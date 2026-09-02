"""
Aplicación Principal - Bienestar Psicológico UST
Versión optimizada para Railway
"""

import streamlit as st
import os

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
            ["Inicio", "Análisis", "Chatbot", "Resúmenes"],
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


def show_home():
    st.markdown("""
    <div style='background: linear-gradient(135deg, #1B365D 0%, #2E5A88 100%); padding: 2rem; border-radius: 16px; color: white; margin-bottom: 2rem;'>
        <h1 style='color: white; margin: 0;'>Análisis de Bienestar Psicológico</h1>
        <p style='color: #94A3B8; margin: 0.5rem 0 0 0;'>Universidad Santo Tomás — Sistema Inteligente</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Participantes", "281")
    with col2:
        st.metric("Bienestar Global", "4.52/6")
    with col3:
        st.metric("Dimensiones", "6")
    with col4:
        st.metric("Modelos", "10+")

    st.divider()

    st.markdown("### Funcionalidades")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div style='background: #1A2736; padding: 1.5rem; border-radius: 10px; border: 1px solid #2D3F50;'>
            <h4 style='color: #C8A951;'>📊 Análisis Estadístico</h4>
            <ul style='color: #94A3B8;'>
                <li>Estadísticas descriptivas</li>
                <li>Correlaciones</li>
                <li>Regresión múltiple</li>
                <li>Clustering avanzado</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div style='background: #1A2736; padding: 1.5rem; border-radius: 10px; border: 1px solid #2D3F50;'>
            <h4 style='color: #C8A951;'>🤖 Inteligencia Artificial</h4>
            <ul style='color: #94A3B8;'>
                <li>Chatbot interactivo</li>
                <li>Interpretación automática</li>
                <li>Recomendaciones</li>
                <li>Detección de patrones</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div style='background: #1A2736; padding: 1.5rem; border-radius: 10px; border: 1px solid #2D3F50;'>
            <h4 style='color: #C8A951;'>📈 Visualización</h4>
            <ul style='color: #94A3B8;'>
                <li>Panel interactivo</li>
                <li>Gráficos dinámicos</li>
                <li>Reportes PDF</li>
                <li>Exportación múltiple</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)


def show_analysis():
    st.markdown("""
    <div style='background: linear-gradient(135deg, #1B365D 0%, #2E5A88 100%); padding: 2rem; border-radius: 16px; color: white; margin-bottom: 2rem;'>
        <h1 style='color: white; margin: 0;'>Panel de Análisis</h1>
        <p style='color: #94A3B8;'>Resultados del análisis de bienestar psicológico</p>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["Dimensiones", "Correlaciones", "Modelos"])

    with tab1:
        st.markdown("### Promedio por Dimensión")
        st.markdown("""
        | Dimensión | Puntuación | Estado |
        |-----------|------------|--------|
        | Autoaceptación | 4.68 | Fortaleza |
        | Propósito de Vida | 4.58 | Fortaleza |
        | Dominio del Entorno | 4.55 | Fortaleza |
        | Autonomía | 4.52 | Aceptable |
        | Crecimiento Personal | 4.50 | Aceptable |
        | Relaciones Positivas | 4.28 | Oportunidad |
        """)

    with tab2:
        st.markdown("### Correlaciones Principales")
        st.markdown("""
        | Variable 1 | Variable 2 | Correlación |
        |------------|------------|-------------|
        | Autoaceptación | Crecimiento | 0.72 (Fuerte) |
        | Autonomía | Dominio | 0.68 (Moderada) |
        | Propósito | Autoaceptación | 0.65 (Moderada) |
        """)

    with tab3:
        st.markdown("### Resultados de Modelos")
        st.markdown("""
        | Modelo | Precisión | AUC-ROC |
        |--------|-----------|---------|
        | Random Forest | 99.6% | 0.99 |
        | SVM | 99.6% | 0.99 |
        | Gradient Boosting | 99.6% | 0.99 |
        | Red Neuronal | 99.6% | 0.99 |
        | Regresión Lineal | 100% | 1.00 |
        """)


def show_chatbot():
    st.markdown("""
    <div style='background: linear-gradient(135deg, #1B365D 0%, #2E5A88 100%); padding: 2rem; border-radius: 16px; color: white; margin-bottom: 2rem;'>
        <h1 style='color: white; margin: 0;'>BienestarBot</h1>
        <p style='color: #94A3B8;'>Chatbot de bienestar psicológico</p>
    </div>
    """, unsafe_allow_html=True)

    if "messages" not in st.session_state:
        st.session_state.messages = [{
            "role": "assistant",
            "content": "¡Hola! Soy BienestarBot. ¿Qué te gustaría saber sobre el análisis de bienestar?"
        }]

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Escribe tu pregunta..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        response = get_bot_response(prompt)

        with st.chat_message("assistant"):
            st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})


def get_bot_response(question):
    q = question.lower()

    if "hola" in q:
        return "¡Hola! Puedo ayudarte con información sobre el bienestar psicológico de los estudiantes."
    elif "bienestar" in q or "global" in q:
        return "El **bienestar global** es **4.52/6.00**, un nivel medio con oportunidades de mejora."
    elif "dimensión" in q or "peor" in q:
        return "**Relaciones Positivas** es la dimensión más baja con **4.28/6.00**."
    elif "participan" in q or "cuántos" in q:
        return "Participaron **281 estudiantes** de la Universidad Santo Tomás."
    elif "recomendar" in q or "mejorar" in q:
        return "**Recomendaciones:**\n1. Talleres de habilidades sociales\n2. Programas de mentoría\n3. Desarrollo personal"
    else:
        return f"Entiendo tu pregunta: **{question}**. Para más detalles, revisa la sección de Análisis."


def show_summaries():
    st.markdown("""
    <div style='background: linear-gradient(135deg, #1B365D 0%, #2E5A88 100%); padding: 2rem; border-radius: 16px; color: white; margin-bottom: 2rem;'>
        <h1 style='color: white; margin: 0;'>Resúmenes</h1>
        <p style='color: #94A3B8;'>Resumen ejecutivo de resultados</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Datos Generales")
        st.markdown("""
        | Dato | Valor |
        |------|-------|
        | Institución | Universidad Santo Tomás |
        | Instrumento | Ryff-29 |
        | Participantes | 281 |
        | Dimensiones | 6 |
        """)

    with col2:
        st.markdown("### Resultados Principales")
        st.markdown("""
        | Indicador | Resultado |
        |-----------|-----------|
        | Bienestar Global | 4.52/6.00 |
        | Más alta | Autoaceptación (4.68) |
        | Más baja | Relaciones (4.28) |
        """)

    st.divider()

    st.markdown("### Recomendaciones")
    st.markdown("""
    | Prioridad | Recomendación | Objetivo |
    |-----------|---------------|----------|
    | Alta | Habilidades Sociales | Relaciones |
    | Alta | Mentoría | Propósito |
    | Media | Inteligencia Emocional | Autoaceptación |
    """)


if __name__ == "__main__":
    main()
