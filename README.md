# Análisis Estadístico e Inteligente de la Felicidad Estudiantil

**Universidad Santo Tomás**

---

## Descripción

Sistema reproducible en Python para el análisis estadístico de la felicidad estudiantil basado en una escala de 29 ítems tipo Likert organizada en seis dimensiones:

1. **Crecimiento Personal**
2. **Propósito de Vida**
3. **Dominio del Entorno**
4. **Entorno Institucional**
5. **Relaciones Positivas**
6. **Autonomía**

## Objetivos

- Cargar y explorar datos de la encuesta de felicidad estudiantil
- Validar y limpiar la información
- Calcular puntajes por ítem, dimensión e índice global
- Realizar análisis estadístico descriptivo e inferencial
- Evaluar consistencia interna de la escala
- Analizar correlaciones y diferencias entre grupos
- Identificar perfiles de estudiantes mediante clustering
- Generar tablas, visualizaciones y reportes automáticos
- Dashboard interactivo (futura implementación)
- Componente de IA para interpretación de resultados (futura implementación)

## Estructura del Proyecto

```
felicidad-estudiantil/
├── data/
│   ├── raw/              # Datos originales (no modificar)
│   ├── processed/        # Datos limpios y procesados
│   └── external/         # Datos externos adicionales
├── src/
│   ├── data/             # Módulos de carga y limpieza
│   ├── analysis/         # Módulos de análisis estadístico
│   ├── visualization/    # Módulos de gráficos
│   └── utils/            # Funciones auxiliares
├── notebooks/            # Notebooks de exploración
├── reports/
│   └── figures/          # Gráficos generados
├── configs/              # Archivos de configuración
├── tests/                # Pruebas unitarias
├── requirements.txt      # Dependencias
├── pyproject.toml        # Configuración del proyecto
└── config.yaml           # Parámetros de análisis
```

## Instalación

```bash
# Clonar el repositorio
git clone <url-del-repositorio>
cd felicidad-estudiantil

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Instalar dependencias
pip install -r requirements.txt
```

## Uso

1. Colocar los datos crudos en `data/raw/`
2. Ejecutar los notebooks en orden secuencial
3. Los resultados se generarán en `reports/`

## Principios

- **Reproducibilidad**: Todo el análisis puede ejecutarse nuevamente con nueva data
- **Modularidad**: Código organizado en módulos independientes
- **Documentación**: Toda decisión estadística queda registrada
- **Integridad**: Los datos originales nunca se modifican
- **Validación**: Las pruebas estadísticas se verifican antes de aplicarse

## Licencia

Proyecto académico - Universidad Santo Tomás
