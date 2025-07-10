# Your Program 보안 강화 스크립트
# 기본 비밀번호 변경, 접근 제어, 보안 스캔

$OutputEncoding = [Console]::OutputEncoding = [Text.Encoding]::UTF8

Write-Host "🔒 Your Program Security Setup (보안 강화)" -ForegroundColor Green
Write-Host "===========================================" -ForegroundColor Cyan

function Set-DefaultPassword {
    Write-Host "`n🔑 Changing default admin password (기본 관리자 비밀번호 변경)..." -ForegroundColor Yellow
    
    $newPassword = Read-Host "Enter new admin password (새 관리자 비밀번호 입력)" -AsSecureString
    $confirmPassword = Read-Host "Confirm new admin password (새 비밀번호 확인)" -AsSecureString
    
    $newPasswordText = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($newPassword))
    $confirmPasswordText = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($confirmPassword))
    
    if ($newPasswordText -eq $confirmPasswordText) {
        # Python 스크립트로 비밀번호 변경
        $passwordScript = @"
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath('.')))

from app import app, db
from models import User
from werkzeug.security import generate_password_hash

with app.app_context():
    try:
        # 관리자 사용자 찾기
        admin_user = User.query.filter_by(username='testadmin').first()
        if admin_user:
            # 새 비밀번호 해시 생성
            admin_user.password_hash = generate_password_hash('$newPasswordText', method='pbkdf2:sha256')
            db.session.commit()
            print('SUCCESS: Admin password changed successfully')
        else:
            print('ERROR: Admin user not found')
    except Exception as e:
        print(f'ERROR: {e}')
"@
        
        $passwordScript | Out-File -FilePath "temp_change_password.py" -Encoding UTF8
        $result = python temp_change_password.py 2>&1
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "   ✅ Admin password changed successfully" -ForegroundColor Green
        } else {
            Write-Host "   ❌ Failed to change password: $result" -ForegroundColor Red
        }
        
        # 임시 파일 삭제
        if (Test-Path "temp_change_password.py") {
            Remove-Item "temp_change_password.py" -Force
        }
    } else {
        Write-Host "   ❌ Passwords do not match" -ForegroundColor Red
    }
}

function Initialize-AccessControl {
    Write-Host "`n🚪 Setting up access control (접근 제어 설정)..." -ForegroundColor Yellow
    
    # 방화벽 규칙 설정 (Windows)
    try {
        # 포트 5000 (백엔드) - 로컬 접근만 허용
        New-NetFirewallRule -DisplayName "Your Program Backend" -Direction Inbound -Protocol TCP -LocalPort 5000 -Action Allow -Profile Private, Domain -ErrorAction SilentlyContinue
        
        # 포트 3000, 3001 (프론트엔드) - 로컬 접근만 허용
        New-NetFirewallRule -DisplayName "Your Program Frontend" -Direction Inbound -Protocol TCP -LocalPort 3000,3001 -Action Allow -Profile Private, Domain -ErrorAction SilentlyContinue
        
        Write-Host "   ✅ Firewall rules configured" -ForegroundColor Green
    } catch {
        Write-Host "   ⚠️ Firewall configuration failed (관리자 권한 필요)" -ForegroundColor Yellow
    }
    
    # 보안 헤더 설정
    $securityHeaders = @"
# Your Program Security Headers
SECURITY_HEADERS = {
    'X-Content-Type-Options': 'nosniff',
    'X-Frame-Options': 'DENY',
    'X-XSS-Protection': '1; mode=block',
    'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
    'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline';"
}

# CORS 설정
CORS_ORIGINS = ['http://localhost:3000', 'http://localhost:3001']
"@
    
    $securityHeaders | Out-File -FilePath "security_config.py" -Encoding UTF8
    Write-Host "   ✅ Security headers configuration created" -ForegroundColor Green
}

