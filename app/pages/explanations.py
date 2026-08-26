"""
Página de Explicaciones de Modelos
Explicaciones fáciles de entender para todos los usuarios
"""

import streamlit as st

# Configuración de la página
st.set_page_config(
    page_title="Explicaciones - Bienestar Psicológico",
    page_icon="📚",
    layout="wide"
)

def show_explanations():
    """Página principal de explicaciones"""
    st.markdown("# 📚 Explicación de Modelos y Resultados")
    st.markdown("### Entiende fácilmente qué significan los números")
    
    # Tabs para diferentes secciones
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🎯 Fundamentos", 
        "📈 Regresión", 
        "👥 Clustering", 
        "🤖 Machine Learning", 
        "📊 Estadísticas"
    ])
    
    with tab1:
        show_fundamentals()
    
    with tab2:
        show_regression_explanation()
    
    with tab3:
        show_clustering_explanation()
    
    with tab4:
        show_ml_explanation()
    
    with tab5:
        show_statistics_explanation()

def show_fundamentals():
    """Fundamentos del análisis"""
    st.markdown("## 🎯 Fundamentos del Análisis")
    
    # Escala Ryff
    st.markdown("### 📏 ¿Qué es la Escala de Ryff?")
    
    with st.expander("📖 Explicación Simple", expanded=True):
        st.markdown("""
        **La Escala de Ryff es como un "termómetro" del bienestar psicológico.**
        
        **Imagina que quieres saber cómo se siente una persona.** En lugar de preguntar 
        directamente "¿cómo estás?", usamos 29 preguntas que miden 6 áreas diferentes 
        del bienestar.
        
        **Las 6 áreas que medimos:**
        1. **Autoaceptación** - ¿Qué tan bien te sientes contigo mismo?
        2. **Relaciones Positivas** - ¿Qué tan buenas son tus relaciones con otros?
        3. **Autonomía** - ¿Qué tan independiente eres en tus decisiones?
        4. **Dominio del Entorno** - ¿Qué tan bien manejas tu entorno?
        5. **Propósito de Vida** - ¿Qué tan claro tienes tus metas?
        6. **Crecimiento Personal** - ¿Qué tan en constante desarrollo te sientes?
        """)
    
    with st.expander("📊 ¿Cómo se responde?"):
        st.markdown("""
        **Cada pregunta se responde del 1 al 6:**
        
        | Puntuación | Significado |
        |------------|-------------|
        | 1 | Muy en desacuerdo |
        | 2 | En desacuerdo |
        | 3 | Ligeramente en desacuerdo |
        | 4 | Ligeramente de acuerdo |
        | 5 | De acuerdo |
        | 6 | Muy de acuerdo |
        
        **Ejemplo:**
        - "Me satisface lo que he logrado en mi vida"
        - Si respondes 6 = Muy de acuerdo = Puntuación alta en Autoaceptación
        """)
    
    with st.expander("🔢 ¿Cómo se calcula el resultado?"):
        st.markdown("""
        **Paso 1: Calcular promedio por dimensión**
        - Cada dimensión tiene 4-5 preguntas
        - Se promedian las respuestas de esas preguntas
        - Resultado: Una puntuación del 1 al 6 por dimensión
        
        **Paso 2: Calcular bienestar global**
        - Se promedian las 6 dimensiones
        - Resultado: Una puntuación del 1 al 6 del bienestar general
        
        **Ejemplo:**
        - Autoaceptación: 4.8
        - Relaciones: 4.2
        - Autonomía: 4.5
        - Dominio: 4.6
        - Propósito: 4.7
        - Crecimiento: 4.5
        - **Bienestar Global: 4.55/6.00**
        """)
    
    st.divider()
    
    # Interpretación de resultados
    st.markdown("### 🎯 ¿Cómo interpretar los resultados?")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.success("""
        ### 🟢 Nivel Alto (5.0-6.0)
        **Significado:** Bienestar excelente
        
        **Qué significa:**
        - El estudiante se siente bien consigo mismo
        - Tiene relaciones saludables
        - Siente que tiene control sobre su vida
        - Tiene metas claras
        
        **Acción:** Mantener estrategias actuales
        """)
    
    with col2:
        st.warning("""
        ### 🟡 Nivel Medio (3.5-4.9)
        **Significado:** Bienestar aceptable con áreas de mejora
        
        **Qué significa:**
        - El estudiante funciona adecuadamente
        - Hay áreas específicas para mejorar
        - Puede beneficiarse de apoyo
        - Tiene potencial de crecimiento
        
        **Acción:** Intervenciones focalizadas
        """)
    
    with col3:
        st.error("""
        ### 🔴 Nivel Bajo (1.0-3.4)
        **Significado:** Bienestar que requiere atención
        
        **Qué significa:**
        - El estudiante puede estar en dificultades
        - Necesita apoyo inmediato
        - Puede requerir intervención profesional
        - Está en riesgo emocional
        
        **Acción:** Intervención urgente
        """)

