# Your Program 모니터링 설정 스크립트
# 시스템 성능, 로그, 알림 모니터링 자동화

$OutputEncoding = [Console]::OutputEncoding = [Text.Encoding]::UTF8

Write-Host "📊 Your Program Monitoring Setup (모니터링 설정)" -ForegroundColor Green
Write-Host "=================================================" -ForegroundColor Cyan

# 모니터링 설정 (참조용)
$script:monitoringConfig = @{
    "log_retention_days" = 30
    "performance_check_interval" = 300  # 5분
    "disk_usage_threshold" = 80  # 80%
    "memory_usage_threshold" = 85  # 85%
    "cpu_usage_threshold" = 90  # 90%
    "database_connection_timeout" = 10  # 10초
    "api_response_time_threshold" = 5000  # 5초
}

function Initialize-LogMonitoring {
    Write-Host "`n📝 Setting up log monitoring (로그 모니터링 설정)..." -ForegroundColor Yellow
    
    # 로그 디렉토리 생성
    $logDirs = @("logs", "logs/errors", "logs/performance", "logs/security")
    foreach ($dir in $logDirs) {
        if (!(Test-Path $dir)) {
            New-Item -ItemType Directory -Path $dir -Force
            Write-Host "   ✅ Created directory: $dir" -ForegroundColor Green
        }
    }
    
    # 로그 로테이션 설정
    $logrotateConfig = @"
# Your Program Log Rotation Configuration
logs/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    create 644 root root
    postrotate
        systemctl reload your_program
    endscript
}
"@
    
    $logrotateConfig | Out-File -FilePath "logrotate.conf" -Encoding UTF8
    Write-Host "   ✅ Log rotation configuration created" -ForegroundColor Green
}

