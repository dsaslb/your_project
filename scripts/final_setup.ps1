# Your Program 최종 설정 및 문제 해결 스크립트
# 헬스체크 결과에 따른 자동 문제 해결

$OutputEncoding = [Console]::OutputEncoding = [Text.Encoding]::UTF8

Write-Host "🔧 Your Program Final Setup & Issue Resolution (최종 설정 및 문제 해결)" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Cyan

function Repair-DatabaseIssues {
    Write-Host "`n🗄️ Repairing Database Issues (데이터베이스 문제 해결)..." -ForegroundColor Yellow
    
    try {
        # 데이터베이스 마이그레이션 재실행
        Write-Host "Running database migrations... (데이터베이스 마이그레이션 실행)" -ForegroundColor White
        flask db upgrade
        
        # 데이터베이스 초기화 스크립트 실행
        Write-Host "Initializing database... (데이터베이스 초기화)" -ForegroundColor White
        python -c "
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath('.')))

from app import app, db
from models import User, Brand, Branch, Industry

with app.app_context():
    # 기본 역할 생성
    roles = ['admin', 'brand_manager', 'branch_manager', 'employee']
    for role_name in roles:
        role = Role.query.filter_by(name=role_name).first()
        if not role:
            role = Role(name=role_name, description=f'{role_name} role')
            db.session.add(role)
    
    # 기본 산업 생성
    industries = ['음식점', '카페', '편의점', '기타']
    for ind_name in industries:
        industry = Industry.query.filter_by(name=ind_name).first()
        if not industry:
            industry = Industry(name=ind_name, description=f'{ind_name} industry')
            db.session.add(industry)
    
    db.session.commit()
    print('Database initialization completed')
"
        
        Write-Host "✅ Database issues fixed (데이터베이스 문제 해결 완료)" -ForegroundColor Green
        return $true
    } catch {
        Write-Host "❌ Failed to fix database issues (데이터베이스 문제 해결 실패)" -ForegroundColor Red
        Write-Host "   Error: $($_.Exception.Message)" -ForegroundColor White
        return $false
    }
}

function Repair-FrontendIssues {
    Write-Host "`n🎨 Repairing Frontend Issues (프론트엔드 문제 해결)..." -ForegroundColor Yellow
    
    try {
        # 프론트엔드 디렉토리로 이동
        Push-Location "your_program_frontend"
        
        # 의존성 재설치
        Write-Host "Reinstalling frontend dependencies... (프론트엔드 의존성 재설치)" -ForegroundColor White
        npm install
        
        # 빌드 테스트
        Write-Host "Testing frontend build... (프론트엔드 빌드 테스트)" -ForegroundColor White
        npm run build
        
        # 개발 서버 시작
        Write-Host "Starting frontend development server... (프론트엔드 개발 서버 시작)" -ForegroundColor White
        Start-Process -FilePath "npm" -ArgumentList "run", "dev" -WindowStyle Minimized
        
        Pop-Location
        Write-Host "✅ Frontend issues fixed (프론트엔드 문제 해결 완료)" -ForegroundColor Green
        return $true
    } catch {
        Write-Host "❌ Failed to fix frontend issues (프론트엔드 문제 해결 실패)" -ForegroundColor Red
        Write-Host "   Error: $($_.Exception.Message)" -ForegroundColor White
        Pop-Location
        return $false
    }
}

function Repair-PermissionsIssues {
    Write-Host "`n🔐 Repairing Permissions Issues (권한 시스템 문제 해결)..." -ForegroundColor Yellow
    
    try {
        # 권한 시스템 초기화 스크립트
        $permInitScript = @"
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath('.')))

from app import app, db
from models import User, Brand, Branch, Industry

