# Your Program 전체 시스템 헬스체크 스크립트
# 백엔드, 프론트엔드, 데이터베이스, 권한 시스템 등 전체 상태 확인

$OutputEncoding = [Console]::OutputEncoding = [Text.Encoding]::UTF8

Write-Host "🏥 Your Program System Health Check (전체 시스템 헬스체크)" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Cyan

$startTime = Get-Date
$healthStatus = @{
    backend = $false
    frontend = $false
    database = $false
    permissions = $false
    overall = $false
}

function Test-BackendHealth {
    Write-Host "`n🔧 Backend Health Check (백엔드 상태 확인)..." -ForegroundColor Yellow
    
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:5000" -UseBasicParsing -TimeoutSec 10
        if ($response.StatusCode -eq 200) {
            Write-Host "✅ Backend server is running (백엔드 서버 실행 중)" -ForegroundColor Green
            Write-Host "   Status: $($response.StatusCode) $($response.StatusDescription)" -ForegroundColor White
            Write-Host "   Response Time: $($response.BaseResponse.ResponseTime)ms" -ForegroundColor White
            $script:healthStatus.backend = $true
        } else {
            Write-Host "❌ Backend server returned unexpected status (백엔드 서버 예상치 못한 상태)" -ForegroundColor Red
            Write-Host "   Status: $($response.StatusCode)" -ForegroundColor White
        }
    } catch {
        Write-Host "❌ Backend server is not responding (백엔드 서버 응답 없음)" -ForegroundColor Red
        Write-Host "   Error: $($_.Exception.Message)" -ForegroundColor White
    }
}

function Test-FrontendHealth {
    Write-Host "`n🎨 Frontend Health Check (프론트엔드 상태 확인)..." -ForegroundColor Yellow
    
    # 포트 3000과 3001 모두 확인
    $frontendPorts = @(3000, 3001)
    $frontendRunning = $false
    
    foreach ($port in $frontendPorts) {
        try {
            $response = Invoke-WebRequest -Uri "http://localhost:$port" -UseBasicParsing -TimeoutSec 5
            if ($response.StatusCode -eq 200) {
                Write-Host "✅ Frontend server is running on port $port (프론트엔드 서버 포트 $port에서 실행 중)" -ForegroundColor Green
                Write-Host "   Status: $($response.StatusCode) $($response.StatusDescription)" -ForegroundColor White
                $frontendRunning = $true
                break
            }
        } catch {
            Write-Host "⚠️ Frontend server not responding on port $port (프론트엔드 서버 포트 $port에서 응답 없음)" -ForegroundColor Yellow
        }
    }
    
    if ($frontendRunning) {
        $script:healthStatus.frontend = $true
    } else {
        Write-Host "❌ Frontend server is not running on any expected port (프론트엔드 서버가 예상 포트에서 실행되지 않음)" -ForegroundColor Red
    }
}

function Test-DatabaseHealth {
    Write-Host "`n🗄️ Database Health Check (데이터베이스 상태 확인)..." -ForegroundColor Yellow
    
    try {
        # Python 스크립트로 데이터베이스 연결 테스트
        $dbTestScript = @'
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath('.')))
from app import app, db
from sqlalchemy import text
with app.app_context():
    try:
        result = db.session.execute(text("SELECT 1")).fetchone()
        if result:
            print("SUCCESS: Database connection successful")
            sys.exit(0)
        else:
            print("ERROR: Database query failed")
            sys.exit(1)
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)
'@
        
        $dbTestScript | Out-File -FilePath "temp_db_test.py" -Encoding UTF8
        $result = python temp_db_test.py 2>&1
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Database connection successful (데이터베이스 연결 성공)" -ForegroundColor Green
            $script:healthStatus.database = $true
        } else {
            Write-Host "❌ Database connection failed (데이터베이스 연결 실패)" -ForegroundColor Red
            Write-Host "   Error: $result" -ForegroundColor White
        }
        
        # 임시 파일 삭제
        if (Test-Path "temp_db_test.py") {
            Remove-Item "temp_db_test.py" -Force
        }
    } catch {
        Write-Host "❌ Database health check failed (데이터베이스 헬스체크 실패)" -ForegroundColor Red
        Write-Host "   Error: $($_.Exception.Message)" -ForegroundColor White
    }
}

function Test-PermissionsHealth {
    Write-Host "`n🔐 Permissions System Health Check (권한 시스템 상태 확인)..." -ForegroundColor Yellow
    
    try {
        # 권한 시스템 테스트 스크립트
        $permTestScript = @"
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath('.')))

try:
    from app import app, db
    from models import User, Brand, Branch, Permission, Role
    
    with app.app_context():
        # 기본 권한 확인
        admin_role = Role.query.filter_by(name='admin').first()
        if admin_role:
            print('SUCCESS: Admin role exists')
        else:
            print('WARNING: Admin role not found')
        
        # 사용자 권한 확인
        users = User.query.limit(5).all()
        print(f'SUCCESS: Found {len(users)} users')
        
        # 브랜드/지점 구조 확인
        brands = Brand.query.limit(5).all()
        print(f'SUCCESS: Found {len(brands)} brands')
        
        print('SUCCESS: Permissions system is working')
        sys.exit(0)
        
except Exception as e:
    print(f'ERROR: {str(e)}')
    sys.exit(1)