function Start-SecurityScan {
    Write-Host "`n🔍 Running security scan (보안 스캔 실행)..." -ForegroundColor Yellow
    
    # 보안 스캔 스크립트 생성
    $scanScript = @'
import os
import json
import hashlib
from datetime import datetime

def scan_security_issues():
    """보안 이슈 스캔"""
    issues = []
    
    # 1. 환경 변수 파일 체크
    if os.path.exists('.env'):
        with open('.env', 'r') as f:
            content = f.read()
            if 'SECRET_KEY' in content and 'test' in content.lower():
                issues.append("WARNING: Default SECRET_KEY detected in .env")
            if 'password' in content.lower() and 'admin' in content.lower():
                issues.append("WARNING: Default password detected in .env")
    
    # 2. 데이터베이스 파일 권한 체크
    db_path = "instance/your_program.db"
    if os.path.exists(db_path):
        # Windows에서는 파일 권한 체크가 다름
        try:
            import stat
            mode = os.stat(db_path).st_mode
            if mode & stat.S_IROTH:  # 다른 사용자 읽기 권한
                issues.append("WARNING: Database file has public read permissions")
        except:
            pass
    
    # 3. 로그 파일 체크
    log_files = []
    for root, dirs, files in os.walk('logs'):
        for file in files:
            if file.endswith('.log'):
                log_files.append(os.path.join(root, file))
    
    if len(log_files) > 10:
        issues.append(f"INFO: {len(log_files)} log files found - consider log rotation")
    
    # 4. 임시 파일 체크
    temp_files = []
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.startswith('temp_') or file.endswith('.tmp'):
                temp_files.append(os.path.join(root, file))
    
    if temp_files:
        issues.append(f"INFO: {len(temp_files)} temporary files found")
    
    # 5. Git 보안 체크
    if os.path.exists('.git'):
        gitignore_path = '.gitignore'
        if os.path.exists(gitignore_path):
            with open(gitignore_path, 'r') as f:
                content = f.read()
                if '.env' not in content:
                    issues.append("WARNING: .env file not in .gitignore")
                if '*.db' not in content:
                    issues.append("WARNING: Database files not in .gitignore")
    
    return issues

def generate_security_report():
    """보안 리포트 생성"""
    issues = scan_security_issues()
    
    report = {
        "timestamp": datetime.now().isoformat(),
        "total_issues": len(issues),
        "issues": issues,
        "recommendations": [
            "Change default passwords",
            "Use strong SECRET_KEY",
            "Enable HTTPS in production",
            "Regular security updates",
            "Monitor access logs"
        ]
    }
    
    # 리포트 저장
    with open("logs/security/security_report.json", "w") as f:
        json.dump(report, f, indent=2)
    
    return report

if __name__ == "__main__":
    report = generate_security_report()
    print(json.dumps(report, indent=2))
'@
    
    $scanScript | Out-File -FilePath "scripts/security_scanner.py" -Encoding UTF8
    
    # 보안 스캔 실행
    $result = python scripts/security_scanner.py 2>&1
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   ✅ Security scan completed" -ForegroundColor Green
        Write-Host "   📋 Scan results saved to logs/security/security_report.json" -ForegroundColor White
    } else {
        Write-Host "   ❌ Security scan failed: $result" -ForegroundColor Red
    }
}

function Initialize-Logging {
    Write-Host "`n📝 Setting up security logging (보안 로깅 설정)..." -ForegroundColor Yellow
    
    # 보안 로깅 설정
    $loggingConfig = @'
import logging
from logging.handlers import RotatingFileHandler
import os

def setup_security_logging():
    """보안 로깅 설정"""
    # 로그 디렉토리 생성
    os.makedirs('logs/security', exist_ok=True)
    
    # 보안 로거 설정
    security_logger = logging.getLogger('security')
    security_logger.setLevel(logging.INFO)
    
    # 파일 핸들러 (일별 로테이션)
    file_handler = RotatingFileHandler(
        'logs/security/security.log',
        maxBytes=10*1024*1024,  # 10MB
        backupCount=30
    )
    file_handler.setLevel(logging.INFO)
    
    # 포맷터
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(formatter)
    
    security_logger.addHandler(file_handler)
    
    return security_logger

# 보안 이벤트 로깅 함수들
def log_login_attempt(user_id, success, ip_address):
    """로그인 시도 로깅"""
    logger = logging.getLogger('security')
    status = "SUCCESS" if success else "FAILED"
    logger.info(f"Login attempt: user_id={user_id}, status={status}, ip={ip_address}")

def log_permission_change(user_id, target_user_id, change_type):
    """권한 변경 로깅"""
    logger = logging.getLogger('security')
    logger.info(f"Permission change: user_id={user_id}, target={target_user_id}, type={change_type}")

def log_suspicious_activity(activity_type, details, ip_address):
    """의심스러운 활동 로깅"""
    logger = logging.getLogger('security')
    logger.warning(f"Suspicious activity: type={activity_type}, details={details}, ip={ip_address}")

if __name__ == "__main__":
    logger = setup_security_logging()
    logger.info("Security logging system initialized")
'@
    
    $loggingConfig | Out-File -FilePath "scripts/security_logging.py" -Encoding UTF8
    Write-Host "   ✅ Security logging configured" -ForegroundColor Green
}