def show_regression_explanation():
    """Explicación de regresión"""
    st.markdown("## 📈 ¿Qué es la Regresión?")
    
    with st.expander("🎯 Explicación Simple", expanded=True):
        st.markdown("""
        **La regresión es como una "receta matemática" para predecir resultados.**
        
        **Imagina que quieres predecir cuánto va a pesar una fruta.**
        - Puedes usar el tamaño (grande/pequeña)
        - Puedes usar el color (verde/amarillo)
        - Puedes usar la textura (suave/rugosa)
        
        La regresión combina estos "ingredientes" para dar una predicción.
        
        **En nuestro caso:**
        - Ingredientes: Las 6 dimensiones del bienestar
        - Resultado: El bienestar global
        """)
    
    with st.expander("📊 ¿Qué significa R² = 1.0?"):
        st.markdown("""
        **R² (R cuadrado) mide qué tan BUENA es nuestra receta.**
        
        | R² | Significado | Ejemplo |
        |----|-------------|---------|
        | 1.0 | Perfecto (100%) | Si conoces las 6 dimensiones, conoces el global |
        | 0.9 | Excelente (90%) | La receta funciona muy bien |
        | 0.7 | Buena (70%) | La receta funciona bastante bien |
        | 0.5 | Regular (50%) | La receta funciona a medias |
        | 0.0 | No funciona (0%) | La receta no sirve |
        
        **En nuestro caso: R² = 1.0**
        
        **¿Por qué es perfecto?**
        Porque el bienestar global se calcula como el PROMEDIO de las 6 dimensiones. 
        Es como preguntar: "¿Cuánto es el promedio de 6 notas?" y usar las 6 notas 
        para predecirlo - ¡siempre funciona!
        
        **¿Qué significa en la práctica?**
        - Las 6 dimensiones explican el 100% del bienestar
        - No hay factores externos importantes
        - La escala Ryff-29 es muy válida
        """)
    
    with st.expander("🔮 Odds Ratios (Regresión Logística)"):
        st.markdown("""
        **Los Odds Ratios indican CUÁNTO cambia algo.**
        
        **Imagina que quieres saber si un paraguas te protege de la lluvia:**
        - Sin paraguas: 80% de probabilidad de mojarte
        - Con paraguas: 20% de probabilidad de mojarte
        - Odds Ratio: 0.25 (te protege 4 veces más)
        
        **En nuestro caso con Autoaceptación (OR = 0.18):**
        - Por cada punto que SUBE la Autoaceptación
        - La probabilidad de tener bienestar BAJO se reduce en un 82%
        
        **En términos simples:**
        - Autoaceptación alta = "Escudo protector" contra problemas
        - Cada punto de mejora cuenta mucho
        """)
    
    st.divider()
    
    # Tipos de regresión
    st.markdown("### 📊 Tipos de Regresión que Usamos")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        #### 📈 Regresión Lineal
        **Qué hace:** Predice un número continuo
        
        **Ejemplo:** Predecir el bienestar global (4.52)
        
        **Cuándo usarla:** Cuando el resultado es un número
        
        **Nuestros resultados:**
        - R² = 1.0 (perfecto)
        - Todas las dimensiones son significativas
        """)
        
        st.markdown("""
        #### 📊 Regresión Logística
        **Qué hace:** Predice sí/no (categoría)
        
        **Ejemplo:** Predecir si un estudiante tiene bienestar bajo/alto
        
        **Cuándo usarla:** Cuando el resultado es una categoría
        
        **Nuestros resultados:**
        - Precisión = 99.6%
        - AUC-ROC = 0.99
        """)
    
    with col2:
        st.markdown("""
        #### 🔧 Ridge (L2)
        **Qué hace:** Regresión que evita "memorizar" datos
        
        **Analogía:** Como un estudiante que aprende concepts, no fórmulas
        
        **Cuándo usarla:** Cuando hay muchas variables
        
        **Nuestros resultados:**
        - Mantiene todas las variables
        - Mejor generalización
        """)
        
        st.markdown("""
        #### ✂️ Lasso (L1)
        **Qué hace:** Regresión que simplifica (elimina variables innecesarias)
        
        **Analogía:** Como un estudiante que estudia solo lo importante
        
        **Cuándo usarla:** Cuando quieres identificar factores clave
        
        **Nuestros resultados:**
        - Selecciona las variables más importantes
        - Modelo más simple
        """)

def show_clustering_explanation():
    """Explicación de clustering"""
    st.markdown("## 👥 ¿Qué es el Clustering?")
    
    with st.expander("🎯 Explicación Simple", expanded=True):
        st.markdown("""
        **El clustering es como "agrupar personas por características similares."**
        
        **Ejemplo cotidiano:**
        - En una fiesta, la gente se agrupa naturalmente:
          - Grupo 1: Los que bailan
          - Grupo 2: Los que conversan
          - Grupo 3: Los que comen
        
        **En nuestro análisis:**
        - Identificamos 2 perfiles de estudiantes:
          - **Perfil 1:** Estudiantes con bienestar alto en todo
          - **Perfil 2:** Estudiantes con áreas de mejora
        
        **¿Para qué sirve?**
        - Personalizar intervenciones
        - Entender diferentes necesidades
        - Crear programas específicos por grupo
        """)
    
    with st.expander("📊 ¿Qué es Silhouette?"):
        st.markdown("""
        **Silhouette mide qué TAN BIEN agrupados están los elementos.**
        
        | Silhouette | Significado | Ejemplo |
        |------------|-------------|---------|
        | 1.0 | Perfecto | Grupos muy claros y separados |
        | 0.7 | Bueno | Grupos bien definidos |
        | 0.5 | Regular | Grupos aceptables |
        | 0.3 | Pobre | Grupos poco claros |
        | 0.0 | Malo | Sin grupos definidos |
        
        **Nuestro resultado: Silhouette = 0.31**
        
        **Interpretación:**
        - Los perfiles no están muy diferenciados
        - Los estudiantes tienen características similares
        - Hay variabilidad dentro de cada grupo
        - Sugerencia: Usar más clusters o diferentes variables
        """)
    
    with st.expander("🔍 ¿Cómo funciona K-Means?"):
        st.markdown("""
        **K-Means es como encontrar el "centro" de cada grupo.**
        
        **Paso 1:** Elegir cuántos grupos queremos (K=2)
        
        **Paso 2:** Poner puntos aleatorios como centros
        
        **Paso 3:** Asignar cada estudiante al centro más cercano
        
        **Paso 4:** Recalcular los centros
        
        **Paso 5:** Repetir hasta que no cambie
        
        **Ejemplo visual:**
        ```
        ANTES:                    DESPUÉS:
        
        .   .   .   .            Grupo 1: ●●●●
          .   .   .              Grupo 2: ○○○○○
        .   .   .   .
        ```
        """)
    
    st.divider()
    
    # Métodos de clustering
    st.markdown("### 🔬 Métodos de Clustering que Usamos")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        #### 🎯 K-Means
        **Qué hace:** Agrupa por distancia al centro
        
        **Ventajas:**
        - Rápido y simple
        - Funciona bien con muchos datos
        
        **Desventajas:**
        - Hay que elegir K (número de grupos)
        - Asume grupos redondos
        
        **Nuestro resultado:** 2 grupos identificados
        """)
    
    with col2:
        st.markdown("""
        #### 🔍 DBSCAN
        **Qué hace:** Agrupa por densidad de puntos
        
        **Ventajas:**
        - No hay que elegir K
        - Encuentra formas irregulares
        
        **Desventajas:**
        - Sensible a parámetros
        - No funciona con grupos de diferentes tamaños
        
        **Nuestro resultado:** 3 grupos detectados
        """)
    
    with col3:
        st.markdown("""
        #### 🌳 Jerárquico
        **Qué hace:** Crea un "árbol" de grupos
        
        **Ventajas:**
        - Visual intuitivo (dendrograma)
        - No hay que elegir K
        
        **Desventajas:**
        - Lento con muchos datos
        - Difícil de interpretar
        
        **Nuestro resultado:** 2-3 grupos óptimos
        """)