function Initialize-PerformanceMonitoring {
    Write-Host "`n⚡ Setting up performance monitoring (성능 모니터링 설정)..." -ForegroundColor Yellow
    
    # 성능 모니터링 스크립트 생성
    $perfScript = @'
import psutil
import time
import json
from datetime import datetime

def get_system_metrics():
    """시스템 메트릭 수집"""
    return {
        "timestamp": datetime.now().isoformat(),
        "cpu_percent": psutil.cpu_percent(interval=1),
        "memory_percent": psutil.virtual_memory().percent,
        "disk_percent": psutil.disk_usage('/').percent,
        "network_io": psutil.net_io_counters()._asdict()
    }

def check_thresholds(metrics, thresholds):
    """임계값 체크"""
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
    
    # 메트릭 저장
    with open("logs/performance/metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)
    
    # 알림 처리
    if alerts:
        with open("logs/performance/alerts.log", "a") as f:
            for alert in alerts:
                f.write(f"{datetime.now()}: {alert}\n")
    
    print(json.dumps(metrics, indent=2))
'@
    
    $perfScript | Out-File -FilePath "scripts/performance_monitor.py" -Encoding UTF8
    Write-Host "   ✅ Performance monitoring script created" -ForegroundColor Green
}

function Initialize-HealthCheckScheduler {
    Write-Host "`n🏥 Setting up health check scheduler (헬스체크 스케줄러 설정)..." -ForegroundColor Yellow
    
    # 헬스체크 스케줄러 스크립트 생성
    $schedulerScript = @'
import schedule
import time
import subprocess
import json
from datetime import datetime

def run_health_check():
    """헬스체크 실행"""
    try:
        result = subprocess.run(
            ["powershell", "-ExecutionPolicy", "Bypass", "-File", "scripts/health_check.ps1"],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        # 결과 저장
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
    # 5분마다 헬스체크 실행
    schedule.every(5).minutes.do(run_health_check)
    
    # 시작 시 즉시 실행
    run_health_check()
    
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    main()
'@
    
    $schedulerScript | Out-File -FilePath "scripts/health_scheduler.py" -Encoding UTF8
    Write-Host "   ✅ Health check scheduler created" -ForegroundColor Green
}

function Initialize-AlertSystem {
    Write-Host "`n🔔 Setting up alert system (알림 시스템 설정)..." -ForegroundColor Yellow
    
    # 알림 시스템 스크립트 생성
    $alertScript = @'
import smtplib
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json
from datetime import datetime

class AlertSystem:
    def __init__(self, config):
        self.config = config
        self.smtp_server = config.get("smtp_server", "smtp.gmail.com")
        self.smtp_port = config.get("smtp_port", 587)
        self.email = config.get("email")
        self.password = config.get("password")
        self.webhook_url = config.get("webhook_url")
    
    def send_email_alert(self, subject, message):
        """이메일 알림 발송"""
        if not self.email or not self.password:
            return False
        
        try:
            msg = MIMEMultipart()
            msg["From"] = self.email
            msg["To"] = self.email
            msg["Subject"] = f"[Your Program Alert] {subject}"
            
            msg.attach(MIMEText(message, "plain"))
            
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.email, self.password)
            server.send_message(msg)
            server.quit()
            
            return True
        except Exception as e:
            print(f"Email alert failed: {e}")
            return False
    
    def send_webhook_alert(self, message):
        """웹훅 알림 발송"""
        if not self.webhook_url:
            return False
        
        try:
            payload = {
                "text": f"[Your Program Alert] {message}",
                "timestamp": datetime.now().isoformat()
            }
            
            response = requests.post(self.webhook_url, json=payload, timeout=10)
            return response.status_code == 200
        except Exception as e:
            print(f"Webhook alert failed: {e}")
            return False
    
    def send_alert(self, subject, message, alert_type="both"):
        """알림 발송"""
        success = True
        
        if alert_type in ["email", "both"]:
            success &= self.send_email_alert(subject, message)
        
        if alert_type in ["webhook", "both"]:
            success &= self.send_webhook_alert(message)
        
        return success

# 설정 예시
config = {
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "email": "your-email@gmail.com",
    "password": "your-app-password",
    "webhook_url": "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
}

alert_system = AlertSystem(config)
'@
    
    $alertScript | Out-File -FilePath "scripts/alert_system.py" -Encoding UTF8
    Write-Host "   ✅ Alert system created" -ForegroundColor Green
}

function Initialize-DatabaseMonitoring {
    Write-Host "`n🗄️ Setting up database monitoring (데이터베이스 모니터링 설정)..." -ForegroundColor Yellow
    
    # DB 모니터링 스크립트 생성
    $dbScript = @'
import sqlite3
import json
from datetime import datetime
import os

def check_database_health():
    """데이터베이스 상태 확인"""
    try:
        # DB 연결 테스트
        conn = sqlite3.connect("instance/your_program.db")
        cursor = conn.cursor()
        
        # 테이블 정보 수집
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        # 각 테이블의 레코드 수 확인
        table_stats = {}
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            table_stats[table] = count
        
        # DB 크기 확인
        db_size = os.path.getsize("instance/your_program.db")
        
        # 연결 시간 측정
        start_time = datetime.now()
        cursor.execute("SELECT 1")
        cursor.fetchone()
        response_time = (datetime.now() - start_time).total_seconds() * 1000
        
        conn.close()
        
        health_data = {
            "timestamp": datetime.now().isoformat(),
            "status": "healthy",
            "tables": table_stats,
            "db_size_mb": round(db_size / (1024 * 1024), 2),
            "response_time_ms": round(response_time, 2),
            "total_records": sum(table_stats.values())
        }
        
        # 결과 저장
        with open("logs/database_health.json", "w") as f:
            json.dump(health_data, f, indent=2)
        
        return health_data
        
    except Exception as e:
        error_data = {
            "timestamp": datetime.now().isoformat(),
            "status": "error",
            "error": str(e)
        }
        
        with open("logs/database_health.json", "w") as f:
            json.dump(error_data, f, indent=2)
        
        return error_data

if __name__ == "__main__":
    result = check_database_health()
    print(json.dumps(result, indent=2))
'@
    
    $dbScript | Out-File -FilePath "scripts/database_monitor.py" -Encoding UTF8
    Write-Host "   ✅ Database monitoring script created" -ForegroundColor Green
}

function Initialize-AutoBackup {
    Write-Host "`n💾 Setting up auto backup (자동 백업 설정)..." -ForegroundColor Yellow
    
    # 자동 백업 스케줄러 생성
    $backupScript = @'
import schedule
import time
import subprocess
from datetime import datetime

def run_backup():
    """자동 백업 실행"""
    try:
        print(f"Starting backup: {datetime.now()}")
        
        result = subprocess.run(
            ["powershell", "-ExecutionPolicy", "Bypass", "-File", "scripts/backup_project.ps1"],
            capture_output=True,
            text=True,
            timeout=300
        )
        
        if result.returncode == 0:
            print(f"Backup completed successfully: {datetime.now()}")
        else:
            print(f"Backup failed: {result.stderr}")
        
    except Exception as e:
        print(f"Backup error: {e}")

def main():
    # 매일 새벽 2시에 백업 실행
    schedule.every().day.at("02:00").do(run_backup)
    
    # 매주 일요일 새벽 3시에 전체 백업
    schedule.every().sunday.at("03:00").do(run_backup)
    
    print("Auto backup scheduler started...")
    
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    main()
'@
    
    $backupScript | Out-File -FilePath "scripts/auto_backup.py" -Encoding UTF8
    Write-Host "   ✅ Auto backup scheduler created" -ForegroundColor Green
}

# 메인 실행
Write-Host "`n🚀 Starting monitoring setup..." -ForegroundColor Cyan

Initialize-LogMonitoring
Initialize-PerformanceMonitoring
Initialize-HealthCheckScheduler
Initialize-AlertSystem
Initialize-DatabaseMonitoring
Initialize-AutoBackup

Write-Host "`n✅ Monitoring setup completed!" -ForegroundColor Green
Write-Host "`n📋 Next steps:" -ForegroundColor Yellow
Write-Host "   1. Configure alert settings in scripts/alert_system.py" -ForegroundColor White
Write-Host "   2. Start monitoring services:" -ForegroundColor White
Write-Host "      - python scripts/health_scheduler.py" -ForegroundColor White
Write-Host "      - python scripts/auto_backup.py" -ForegroundColor White
Write-Host "   3. Set up log rotation: logrotate -f logrotate.conf" -ForegroundColor White
Write-Host "   4. Monitor logs in logs/ directory" -ForegroundColor White

Write-Host "`n🎉 Your Program monitoring system is ready!" -ForegroundColor Green 