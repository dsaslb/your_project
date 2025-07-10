# Your Program Quick Fix Script (빠른 문제 해결 스크립트)
# 데이터베이스 및 권한 시스템 문제 해결

$OutputEncoding = [Console]::OutputEncoding = [Text.Encoding]::UTF8

Write-Host "🔧 Your Program Quick Fix (빠른 문제 해결)" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Cyan

function Repair-DatabaseQuery {
    Write-Host "`n🗄️ Repairing Database Query Issues (데이터베이스 쿼리 문제 해결)..." -ForegroundColor Yellow
    
    try {
        # DB 쿼리 부분만 text("SELECT 1")로 수정
        $dbFixScript = @"
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath('.')))

from app import app, db
from sqlalchemy import text

with app.app_context():
    try:
        # SQLAlchemy 2.0 호환 쿼리 실행
        result = db.session.execute(text('SELECT 1')).fetchone()
        if result:
            print('SUCCESS: Database connection successful with SQLAlchemy 2.0')
            sys.exit(0)
        else:
            print('ERROR: Database query returned no results')
            sys.exit(1)
    except Exception as e:
        print(f'ERROR: {str(e)}')
        sys.exit(1)
"@
        
        $dbFixScript | Out-File -FilePath "temp_db_fix.py" -Encoding UTF8
        $result = python temp_db_fix.py 2>&1
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Database query issues fixed (데이터베이스 쿼리 문제 해결 완료)" -ForegroundColor Green
            $script:dbFixed = $true
        } else {
            Write-Host "❌ Failed to fix database query issues (데이터베이스 쿼리 문제 해결 실패)" -ForegroundColor Red
            Write-Host "   Error: $result" -ForegroundColor White
            $script:dbFixed = $false
        }
        
        # 임시 파일 삭제
        if (Test-Path "temp_db_fix.py") {
            Remove-Item "temp_db_fix.py" -Force
        }
    } catch {
        Write-Host "❌ Database fix failed (데이터베이스 수정 실패)" -ForegroundColor Red
        Write-Host "   Error: $($_.Exception.Message)" -ForegroundColor White
        $script:dbFixed = $false
    }
}

function Repair-PermissionsModel {
    Write-Host "`n🔐 Repairing Permissions Model Issues (권한 모델 문제 해결)..." -ForegroundColor Yellow
    
    try {
        # models.py에서 Permission 클래스 확인 및 수정
        $modelsContent = Get-Content "models.py" -Raw
        
        if ($modelsContent -notmatch "class Permission") {
            Write-Host "Adding Permission model to models.py... (models.py에 Permission 모델 추가)" -ForegroundColor White
            
            # Permission 클래스 추가
            $permissionClass = @"

class Permission(db.Model):
    __tablename__ = 'permissions'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Permission {self.name}>'
"@
            
            # models.py 파일 끝에 추가
            Add-Content -Path "models.py" -Value $permissionClass
            Write-Host "✅ Permission model added to models.py (Permission 모델이 models.py에 추가됨)" -ForegroundColor Green
        } else {
            Write-Host "✅ Permission model already exists (Permission 모델이 이미 존재함)" -ForegroundColor Green
        }
        
        # 권한 시스템 초기화
        $permInitScript = @"
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath('.')))

from app import app, db
from models import User, Brand, Branch, Industry
from datetime import datetime

with app.app_context():
    try:
        # 기본 산업 생성
        industries = ['음식점', '카페', '편의점', '기타']
        for ind_name in industries:
            industry = Industry.query.filter_by(name=ind_name).first()
            if not industry:
                industry = Industry(name=ind_name, description=f'{ind_name} industry')
                db.session.add(industry)
                print(f'Created industry: {ind_name}')
        
        # 관리자 사용자 생성 (없는 경우)
        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            admin_user = User(
                username='admin',
                email='admin@your_program.com',
                role='admin',
                is_active=True
            )
            admin_user.set_password('admin123')
            db.session.add(admin_user)
            print('Created admin user')
        
        db.session.commit()
        print('SUCCESS: Permissions system initialization completed')
        sys.exit(0)
        
    except Exception as e:
        print(f'ERROR: {str(e)}')
        db.session.rollback()
        sys.exit(1)
