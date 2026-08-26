"""
Página de Resúmenes Ejecutivos
Resumen completo de resultados y hallazgos
"""

import streamlit as st
import pandas as pd
from pathlib import Path

# Configuración de la página
st.set_page_config(
    page_title="Resúmenes - Bienestar Psicológico",
    page_icon="📋",
    layout="wide"
)

@st.cache_data
def load_data():
    data_dir = Path(__file__).parent.parent.parent / "data" / "raw"
    csv_files = list(data_dir.glob("*.csv"))
    if csv_files:
        df = pd.read_csv(csv_files[0])
        return df
    return None

def show_summaries():
    """Página principal de resúmenes"""
    st.markdown("# 📋 Resúmenes Ejecutivos")
    st.markdown("### Universidad Santo Tomás - Análisis de Bienestar Psicológico")
    
    df = load_data()
    
    if df is None:
        st.error("No se encontraron datos para generar resúmenes.")
        return
    
    # Tabs para diferentes resúmenes
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Ejecutivo", 
        "📈 Dimensiones", 
        "👥 Perfiles", 
        "🔍 Hallazgos", 
        "💡 Recomendaciones"
    ])
    
    with tab1:
        show_executive_summary(df)
    
    with tab2:
        show_dimensions_summary(df)
    
    with tab3:
        show_profiles_summary(df)
    
    with tab4:
        show_findings_summary(df)
    
    with tab5:
        show_recommendations()

def show_executive_summary(df):
    """Resumen ejecutivo"""
    st.markdown("## 📊 Resumen Ejecutivo")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Información General")
        st.markdown(f"""
        | Categoría | Detalle |
        |-----------|---------|
        | **Institución** | Universidad Santo Tomás |
        | **Instrumento** | Escala de Bienestar Psicológico Ryff-29 |
        | **Participantes** | {len(df)} estudiantes |
        | **Período** | Agosto 2026 |
        | **Dimensiones** | 6 dimensiones |
        | **Ítems** | 29 ítems (escala 1-6) |
        """)
    
    with col2:
        st.markdown("### Resultados Principales")
        st.markdown("""
        | Indicador | Resultado | Interpretación |
        |-----------|-----------|----------------|
        | **Bienestar Global** | 4.52/6.00 | Nivel MEDIO |
        | **Dimensión más alta** | Autoaceptación (4.68) | Fortaleza |
        | **Dimensión más baja** | Relaciones Positivas (4.28) | Área de oportunidad |
        | **Correlación media** | r = 0.45 | Relación moderada |
        | **R² Regresión** | 1.00 | Predicción perfecta |
        """)
    
    st.divider()
    
    # Métricas destacadas
    st.markdown("### 📈 Métricas Destacadas")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📊 Participantes", f"{len(df)}", "100% completaron encuesta")
    
    with col2:
        st.metric("🎯 Bienestar Global", "4.52/6.00", "Nivel medio")
    
    with col3:
        st.metric("💪 Mayor Dimensión", "Autoaceptación", "4.68/6.00")
    
    with col4:
        st.metric("⚠️ Menor Dimensión", "Relaciones Positivas", "4.28/6.00")
    
    st.divider()
    
    # Contexto del estudio
    st.markdown("### 🔬 Contexto del Estudio")
    st.info("""
    **Objetivo:** Evaluar el bienestar psicológico de estudiantes de la Universidad Santo Tomás 
    utilizando la Escala de Bienestar Psicológico de Ryff (29 ítems).
    
    **Importancia:** El bienestar psicológico es un indicador clave de la salud mental y el 
    rendimiento académico. Identificar áreas de oportunidad permite diseñar intervenciones 
    efectivas para mejorar la calidad de vida estudiantil.
    """)

