"""Script de prueba para modelos de regresión."""

import yaml
import pandas as pd

from src.data.processor import DataProcessor
from src.analysis.factors import FactorAnalysis

# Cargar configuración
config = yaml.safe_load(open("configs/config.yaml", encoding="utf-8"))

# Cargar datos
print("Cargando datos...")
df = pd.read_csv(
    "data/raw/Escala de Bienestar Psicológico (respuestas) - Respuestas de formulario 1.csv",
    encoding="utf-8-sig"
)

# Procesar
processor = DataProcessor(config)
df_processed, _ = processor.prepare_analysis_data(df)

# Inicializar análisis de factores
fa = FactorAnalysis(config)

# 1. Regresión Lineal
print("\n" + "="*60)
print("REGRESIÓN LINEAL MÚLTIPLE")
print("="*60)
r = fa.regression_analysis(df_processed)
print(f"R² = {r.get('r_squared', 0):.4f}")
print(f"R² ajustado = {r.get('adj_r_squared', 0):.4f}")
print(f"Observaciones = {r.get('n_observations', 0)}")
print("\nFactores:")
for f in r.get("factors", []):
    sig = "***" if f.significant else ""
    print(f"  {f.factor}: beta = {f.std_coefficient:.4f}, p = {f.p_value:.4f} {sig}")

# 2. Regresión Logística
print("\n" + "="*60)
print("REGRESIÓN LOGÍSTICA (Bienestar bajo vs alto)")
print("="*60)
lr = fa.logistic_regression(df_processed)
print(f"Accuracy = {lr.get('accuracy', 0):.4f}")
print(f"AUC-ROC = {lr.get('auc_roc', 0):.4f}")
print(f"Umbral = {lr.get('threshold', 3.5)}")
print("\nOdds Ratios:")
for factor, or_val in lr.get("odds_ratios", {}).items():
    print(f"  {factor}: OR = {or_val:.4f}")
print("\nFactores significativos:")
for f in lr.get("significant_factors", []):
    print(f"  {f['factor']}: OR = {f['odds_ratio']:.4f}, p = {f['p_value']:.4f}")

# 3. Regresión Ridge
print("\n" + "="*60)
print("REGRESIÓN RIDGE (L2)")
print("="*60)
rr = fa.ridge_regression(df_processed)
print(f"R² = {rr.get('r_squared', 0):.4f}")
print(f"Alpha = {rr.get('alpha', 1.0)}")
print("\nCoeficientes:")
for factor, coef in rr.get("coefficients", {}).items():
    print(f"  {factor}: coef = {coef:.4f}")

# 4. Regresión Lasso
print("\n" + "="*60)
print("REGRESIÓN LASSO (L1)")
print("="*60)
lr = fa.lasso_regression(df_processed)
print(f"R² = {lr.get('r_squared', 0):.4f}")
print(f"Alpha = {lr.get('alpha', 1.0)}")
print("\nCoeficientes:")
for factor, coef in lr.get("coefficients", {}).items():
    print(f"  {factor}: coef = {coef:.4f}")

# 5. Regresión Stepwise
print("\n" + "="*60)
print("REGRESIÓN STEPWISE (Selección de variables)")
print("="*60)
sr = fa.stepwise_regression(df_processed)
print(f"Variables seleccionadas = {sr.get('n_selected', 0)}")
print(f"R² = {sr.get('r_squared', 0):.4f}")
print(f"R² ajustado = {sr.get('adj_r_squared', 0):.4f}")
print("\nHistorial de selección:")
for step in sr.get("step_history", []):
    print(f"  Paso {step['step']}: {step['added']} (R² adj = {step['adj_r_squared']:.4f})")
print("\nCoeficientes finales:")
for factor, coef in sr.get("coefficients", {}).items():
    print(f"  {factor}: coef = {coef:.4f}")

# 6. Regresión Polinómica
print("\n" + "="*60)
print("REGRESIÓN POLINÓMICA (Grado 2)")
print("="*60)
pr = fa.polynomial_regression(df_processed)
print(f"R² = {pr.get('r_squared', 0):.4f}")
print(f"R² ajustado = {pr.get('adj_r_squared', 0):.4f}")
print(f"Features = {pr.get('n_features', 0)}")

print("\n" + "="*60)
print("TODOS LOS MODELOS COMPLETADOS EXITOSAMENTE")
print("="*60)
