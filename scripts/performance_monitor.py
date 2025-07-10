import psutil
import time
import json
from datetime import datetime

def get_system_metrics():
    """?쒖뒪??硫뷀듃由??섏쭛"""
    return {
        "timestamp": datetime.now().isoformat(),
        "cpu_percent": psutil.cpu_percent(interval=1),
        "memory_percent": psutil.virtual_memory().percent,
        "disk_percent": psutil.disk_usage('/').percent,
        "network_io": psutil.net_io_counters()._asdict()
    }

def check_thresholds(metrics, thresholds):
    """?꾧퀎媛?泥댄겕"""
    alerts = []
    
    if metrics["cpu_percent"] > thresholds["cpu_usage_threshold"]:
        alerts.append(f"CPU usage high: {metrics['cpu_percent']}%")
    
    if metrics["memory_percent"] > thresholds["memory_usage_threshold"]:
        alerts.append(f"Memory usage high: {metrics['memory_percent']}%")
    
    if metrics["disk_percent"] > thresholds["disk_usage_threshold"]:
        alerts.append(f"Disk usage high: {metrics['disk_percent']}%")
    
    return alerts

if __name__ == "__main__":
    thresholds = {
        "cpu_usage_threshold": 90,
        "memory_usage_threshold": 85,
        "disk_usage_threshold": 80
    }
    
    metrics = get_system_metrics()
    alerts = check_thresholds(metrics, thresholds)
    
    # 硫뷀듃由????
    with open("logs/performance/metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)
    
    # ?뚮┝ 泥섎━
    if alerts:
        with open("logs/performance/alerts.log", "a") as f:
            for alert in alerts:
                f.write(f"{datetime.now()}: {alert}\n")
    
    print(json.dumps(metrics, indent=2))
