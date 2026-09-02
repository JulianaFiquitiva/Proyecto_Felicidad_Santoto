import subprocess
import sys
import os

port = os.environ.get('PORT', '8080')

print("=" * 50)
print(f"PORT env var: {port}")
print(f"Python: {sys.executable}")
print("=" * 50)

# Limpiar variables de entorno que puedan interferir
env = os.environ.copy()
if 'STREAMLIT_SERVER_PORT' in env:
    del env['STREAMLIT_SERVER_PORT']

cmd = [
    sys.executable, "-m", "streamlit", "run", "app/main.py",
    "--server.port", str(port),
    "--server.address", "0.0.0.0",
    "--server.headless", "true",
    "--browser.gatherUsageStats", "false"
]

print(f"Comando: {' '.join(cmd)}")
print("=" * 50)

subprocess.run(cmd, env=env)
