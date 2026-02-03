import psutil
import subprocess
from datetime import datetime

def log_system_metrics():
    with open("system_metrics.log", "a") as f:
        f.write(f"\n===== {datetime.now()} =====\n")
        f.write(f"CPU Usage: {psutil.cpu_percent()}%\n")
        f.write(f"Memory Usage: {psutil.virtual_memory().percent}%\n")

        temp = subprocess.getoutput("vcgencmd measure_temp")
        f.write(f"Temperature: {temp}\n")