with app.app_context():
    # 기본 권한 생성
    permissions = [
        'user_management', 'brand_management', 'branch_management',
        'schedule_management', 'attendance_management', 'order_management',
        'inventory_management', 'report_view', 'system_admin'
    ]
    
    for perm_name in permissions:
        perm = Permission.query.filter_by(name=perm_name).first()
        if not perm:
            perm = Permission(name=perm_name, description=f'{perm_name} permission')
            db.session.add(perm)
    
    # 관리자 사용자 생성 (없는 경우)
    admin_user = User.query.filter_by(username='admin').first()
    if not admin_user:
        admin_role = Role.query.filter_by(name='admin').first()
        if admin_role:
            admin_user = User(
                username='admin',
                email='admin@your_program.com',
                role_id=admin_role.id,
                is_active=True
            )
            admin_user.set_password('admin123')
            db.session.add(admin_user)
    
    db.session.commit()
    print('Permissions system initialization completed')
"@
        
        $permInitScript | Out-File -FilePath "temp_perm_init.py" -Encoding UTF8
        python temp_perm_init.py
        
        if (Test-Path "temp_perm_init.py") {
            Remove-Item "temp_perm_init.py" -Force
        }
        
        Write-Host "✅ Permissions issues fixed (권한 시스템 문제 해결 완료)" -ForegroundColor Green
        return $true
    } catch {
        Write-Host "❌ Failed to fix permissions issues (권한 시스템 문제 해결 실패)" -ForegroundColor Red
        Write-Host "   Error: $($_.Exception.Message)" -ForegroundColor White
        return $false
    }
}

function Start-BackendServer {
    Write-Host "`n🔧 Starting Backend Server (백엔드 서버 시작)..." -ForegroundColor Yellow
    
    try {
        # 백엔드 서버가 실행 중인지 확인
        $backendProcess = Get-Process python -ErrorAction SilentlyContinue | Where-Object { $_.ProcessName -eq "python" }
        
        if ($backendProcess) {
            Write-Host "✅ Backend server is already running (백엔드 서버가 이미 실행 중)" -ForegroundColor Green
            return $true
        } else {
            Write-Host "Starting backend server... (백엔드 서버 시작)" -ForegroundColor White
            Start-Process -FilePath "python" -ArgumentList "app.py" -WindowStyle Minimized
            Start-Sleep -Seconds 3
            
            # 서버 시작 확인
            try {
                $response = Invoke-WebRequest -Uri "http://localhost:5000" -UseBasicParsing -TimeoutSec 10
                if ($response.StatusCode -eq 200) {
                    Write-Host "✅ Backend server started successfully (백엔드 서버 성공적으로 시작)" -ForegroundColor Green
                    return $true
                }
            } catch {
                Write-Host "⚠️ Backend server may still be starting... (백엔드 서버가 아직 시작 중일 수 있음)" -ForegroundColor Yellow
                return $true
            }
        }
    } catch {
        Write-Host "❌ Failed to start backend server (백엔드 서버 시작 실패)" -ForegroundColor Red
        Write-Host "   Error: $($_.Exception.Message)" -ForegroundColor White
        return $false
    }
}

function Show-FinalStatus {
    Write-Host "`n📋 Final System Status (최종 시스템 상태)" -ForegroundColor Cyan
    Write-Host "================================================" -ForegroundColor Cyan
    
    # 서버 상태 확인
    try {
        $null = Invoke-WebRequest -Uri "http://localhost:5000" -UseBasicParsing -TimeoutSec 5
        Write-Host "Backend: ✅ Running (http://localhost:5000)" -ForegroundColor Green
    } catch {
        Write-Host "Backend: ❌ Not responding" -ForegroundColor Red
    }
    
    try {
        $null = Invoke-WebRequest -Uri "http://localhost:3001" -UseBasicParsing -TimeoutSec 5
        Write-Host "Frontend: ✅ Running (http://localhost:3001)" -ForegroundColor Green
    } catch {
        try {
            $null = Invoke-WebRequest -Uri "http://localhost:3000" -UseBasicParsing -TimeoutSec 5
            Write-Host "Frontend: ✅ Running (http://localhost:3000)" -ForegroundColor Green
        } catch {
            Write-Host "Frontend: ❌ Not responding" -ForegroundColor Red
        }
    }
    
    # 프로세스 상태
    $pythonProcesses = tasklist | findstr python
    $nodeProcesses = tasklist | findstr node
    
    Write-Host "`n📊 Process Status:" -ForegroundColor Yellow
    if ($pythonProcesses) {
        Write-Host "Python: ✅ Running ($(($pythonProcesses | Measure-Object).Count) processes)" -ForegroundColor Green
    } else {
        Write-Host "Python: ❌ Not running" -ForegroundColor Red
    }
    
    if ($nodeProcesses) {
        Write-Host "Node.js: ✅ Running ($(($nodeProcesses | Measure-Object).Count) processes)" -ForegroundColor Green
    } else {
        Write-Host "Node.js: ❌ Not running" -ForegroundColor Red
    }
}