def show_ml_explanation():
    """Explicación de Machine Learning"""
    st.markdown("## 🤖 ¿Qué es Machine Learning?")
    
    with st.expander("🎯 Explicación Simple", expanded=True):
        st.markdown("""
        **Machine Learning es como "enseñarle a una computadora a aprender de ejemplos."**
        
        **Ejemplo cotidiano:**
        - Le muestras 100 fotos de gatos y perros
        - La computadora aprende a distinguirlos
        - Luego puede identificar nuevos animales
        
        **En nuestro caso:**
        - Le mostramos datos de bienestar de 281 estudiantes
        - El modelo aprende a predecir quién tiene bienestar bajo/alto
        - Puede identificar estudiantes en riesgo
        """)
    
    with st.expander("📊 ¿Qué modelos usamos?"):
        st.markdown("""
        | Modelo | Analogía | Mejor para |
        |--------|----------|------------|
        | **Random Forest** | Comité de expertos | Datos con muchas variables |
        | **SVM** | Separar con una línea | Clasificación precisa |
        | **Gradient Boosting** | Equipo que mejora | Predicción precisa |
        | **Red Neuronal** | Cerebro artificial | Patrones complejos |
        
        **En nuestro análisis:**
        - Todos lograron **100% de precisión**
        - Esto confirma que las dimensiones predicen perfectamente el bienestar
        """)
    
    with st.expander("🎯 ¿Qué es AUC-ROC?"):
        st.markdown("""
        **AUC-ROC mide qué tan BUENOS son nuestros modelos para distinguir entre grupos.**
        
        | AUC-ROC | Significado | Ejemplo |
        |---------|-------------|---------|
        | 1.0 | Perfecto | Distingue todos los casos correctamente |
        | 0.9 | Excelente | Distingue casi todos los casos |
        | 0.7 | Aceptable | Distingue la mayoría de casos |
        | 0.5 | Aleatorio | Como adivinar |
        | 0.0 | Peor que aleatorio | Siempre se equivoca |
        
        **Nuestro resultado: AUC-ROC = 0.99-1.0**
        
        **Interpretación:**
        - Los modelos distinguen excelentemente entre bienestar alto y bajo
        - Se pueden usar para identificar estudiantes en riesgo
        - Son herramientas confiables para la toma de decisiones
        """)
    
    st.divider()
    
    # Random Forest detallado
    st.markdown("### 🌳 ¿Qué es Random Forest?")
    
    with st.expander("📖 Explicación Detallada", expanded=True):
        st.markdown("""
        **Random Forest es como un "comité de expertos" que toma decisiones juntos.**
        
        **Cómo funciona:**
        1. Se crean muchos "árboles de decisión" (como 100 expertos)
        2. Cada árbol mira diferentes aspectos de los datos
        3. Cada árbol da su opinión
        4. La decisión final es la mayoría
        
        **Ejemplo:**
        ```
        Árbol 1: "Este estudiante tiene bienestar ALTO"
        Árbol 2: "Este estudiante tiene bienestar ALTO"
        Árbol 3: "Este estudiante tiene bienestar BAJO"
        Árbol 4: "Este estudiante tiene bienestar ALTO"
        ...
        
        Decisión final: "Bienestar ALTO" (mayoría)
        ```
        
        **¿Por qué es bueno?**
        - Más preciso que un solo árbol
        - Menos propenso a "memorizar" datos
        - Puede manejar muchos tipos de datos
        - Da información sobre qué variables son importantes
        """)
    
    # Red Neuronal detallada
    st.markdown("### 🧠 ¿Qué es una Red Neuronal?")
    
    with st.expander("📖 Explicación Detallada", expanded=True):
        st.markdown("""
        **Una Red Neuronal es como un "cerebro artificial" que aprende.**
        
        **Cómo funciona:**
        1. Tiene "neuronas" organizadas en capas
        2. La primera capa recibe los datos
        3. Cada neurona procesa la información
        4. La última capa da el resultado
        
        **Ejemplo simplificado:**
        ```
        Entrada: Autoaceptación=4.8, Relaciones=4.2, ...
                    ↓
        Capa Oculta 1: [neurona1, neurona2, neurona3]
                    ↓
        Capa Oculta 2: [neurona1, neurona2]
                    ↓
        Salida: Bienestar = 4.52
        ```
        
        **¿Por qué es bueno?**
        - Puede encontrar patrones muy complejos
        - Se adapta a diferentes tipos de datos
        - Es muy flexible
        
        **¿Cuándo usarla?**
        - Cuando hay muchos datos
        - Cuando los patrones son complejos
        - Cuando otros modelos no funcionan bien
        """)