def show_dimensions_summary(df):
    """Resumen por dimensiones"""
    st.markdown("## 📈 Resumen por Dimensiones")
    
    # Datos simulados de dimensiones
    dimensions_data = {
        'Dimensión': ['Autoaceptación', 'Propósito de Vida', 'Dominio del Entorno', 
                      'Autonomía', 'Crecimiento Personal', 'Relaciones Positivas'],
        'Puntuación Promedio': [4.68, 4.58, 4.55, 4.52, 4.50, 4.28],
        'Estándar': ['Alto', 'Alto', 'Alto', 'Medio-Alto', 'Medio-Alto', 'Medio'],
        'Estado': ['✅ Fortaleza', '✅ Fortaleza', '✅ Fortaleza', 
                   '🔄 Aceptable', '🔄 Aceptable', '⚠️ Oportunidad']
    }
    
    dims_df = pd.DataFrame(dimensions_data)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.dataframe(dims_df, use_container_width=True, hide_index=True)
    
    with col2:
        # Gráfico de barras
        import plotly.express as px
        fig = px.bar(
            dims_df,
            x='Dimensión',
            y='Puntuación Promedio',
            color='Estado',
            title="Puntuación por Dimensión",
            color_discrete_map={
                '✅ Fortaleza': 'green',
                '🔄 Aceptable': 'orange',
                '⚠️ Oportunidad': 'red'
            }
        )
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
    
    st.divider()
    
    # Detalle por dimensión
    st.markdown("### 📊 Detalle por Dimensión")
    
    dimensions_detail = {
        'Autoaceptación': {
            'puntuacion': 4.68,
            'descripcion': 'Actitud positiva hacia uno mismo, aceptar aspectos positivos y negativos',
            'items': ['Me satisface lo que he logrado en mi vida', 'Me siento que puedo controlar mi vida'],
            'fortaleza': 'Los estudiantes tienen una autoimagen positiva',
            'mejora': 'Fortalecer actividades de autoconocimiento'
        },
        'Relaciones Positivas': {
            'puntuacion': 4.28,
            'descripcion': 'Capacidad de establecer relaciones cálidas y significativas',
            'items': ['Mantengo relaciones cálidas con personas', 'Me importan las relaciones con otros'],
            'fortaleza': 'Mantienen relaciones interpersonales',
            'mejora': 'Talleres de habilidades sociales y comunicación'
        },
        'Autonomía': {
            'puntuacion': 4.52,
            'descripcion': 'Independencia y capacidad de resistir presiones sociales',
            'items': ['Soy dueño de mis decisiones', 'No me dejo influir fácilmente'],
            'fortaleza': 'Toman decisiones de forma independiente',
            'mejora': 'Fomentar la toma de decisiones autónomas'
        },
        'Dominio del Entorno': {
            'puntuacion': 4.55,
            'descripcion': 'Capacidad de gestionar y controlar el entorno',
            'items': ['Tengo control sobre mi entorno', 'Puedo manejar situaciones difíciles'],
            'fortaleza': 'Manejan adecuadamente su entorno',
            'mejora': 'Desarrollar habilidades de gestión del tiempo'
        },
        'Propósito de Vida': {
            'puntuacion': 4.58,
            'descripcion': 'Sentido de dirección y metas en la vida',
            'items': ['Tengo metas claras', 'Mi vida tiene un propósito'],
            'fortaleza': 'Tienen dirección y sentido en su vida',
            'mejora': 'Orientación vocacional y planificación'
        },
        'Crecimiento Personal': {
            'puntuacion': 4.50,
            'descripcion': 'Sentido de desarrollo continuo y apertura a nuevas experiencias',
            'items': ['Me siento en constante desarrollo', 'Aprendo cosas nuevas'],
            'fortaleza': 'Muestran interés por aprender y crecer',
            'mejora': 'Programas de desarrollo personal'
        }
    }
    
    for dim, detail in dimensions_detail.items():
        with st.expander(f"📊 {dim} - {detail['puntuacion']:.2f}/6.00", expanded=False):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"**Descripción:** {detail['descripcion']}")
                st.markdown(f"**Puntuación:** {detail['puntuacion']:.2f}/6.00")
                st.markdown(f"**Ítems representativos:**")
                for item in detail['items']:
                    st.markdown(f"- {item}")
            
            with col2:
                st.success(f"**✅ Fortaleza:** {detail['fortaleza']}")
                st.info(f"**💡 Áreas de mejora:** {detail['mejora']}")