"@
        
        $permInitScript | Out-File -FilePath "temp_perm_fix.py" -Encoding UTF8
        $result = python temp_perm_fix.py 2>&1
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Permissions system fixed (권한 시스템 문제 해결 완료)" -ForegroundColor Green
            Write-Host "   $result" -ForegroundColor White
            $script:permFixed = $true
        } else {
            Write-Host "❌ Failed to fix permissions system (권한 시스템 문제 해결 실패)" -ForegroundColor Red
            Write-Host "   Error: $result" -ForegroundColor White
            $script:permFixed = $false
        }
        
        # 임시 파일 삭제
        if (Test-Path "temp_perm_fix.py") {
            Remove-Item "temp_perm_fix.py" -Force
        }
    } catch {
        Write-Host "❌ Permissions fix failed (권한 시스템 수정 실패)" -ForegroundColor Red
        Write-Host "   Error: $($_.Exception.Message)" -ForegroundColor White
        $script:permFixed = $false
    }
}

function Update-HealthCheckScript {
    Write-Host "`n📝 Updating Health Check Script (헬스체크 스크립트 업데이트)..." -ForegroundColor Yellow
    
    try {
        # 헬스체크 스크립트의 데이터베이스 테스트 부분 수정
        $healthCheckContent = Get-Content "scripts\health_check.ps1" -Raw
        
        # SQLAlchemy 2.0 호환 쿼리로 수정
        $newDbTest = @'
        # Python 스크립트로 데이터베이스 연결 테스트
        $dbTestScript = @"
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath('.')))

try:
    from app import app, db
    from sqlalchemy import text
    with app.app_context():
        # SQLAlchemy 2.0 호환 쿼리 실행
        result = db.session.execute(text('SELECT 1')).fetchone()
        if result:
            print('SUCCESS: Database connection successful')
            sys.exit(0)
        else:
            print('ERROR: Database query failed')
            sys.exit(1)
except Exception as e:
    print(f'ERROR: {str(e)}')
    sys.exit(1)
"@
'@
        
        # 기존 데이터베이스 테스트 부분 교체
        $pattern = '(?s)# Python 스크립트로 데이터베이스 연결 테스트.*?except Exception as e:'
        $replacement = $newDbTest.Trim()
        
        $updatedContent = $healthCheckContent -replace $pattern, $replacement
        Set-Content -Path "scripts\health_check.ps1" -Value $updatedContent -Encoding UTF8
        
        Write-Host "✅ Health check script updated (헬스체크 스크립트 업데이트 완료)" -ForegroundColor Green
    } catch {
        Write-Host "❌ Failed to update health check script (헬스체크 스크립트 업데이트 실패)" -ForegroundColor Red
        Write-Host "   Error: $($_.Exception.Message)" -ForegroundColor White
    }
}

# 메인 실행
Write-Host "Starting quick fix at: $(Get-Date)" -ForegroundColor Cyan

$startTime = Get-Date
$dbFixed = $false
$permFixed = $false

# 문제 해결 실행
Repair-DatabaseQuery
Repair-PermissionsModel
Update-HealthCheckScript

# 데이터베이스 마이그레이션 재실행
Write-Host "`n🔄 Running Database Migration (데이터베이스 마이그레이션 실행)..." -ForegroundColor Yellow
flask db upgrade

# 최종 상태 확인
Write-Host "`n📋 Quick Fix Summary (빠른 수정 요약)" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "Database Query: $(if ($dbFixed) { '✅ Fixed' } else { '❌ Failed' })" -ForegroundColor $(if ($dbFixed) { 'Green' } else { 'Red' })
Write-Host "Permissions System: $(if ($permFixed) { '✅ Fixed' } else { '❌ Failed' })" -ForegroundColor $(if ($permFixed) { 'Green' } else { 'Red' })

$endTime = Get-Date
$duration = $endTime - $startTime

Write-Host "`n⏱️ Fix Duration: $($duration.TotalSeconds) seconds" -ForegroundColor White

if ($dbFixed -and $permFixed) {
    Write-Host "`n🎉 Quick fix completed successfully! (빠른 수정 성공적으로 완료)" -ForegroundColor Green
    Write-Host "   Run health check again to verify: .\scripts\health_check.ps1" -ForegroundColor White
} else {
    Write-Host "`n⚠️ Some issues could not be resolved automatically." -ForegroundColor Yellow
    Write-Host "   Please check the error messages above." -ForegroundColor White
}

Write-Host "`nQuick fix completed at: $endTime" -ForegroundColor Cyan 