function Show-AccessInstructions {
    Write-Host "`n🎉 Your Program Setup Complete! (설정 완료)" -ForegroundColor Green
    Write-Host "================================================" -ForegroundColor Cyan
    
    Write-Host "`n🌐 Access URLs:" -ForegroundColor Yellow
    Write-Host "   Backend API: http://localhost:5000" -ForegroundColor White
    Write-Host "   Frontend App: http://localhost:3001 (or http://localhost:3000)" -ForegroundColor White
    Write-Host "   Admin Panel: http://localhost:5000/admin" -ForegroundColor White
    
    Write-Host "`n🔑 Default Login:" -ForegroundColor Yellow
    Write-Host "   Username: admin" -ForegroundColor White
    Write-Host "   Password: admin123" -ForegroundColor White
    
    Write-Host "`n📋 Next Steps:" -ForegroundColor Yellow
    Write-Host "   1. Open your browser and navigate to http://localhost:3001" -ForegroundColor White
    Write-Host "   2. Login with admin/admin123" -ForegroundColor White
    Write-Host "   3. Test all features: user management, permissions, real-time sync" -ForegroundColor White
    Write-Host "   4. Check mobile responsiveness and accessibility" -ForegroundColor White
    
    Write-Host "`n🔧 Management Commands:" -ForegroundColor Yellow
    Write-Host "   Health Check: .\scripts\health_check.ps1" -ForegroundColor White
    Write-Host "   Backup: .\scripts\backup_project.ps1" -ForegroundColor White
    Write-Host "   Cleanup: .\scripts\cleanup_project.ps1" -ForegroundColor White
    
    Write-Host "`n⚠️ Important Notes:" -ForegroundColor Yellow
    Write-Host "   - Change default admin password after first login" -ForegroundColor White
    Write-Host "   - Configure environment variables for production" -ForegroundColor White
    Write-Host "   - Set up proper database for production use" -ForegroundColor White
    Write-Host "   - Enable HTTPS for production deployment" -ForegroundColor White
}

# 메인 실행
Write-Host "Starting final setup at: $(Get-Date)" -ForegroundColor Cyan

$startTime = Get-Date
$success = $true

# 문제 해결 실행
$success = Repair-DatabaseIssues -and $success
$success = Repair-PermissionsIssues -and $success
$success = Start-BackendServer -and $success
$success = Repair-FrontendIssues -and $success

# 잠시 대기
Start-Sleep -Seconds 5

# 최종 상태 확인
Show-FinalStatus

# 완료 시간 계산
$endTime = Get-Date
$duration = $endTime - $startTime

Write-Host "`n⏱️ Setup Duration: $($duration.TotalSeconds) seconds" -ForegroundColor White

if ($success) {
    Show-AccessInstructions
} else {
    Write-Host "`n⚠️ Some issues could not be resolved automatically." -ForegroundColor Yellow
    Write-Host "   Please check the error messages above and resolve manually." -ForegroundColor White
}

Write-Host "`nFinal setup completed at: $endTime" -ForegroundColor Cyan 