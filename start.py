import subprocess
import sys
import os

port = os.environ.get('PORT', '8080')

print(f"Iniciando Streamlit en puerto {port}...")

subprocess.run([
    sys.executable, "-m", "streamlit", "run", "app/main.py",
    "--server.port", port,
    "--server.address", "0.0.0.0",
    "--server.headless", "true",
    "--browser.gatherUsageStats", "false"
])