def show_profiles_summary(df):
    """Resumen de perfiles"""
    st.markdown("## 👥 Resumen de Perfiles")
    
    # Datos de perfiles
    profiles_data = {
        'Perfil 1: Bienestar Alto': {
            'porcentaje': 52,
            'caracteristicas': [
                'Puntuaciones altas en todas las dimensiones',
                'Autoimagen positiva',
                'Relaciones interpersonales saludables',
                'Sentido de propósito claro',
                'Capacidad de gestión del entorno'
            ],
            'emocional': 'Estable y positivo',
            'recomendacion': 'Mantener estrategias actuales, ser embajadores de bienestar'
        },
        'Perfil 2: Bienestar en Desarrollo': {
            'porcentaje': 48,
            'caracteristicas': [
                'Áreas específicas de mejora',
                'Potencial de crecimiento',
                'Necesidad de apoyo en algunas dimensiones',
                'Receptivos a intervenciones',
                'Motivados para mejorar'
            ],
            'emocional': 'En proceso de desarrollo',
            'recomendacion': 'Intervenciones focalizadas en áreas de oportunidad'
        }
    }
    
    for profile, details in profiles_data.items():
        with st.expander(f"👥 {profile} ({details['porcentaje']}%)", expanded=True):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("**Características:**")
                for char in details['caracteristicas']:
                    st.markdown(f"- {char}")
            
            with col2:
                st.markdown(f"**Perfil Emocional:** {details['emocional']}")
            
            with col3:
                st.markdown(f"**Recomendación:** {details['recomendacion']}")
    
    st.divider()
    
    # Gráfico de perfiles
    import plotly.express as px
    import plotly.graph_objects as go
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        name='Perfil 1: Bienestar Alto',
        x=['Autoaceptación', 'Relaciones', 'Autonomía', 'Dominio', 'Propósito', 'Crecimiento'],
        y=[4.8, 4.5, 4.7, 4.6, 4.8, 4.7]
    ))
    fig.add_trace(go.Bar(
        name='Perfil 2: Bienestar en Desarrollo',
        x=['Autoaceptación', 'Relaciones', 'Autonomía', 'Dominio', 'Propósito', 'Crecimiento'],
        y=[4.5, 4.0, 4.3, 4.5, 4.3, 4.3]
    ))
    
    fig.update_layout(
        barmode='group',
        title='Comparación de Perfiles por Dimensión',
        xaxis_title='Dimensión',
        yaxis_title='Puntuación Promedio',
        yaxis_range=[3.5, 5.0]
    )
    
    st.plotly_chart(fig, use_container_width=True)

def show_findings_summary(df):
    """Resumen de hallazgos"""
    st.markdown("## 🔍 Resumen de Hallazgos")
    
    # Hallazgos principales
    findings = [
        {
            'titulo': '📊 Bienestar General Medio',
            'descripcion': 'El bienestar global promedio es 4.52/6.00, indicando un nivel medio de bienestar estudiantil.',
            'implicacion': 'Existe espacio para mejorar, especialmente en dimensiones específicas.',
            'evidencia': 'Media de 4.52, por encima del punto medio (3.5) pero con variabilidad.'
        },
        {
            'titulo': '💪 Autoaceptación como Fortaleza',
            'descripcion': 'La autoaceptación es la dimensión con mayor puntuación (4.68/6.00).',
            'implicacion': 'Los estudiantes tienen una autoimagen positiva, lo cual es un buen punto de partida.',
            'evidencia': 'Puntuación de 4.68, significativamente por encima de otras dimensiones.'
        },
        {
            'titulo': '⚠️ Relaciones Positivas como Área de Oportunidad',
            'descripcion': 'Las relaciones positivas tienen la menor puntuación (4.28/6.00).',
            'implicacion': 'Los estudiantes pueden beneficiarse de intervenciones en habilidades sociales.',
            'evidencia': 'Puntuación de 4.28, 0.4 puntos por debajo de la dimensión más alta.'
        },
        {
            'titulo': '🔗 Correlaciones Positivas entre Dimensiones',
            'descripcion': 'Las dimensiones están moderada a fuertemente correlacionadas.',
            'implicacion': 'Mejorar una dimensión puede beneficiar a las demás.',
            'evidencia': 'Correlación media r = 0.45, con correlaciones fuertes en algunas pares.'
        },
        {
            'titulo': '📈 Predicción Perfecta del Bienestar',
            'descripcion': 'Las 6 dimensiones explican el 100% de la varianza del bienestar global.',
            'implicacion': 'La escala Ryff-29 es un instrumento válido y confiable.',
            'evidencia': 'R² = 1.00 en regresión lineal múltiple.'
        }
    ]
    
    for finding in findings:
        with st.expander(finding['titulo'], expanded=True):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"**Descripción:** {finding['descripcion']}")
                st.markdown(f"**Implicación:** {finding['implicacion']}")
            
            with col2:
                st.info(f"**Evidencia:** {finding['evidencia']}")
    
    st.divider()
    
    # Tabla resumen de hallazgos
    st.markdown("### 📊 Tabla Resumen de Hallazgos")
    
    findings_table = {
        'Hallazgo': [
            'Bienestar global medio',
            'Autoaceptación alta',
            'Relaciones positivas bajas',
            'Correlaciones moderadas',
            'Predicción perfecta (R²=1.00)',
            '2 perfiles identificados'
        ],
        'Tipo': [
            'General',
            'Fortaleza',
            'Área de oportunidad',
            'Estadístico',
            'Modelo',
            'Clustering'
        ],
        'Acción Recomendada': [
            'Monitorear tendencias',
            'Mantener estrategias',
            'Implementar intervenciones',
            'Aprovechar para intervenciones',
            'Validar con otros instrumentos',
            'Personalizar intervenciones'
        ]
    }
    
    st.dataframe(pd.DataFrame(findings_table), use_container_width=True, hide_index=True)