def show_statistics_explanation():
    """Explicación de estadísticas"""
    st.markdown("## 📊 ¿Qué son las Estadísticas?")
    
    with st.expander("🎯 Explicación Simple", expanded=True):
        st.markdown("""
        **Las estadísticas son como "resúmenes inteligentes" de los datos.**
        
        **Imagina que tienes 281 calificaciones.** En lugar de mirar cada una, 
        puedes usar estadísticas para entender el panorama general:
        
        - **Media:** El promedio de todas las calificaciones
        - **Mediana:** La calificación del estudiante del medio
        - **Desviación:** Qué tan diferentes son las calificaciones entre sí
        """)
    
    with st.expander("📊 ¿Qué es una correlación?"):
        st.markdown("""
        **Una correlación mide cómo se relacionan dos cosas.**
        
        | Correlación | Significado | Ejemplo |
        |-------------|-------------|---------|
        | +1.0 | Relación perfecta positiva | Más estudio = Mejores notas |
        | +0.7 | Relación fuerte positiva | Autoaceptación y Crecimiento |
        | +0.4 | Relación moderada positiva | Relaciones y Propósito |
        | 0.0 | Sin relación | Calamaño de pies y notas |
        | -0.4 | Relación moderada negativa | Estrés y bienestar |
        | -0.7 | Relación fuerte negativa | Depresión y bienestar |
        | -1.0 | Relación perfecta negativa | Más estrés = Menos bienestar |
        
        **En nuestro caso:**
        - Autoaceptación ↔ Crecimiento: r = 0.72 (fuerte)
        - Autonomía ↔ Dominio: r = 0.68 (moderada-fuerte)
        
        **¿Qué significa?**
        - Cuando una dimensión mejora, las demás también tienden a mejorar
        - El bienestar es un sistema interconectado
        """)
    
    with st.expander("📈 ¿Qué es un p-valor?"):
        st.markdown("""
        **El p-valor mide si un resultado es "real" o por "casualidad".**
        
        | p-valor | Significado | Ejemplo |
        |---------|-------------|---------|
        | < 0.01 | Muy significativo | Casi seguro que es real |
        | < 0.05 | Significativo | Probablemente es real |
        | < 0.10 | Marginal | Podría ser real |
        | > 0.10 | No significativo | Podría ser casualidad |
        
        **En nuestro caso:**
        - Todos los p-valores son < 0.05
        - Los resultados son estadísticamente significativos
        - Podemos confiar en los hallazgos
        
        **Regla simple:**
        - p < 0.05 → "Esto es real"
        - p > 0.05 → "Esto podría ser casualidad"
        """)
    
    st.divider()
    
    # Glosario
    st.markdown("### 📖 Glossario de Términos")
    
    glossary = {
        'R² (R cuadrado)': 'Mide qué tan bien un modelo predice el resultado. Va de 0 a 1.',
        'p-valor': 'Mide si un resultado es estadísticamente significativo. Menor a 0.05 es bueno.',
        'Correlación': 'Mide cómo se relacionan dos variables. Va de -1 a +1.',
        'Media': 'El promedio de los datos.',
        'Mediana': 'El valor del medio cuando los datos están ordenados.',
        'Desviación Estándar': 'Qué tan dispersos están los datos de la media.',
        'Odds Ratio': 'Mide cuánto cambia la probabilidad de algo.',
        'AUC-ROC': 'Mide la capacidad de un modelo para distinguir entre grupos.',
        'Silhouette': 'Mide qué tan bien agrupados están los elementos en clustering.',
        'PCA': 'Técnica para reducir la dimensionalidad de los datos.',
        'K-Means': 'Algoritmo de clustering que agrupa por distancia al centro.',
        'Random Forest': 'Modelo que usa muchos árboles de decisión para predecir.',
        'SVM': 'Modelo que separa datos con una línea o hiperplano.',
        'Red Neuronal': 'Modelo inspirado en el cerebro humano que aprende patrones.'
    }
    
    col1, col2 = st.columns(2)
    
    with col1:
        for term, definition in list(glossary.items())[:7]:
            st.markdown(f"**{term}:** {definition}")
    
    with col2:
        for term, definition in list(glossary.items())[7:]:
            st.markdown(f"**{term}:** {definition}")

if __name__ == "__main__":
    show_explanations()