"@
        
        $permTestScript | Out-File -FilePath "temp_perm_test.py" -Encoding UTF8
        $result = python temp_perm_test.py 2>&1
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Permissions system is working (권한 시스템 정상 동작)" -ForegroundColor Green
            Write-Host "   $result" -ForegroundColor White
            $script:healthStatus.permissions = $true
        } else {
            Write-Host "❌ Permissions system check failed (권한 시스템 확인 실패)" -ForegroundColor Red
            Write-Host "   Error: $result" -ForegroundColor White
        }
        
        # 임시 파일 삭제
        if (Test-Path "temp_perm_test.py") {
            Remove-Item "temp_perm_test.py" -Force
        }
    } catch {
        Write-Host "❌ Permissions health check failed (권한 헬스체크 실패)" -ForegroundColor Red
        Write-Host "   Error: $($_.Exception.Message)" -ForegroundColor White
    }
}

function Show-ProcessStatus {
    Write-Host "`n📊 Process Status (프로세스 상태)..." -ForegroundColor Yellow
    
    # Python 프로세스 확인
    $pythonProcesses = tasklist | findstr python
    if ($pythonProcesses) {
        Write-Host "✅ Python processes running (Python 프로세스 실행 중)" -ForegroundColor Green
        $pythonProcesses | ForEach-Object { Write-Host "   $_" -ForegroundColor White }
    } else {
        Write-Host "❌ No Python processes found (Python 프로세스 없음)" -ForegroundColor Red
    }
    
    # Node.js 프로세스 확인
    $nodeProcesses = tasklist | findstr node
    if ($nodeProcesses) {
        Write-Host "✅ Node.js processes running (Node.js 프로세스 실행 중)" -ForegroundColor Green
        $nodeProcesses | ForEach-Object { Write-Host "   $_" -ForegroundColor White }
    } else {
        Write-Host "❌ No Node.js processes found (Node.js 프로세스 없음)" -ForegroundColor Red
    }
}

function Show-PortStatus {
    Write-Host "`n🌐 Port Status (포트 상태)..." -ForegroundColor Yellow
    
    $ports = @(5000, 3000, 3001)
    foreach ($port in $ports) {
        $portStatus = netstat -an | findstr ":$port"
        if ($portStatus) {
            Write-Host "✅ Port $port is in use (포트 $port 사용 중)" -ForegroundColor Green
            $portStatus | ForEach-Object { Write-Host "   $_" -ForegroundColor White }
        } else {
            Write-Host "❌ Port $port is not in use (포트 $port 미사용)" -ForegroundColor Red
        }
    }
}

# 메인 실행
Write-Host "Starting health check at: $startTime" -ForegroundColor Cyan

Test-BackendHealth
Test-FrontendHealth
Test-DatabaseHealth
Test-PermissionsHealth
Show-ProcessStatus
Show-PortStatus

# 전체 상태 평가
$endTime = Get-Date
$duration = $endTime - $startTime

$script:healthStatus.overall = $healthStatus.backend -and $healthStatus.frontend -and $healthStatus.database -and $healthStatus.permissions

Write-Host "`n📋 Health Check Summary (헬스체크 요약)" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "Backend: $(if ($healthStatus.backend) { '✅ Healthy' } else { '❌ Unhealthy' })" -ForegroundColor $(if ($healthStatus.backend) { 'Green' } else { 'Red' })
Write-Host "Frontend: $(if ($healthStatus.frontend) { '✅ Healthy' } else { '❌ Unhealthy' })" -ForegroundColor $(if ($healthStatus.frontend) { 'Green' } else { 'Red' })
Write-Host "Database: $(if ($healthStatus.database) { '✅ Healthy' } else { '❌ Unhealthy' })" -ForegroundColor $(if ($healthStatus.database) { 'Green' } else { 'Red' })
Write-Host "Permissions: $(if ($healthStatus.permissions) { '✅ Healthy' } else { '❌ Unhealthy' })" -ForegroundColor $(if ($healthStatus.permissions) { 'Green' } else { 'Red' })
Write-Host "Overall: $(if ($healthStatus.overall) { '✅ All Systems Healthy' } else { '❌ Some Systems Unhealthy' })" -ForegroundColor $(if ($healthStatus.overall) { 'Green' } else { 'Red' })

Write-Host "`n⏱️ Duration: $($duration.TotalSeconds) seconds (소요 시간)" -ForegroundColor White

if ($healthStatus.overall) {
    Write-Host "`n🎉 All systems are healthy! Your Program is ready to use." -ForegroundColor Green
    Write-Host "   Backend: http://localhost:5000" -ForegroundColor White
    Write-Host "   Frontend: http://localhost:3001" -ForegroundColor White
} else {
    Write-Host "`n⚠️ Some systems need attention. Please check the issues above." -ForegroundColor Yellow
    Write-Host "   Recommended actions:" -ForegroundColor Cyan
    if (!$healthStatus.backend) {
        Write-Host "   - Start backend server: python app.py" -ForegroundColor White
    }
    if (!$healthStatus.frontend) {
        Write-Host "   - Start frontend server: cd your_program_frontend && npm run dev" -ForegroundColor White
    }
    if (!$healthStatus.database) {
        Write-Host "   - Check database configuration and run migrations" -ForegroundColor White
    }
    if (!$healthStatus.permissions) {
        Write-Host "   - Check permissions system and user roles" -ForegroundColor White
    }
}

Write-Host "`nHealth check completed at: $endTime" -ForegroundColor Cyan 