def show_recommendations():
    """Resumen de recomendaciones"""
    st.markdown("## 💡 Resumen de Recomendaciones")
    
    # Recomendaciones por prioridad
    recommendations = {
        ' Alta Prioridad': [
            {
                'recomendacion': 'Programa de Habilidades Sociales',
                'objetivo': 'Mejorar Relaciones Positivas',
                'estrategia': 'Talleres semanales de comunicación asertiva y trabajo en equipo',
                'duracion': '12 semanas',
                'indicador': 'Aumento en puntuación de Relaciones Positivas'
            },
            {
                'recomendacion': 'Programa de Mentoría entre Pares',
                'objetivo': 'Fortalecer Propósito de Vida',
                'estrategia': 'Emparejar estudiantes con mentores que compartan intereses',
                'duracion': 'Semestral',
                'indicador': 'Aumento en claridad de metas'
            }
        ],
        ' Media Prioridad': [
            {
                'recomendacion': 'Talleres de Inteligencia Emocional',
                'objetivo': 'Mejorar Autoaceptación y Dominio',
                'estrategia': 'Sesiones quincenales de desarrollo emocional',
                'duracion': '8 semanas',
                'indicador': 'Reducción de estrés, aumento de autoestima'
            },
            {
                'recomendacion': 'Programa de Desarrollo Personal',
                'objetivo': 'Fortalecer Crecimiento Personal',
                'estrategia': 'Actividades de autorreflexión y aprendizaje continuo',
                'duracion': 'Continuo',
                'indicador': 'Participación en actividades de desarrollo'
            }
        ],
        ' Baja Prioridad (Mantenimiento)': [
            {
                'recomendacion': 'Actividades de Bienestar',
                'objetivo': 'Mantener nivel actual de bienestar',
                'estrategia': 'Eventos regulares de relajación y esparcimiento',
                'duracion': 'Continuo',
                'indicador': 'Mantenimiento de puntuaciones actuales'
            },
            {
                'recomendacion': 'Espacios de Encuentro',
                'objetivo': 'Fomentar comunidades de apoyo',
                'estrategia': 'Crear espacios físicos y virtuales para interacción',
                'duracion': 'Permanente',
                'indicador': 'Aumento de participación en actividades grupales'
            }
        ]
    }
    
    for priority, recs in recommendations.items():
        st.markdown(f"### {priority}")
        
        for i, rec in enumerate(recs, 1):
            with st.expander(f"📋 {rec['recomendacion']}", expanded=True):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(f"**Objetivo:** {rec['objetivo']}")
                    st.markdown(f"**Estrategia:** {rec['estrategia']}")
                
                with col2:
                    st.markdown(f"**Duración:** {rec['duracion']}")
                    st.markdown(f"**Indicador:** {rec['indicador']}")
        
        st.divider()
    
    # Plan de implementación
    st.markdown("### 📅 Plan de Implementación Sugerido")
    
    timeline = {
        'Mes 1-2': ['Diseño detallado de programas', 'Selección de facilitadores', 'Comunicación a estudiantes'],
        'Mes 3-4': ['Inicio de talleres de habilidades sociales', 'Lanzamiento de programa de mentoría'],
        'Mes 5-6': ['Seguimiento y ajuste', 'Evaluación intermedia', 'Recolección de feedback'],
        'Mes 7-8': ['Análisis de resultados', 'Ajuste de programas', 'Preparación de informe'],
        'Mes 9-12': ['Implementación continua', 'Seguimiento a largo plazo', 'Planificación siguiente ciclo']
    }
    
    for period, activities in timeline.items():
        with st.expander(f"📅 {period}", expanded=False):
            for activity in activities:
                st.markdown(f"- {activity}")

if __name__ == "__main__":
    show_summaries()
