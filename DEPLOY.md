# Análisis de Bienestar Psicológico Estudiantil

Sistema inteligente de análisis y monitoreo del bienestar psicológico de estudiantes de la Universidad Santo Tomás.

## Despliegue en Railway

### Opción 1: Despliegue directo desde GitHub

1. Ve a [Railway.app](https://railway.app)
2. Inicia sesión con tu cuenta de GitHub
3. Haz clic en "New Project"
4. Selecciona "Deploy from GitHub repo"
5. Selecciona este repositorio
6. Railway detectará automáticamente los archivos necesarios
7. Espera a que se complete el despliegue
8. Tu app estará disponible en la URL proporcionada

### Opción 2: Despliegue con Docker

1. Ve a [Railway.app](https://railway.app)
2. Inicia sesión con tu cuenta de GitHub
3. Haz clic en "New Project"
4. Selecciona "Deploy from Dockerfile"
5. Selecciona este repositorio
6. Railway usará el Dockerfile incluido
7. Espera a que se complete el despliegue

### Variables de Entorno (Opcional)

Si necesitas configurar la API de Gemini, agrega estas variables en Railway:

```
GEMINI_API_KEY=tu_api_key_aqui
```

### Configuración en config.yaml

Para que funcione en Railway, necesitas configurar la API key como variable de entorno o usar la configuración de Railway.

## Desarrollo Local

```bash
# Instalar dependencias
pip install -r requirements.txt

# Ejecutar la aplicación
streamlit run app/main.py
```

## Estructura del Proyecto

```
├── app/
│   └── main.py          # Aplicación principal
├── configs/
│   └── config.yaml      # Configuración (no subir a git)
├── data/                # Datos (no subir a git)
├── reports/             # Reportes generados
├── requirements.txt     # Dependencias
├── Dockerfile          # Configuración Docker
├── railway.json        # Configuración Railway
└── Procfile            # Commando de inicio
```

## Funcionalidades

- 📊 Análisis estadístico completo
- 🤖 Chatbot con Google Gemini
- 📈 Panel de control interactivo
- 📋 Resúmenes ejecutivos
- 📚 Explicaciones de modelos
- ⚙️ Configuración del sistema

## Tecnologías

- Python 3.11
- Streamlit
- Pandas / NumPy
- Scikit-learn
- Plotly
- Google Gemini AI
