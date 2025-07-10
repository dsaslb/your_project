import schedule
import time
import subprocess
import json
from datetime import datetime

def run_health_check():
    """?ъ뒪泥댄겕 ?ㅽ뻾"""
    try:
        result = subprocess.run(
            ["powershell", "-ExecutionPolicy", "Bypass", "-File", "scripts/health_check.ps1"],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        # 寃곌낵 ???
        health_data = {
            "timestamp": datetime.now().isoformat(),
            "exit_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr
        }
        
        with open("logs/health_check.json", "w") as f:
            json.dump(health_data, f, indent=2)
        
        print(f"Health check completed: {datetime.now()}")
        
    except Exception as e:
        print(f"Health check failed: {e}")

def main():
    # 5遺꾨쭏???ъ뒪泥댄겕 ?ㅽ뻾
    schedule.every(5).minutes.do(run_health_check)
    
    # ?쒖옉 ??利됱떆 ?ㅽ뻾
    run_health_check()
    
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    main()