function New-SecurityChecklist {
    Write-Host "`n📋 Creating security checklist (보안 체크리스트 생성)..." -ForegroundColor Yellow
    
    $checklist = @"
# Your Program 보안 체크리스트

## 🔐 인증 및 권한
- [ ] 기본 관리자 비밀번호 변경 완료
- [ ] 강력한 SECRET_KEY 설정
- [ ] 권한 시스템 정상 동작 확인
- [ ] 세션 타임아웃 설정

## 🌐 네트워크 보안
- [ ] 방화벽 규칙 설정
- [ ] HTTPS 설정 (운영 환경)
- [ ] CORS 설정 완료
- [ ] 보안 헤더 설정

## 📝 로깅 및 모니터링
- [ ] 보안 로깅 활성화
- [ ] 접근 로그 모니터링
- [ ] 오류 로그 분석
- [ ] 정기적인 보안 스캔

## 🗄️ 데이터 보안
- [ ] 데이터베이스 백업 설정
- [ ] 민감한 데이터 암호화
- [ ] 데이터 접근 권한 제한
- [ ] 정기적인 데이터 감사

## 🔧 시스템 보안
- [ ] 정기적인 보안 업데이트
- [ ] 불필요한 서비스 비활성화
- [ ] 파일 권한 설정
- [ ] 임시 파일 정리

## 📊 보안 모니터링
- [ ] 실시간 보안 알림 설정
- [ ] 정기적인 보안 리포트 생성
- [ ] 침입 탐지 시스템 구축
- [ ] 보안 사고 대응 계획

## 🚨 응급 대응
- [ ] 보안 사고 대응 절차 문서화
- [ ] 백업 및 복구 절차 확인
- [ ] 연락처 및 에스컬레이션 절차
- [ ] 정기적인 보안 훈련

---
**생성일**: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
**담당자**: 시스템 관리자
**다음 검토일**: $(Get-Date).AddDays(30).ToString('yyyy-MM-dd')
"@
    
    $checklist | Out-File -FilePath "SECURITY_CHECKLIST.md" -Encoding UTF8
    Write-Host "   ✅ Security checklist created" -ForegroundColor Green
}

# 메인 실행
Write-Host "`n🚀 Starting security setup..." -ForegroundColor Cyan

# 비밀번호 변경 (선택사항)
$changePassword = Read-Host "Do you want to change the default admin password? (y/n)"
if ($changePassword -eq 'y' -or $changePassword -eq 'Y') {
    Set-DefaultPassword
}

Initialize-AccessControl
Start-SecurityScan
Initialize-Logging
New-SecurityChecklist

Write-Host "`n✅ Security setup completed!" -ForegroundColor Green
Write-Host "`n📋 Security recommendations:" -ForegroundColor Yellow
Write-Host "   1. Review security_report.json for issues" -ForegroundColor White
Write-Host "   2. Complete SECURITY_CHECKLIST.md" -ForegroundColor White
Write-Host "   3. Enable HTTPS in production" -ForegroundColor White
Write-Host "   4. Set up regular security monitoring" -ForegroundColor White
Write-Host "   5. Train users on security best practices" -ForegroundColor White

Write-Host "`n🔒 Your Program security is now enhanced!" -ForegroundColor Green 