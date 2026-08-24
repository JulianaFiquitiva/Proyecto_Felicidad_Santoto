"""
Generador de dashboard HTML estático con Plotly.
"""

import pandas as pd
import yaml
import glob
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

# Cargar configuración
with open("configs/config.yaml", "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)

# Cargar y procesar datos
from src.data.processor import DataProcessor
from src.analysis.clustering import ClusteringAnalysis

csv_files = glob.glob("data/raw/*.csv")
df_raw = pd.read_csv(csv_files[0], encoding="utf-8-sig")

processor = DataProcessor(config)
df, report = processor.prepare_analysis_data(df_raw)

# Clustering
cluster_analysis = ClusteringAnalysis(config)
df = cluster_analysis.fit_clusters(df)
profiles = cluster_analysis.get_cluster_profiles(df)

dimensions = config["survey"]["dimensions"]
dim_names = {d["id"]: d["name"] for d in dimensions}

# Crear figura con subplots
fig = make_subplots(
    rows=3, cols=2,
    subplot_titles=(
        "Distribución por Dimensiones",
        "Bienestar Global",
        "Correlaciones entre Dimensiones",
        "Comparación por Género",
        "Perfiles de Estudiantes",
        "Estadísticas Descriptivas"
    ),
    specs=[
        [{"type": "box"}, {"type": "indicator"}],
        [{"type": "heatmap"}, {"type": "bar"}],
        [{"type": "pie"}, {"type": "table"}]
    ]
)

# 1. Box plot por dimensiones
score_cols = [f"score_{d['id']}" for d in dimensions]
score_cols = [c for c in score_cols if c in df.columns]

for col in score_cols:
    dim_id = col.replace("score_", "")
    fig.add_trace(
        go.Box(y=df[col], name=dim_names.get(dim_id, dim_id), boxmean=True),
        row=1, col=1
    )

# 2. Indicator de bienestar global
if "wellbeing_global" in df.columns:
    avg = df["wellbeing_global"].mean()
    fig.add_trace(
        go.Indicator(
            mode="gauge+number",
            value=avg,
            title={"text": "Promedio Global"},
            gauge={
                "axis": {"range": [1, 6]},
                "bar": {"color": "darkblue"},
                "steps": [
                    {"range": [1, 2.4], "color": "lightcoral"},
                    {"range": [2.4, 4.2], "color": "lightyellow"},
                    {"range": [4.2, 6], "color": "lightgreen"},
                ],
            }
        ),
        row=1, col=2
    )

# 3. Mapa de calor de correlaciones
corr_data = df[score_cols].corr()
dim_labels = [dim_names.get(c.replace("score_", ""), c) for c in score_cols]
fig.add_trace(
    go.Heatmap(
        z=corr_data.values,
        x=dim_labels,
        y=dim_labels,
        colorscale="RdBu_r",
        zmin=-1, zmax=1,
        text=np.round(corr_data.values, 2),
        texttemplate="%{text}",
    ),
    row=2, col=1
)

# 4. Comparación por género
if "Género" in df.columns:
    gender_means = df.groupby("Género")[score_cols].mean()
    for col in score_cols:
        dim_id = col.replace("score_", "")
        fig.add_trace(
            go.Bar(
                name=dim_names.get(dim_id, dim_id),
                x=gender_means.index,
                y=gender_means[col],
                showlegend=False,
            ),
            row=2, col=2
        )

# 5. Perfiles de clustering
if profiles:
    cluster_sizes = [p.size for p in profiles]
    cluster_labels = [f"Perfil {p.cluster_id}" for p in profiles]
    fig.add_trace(
        go.Pie(
            labels=cluster_labels,
            values=cluster_sizes,
        ),
        row=3, col=1
    )

# 6. Tabla de estadísticas
stats_data = []
for col in score_cols:
    dim_id = col.replace("score_", "")
    stats_data.append([
        dim_names.get(dim_id, dim_id),
        f"{df[col].mean():.3f}",
        f"{df[col].std():.3f}",
        f"{df[col].min():.2f}",
        f"{df[col].max():.2f}",
    ])

fig.add_trace(
    go.Table(
        header=dict(values=["Dimensión", "Media", "DE", "Mín", "Máx"]),
        cells=dict(values=list(zip(*stats_data)))
    ),
    row=3, col=2
)

# Actualizar layout
fig.update_layout(
    height=1200,
    title_text="Dashboard de Bienestar Psicológico Estudiantil - Universidad Santo Tomás",
    showlegend=False,
)

# Guardar como HTML
fig.write_html("reports/dashboard.html")
print("Dashboard generado: reports/dashboard.html")
