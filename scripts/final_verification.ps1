# Your Program 최종 검증 스크립트
# 전체 시스템 상태 최종 확인

$OutputEncoding = [Console]::OutputEncoding = [Text.Encoding]::UTF8

Write-Host "🎯 Your Program Final Verification (최종 검증)" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Cyan

function Test-SystemComponents {
    Write-Host "`n🔍 Testing System Components (시스템 구성 요소 테스트)..." -ForegroundColor Yellow
    
    $results = @{
        backend = $false
        frontend = $false
        database = $false
        models = $false
        overall = $false
    }
    
    # 백엔드 테스트
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:5000" -UseBasicParsing -TimeoutSec 10
        if ($response.StatusCode -eq 200) {
            Write-Host "✅ Backend: Running (http://localhost:5000)" -ForegroundColor Green
            $results.backend = $true
        }
    } catch {
        Write-Host "❌ Backend: Not responding" -ForegroundColor Red
    }
    
    # 프론트엔드 테스트
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:3001" -UseBasicParsing -TimeoutSec 5
        if ($response.StatusCode -eq 200) {
            Write-Host "✅ Frontend: Running (http://localhost:3001)" -ForegroundColor Green
            $results.frontend = $true
        }
    } catch {
        try {
            $response = Invoke-WebRequest -Uri "http://localhost:3000" -UseBasicParsing -TimeoutSec 5
            if ($response.StatusCode -eq 200) {
                Write-Host "✅ Frontend: Running (http://localhost:3000)" -ForegroundColor Green
                $results.frontend = $true
            }
        } catch {
            Write-Host "❌ Frontend: Not responding" -ForegroundColor Red
        }
    }
    
    # 데이터베이스 테스트
    try {
        $dbTestScript = @"
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath('.')))

from app import app, db
from sqlalchemy import text

with app.app_context():
    try:
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
        
        $dbTestScript | Out-File -FilePath "temp_db_verify.py" -Encoding UTF8
        $result = python temp_db_verify.py 2>&1
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Database: Connection successful" -ForegroundColor Green
            $results.database = $true
        } else {
            Write-Host "❌ Database: Connection failed" -ForegroundColor Red
            Write-Host "   Error: $result" -ForegroundColor White
        }
        
        if (Test-Path "temp_db_verify.py") {
            Remove-Item "temp_db_verify.py" -Force
        }
    } catch {
        Write-Host "❌ Database: Test failed" -ForegroundColor Red
    }
    
    # 모델 테스트
    try {
        $modelTestScript = @"
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath('.')))

from app import app, db
from models import User, Brand, Branch, Industry

with app.app_context():
    try:
        # 기본 모델들 테스트
        users = User.query.limit(5).all()
        brands = Brand.query.limit(5).all()
        branches = Branch.query.limit(5).all()
        industries = Industry.query.limit(5).all()
        
        print(f'SUCCESS: Found {len(users)} users, {len(brands)} brands, {len(branches)} branches, {len(industries)} industries')
        sys.exit(0)
    except Exception as e:
        print(f'ERROR: {str(e)}')
        sys.exit(1)
"@
        
        $modelTestScript | Out-File -FilePath "temp_model_verify.py" -Encoding UTF8
        $result = python temp_model_verify.py 2>&1
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Models: All models working correctly" -ForegroundColor Green
            Write-Host "   $result" -ForegroundColor White
            $results.models = $true
        } else {
            Write-Host "❌ Models: Some models have issues" -ForegroundColor Red
            Write-Host "   Error: $result" -ForegroundColor White
        }
        
        if (Test-Path "temp_model_verify.py") {
            Remove-Item "temp_model_verify.py" -Force
        }
    } catch {
        Write-Host "❌ Models: Test failed" -ForegroundColor Red
    }
    
    # 전체 상태 평가
    $results.overall = $results.backend -and $results.frontend -and $results.database -and $results.models
    
    return $results
}

function Show-SystemStatus {
    Write-Host "`n📊 System Status Summary (시스템 상태 요약)" -ForegroundColor Cyan
    Write-Host "================================================" -ForegroundColor Cyan
    
    # 프로세스 상태
    $pythonProcesses = tasklist | findstr python
    $nodeProcesses = tasklist | findstr node
    
    Write-Host "`n🖥️ Process Status:" -ForegroundColor Yellow
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
    
    # 포트 상태
    Write-Host "`n🌐 Port Status:" -ForegroundColor Yellow
    $ports = @(5000, 3000, 3001)
    foreach ($port in $ports) {
        $portStatus = netstat -an | findstr ":$port"
        if ($portStatus) {
            Write-Host "Port ${port}: ✅ In use" -ForegroundColor Green
        } else {
            Write-Host "Port ${port}: ❌ Not in use" -ForegroundColor Red
        }
    }
}

function Show-AccessInfo {
    Write-Host "`n🌐 Access Information (접속 정보)" -ForegroundColor Cyan
    Write-Host "================================================" -ForegroundColor Cyan
    
    Write-Host "Backend API: http://localhost:5000" -ForegroundColor White
    Write-Host "Frontend App: http://localhost:3001 (or http://localhost:3000)" -ForegroundColor White
    Write-Host "Admin Panel: http://localhost:5000/admin" -ForegroundColor White
    
    Write-Host "`n🔑 Default Login:" -ForegroundColor Yellow
    Write-Host "Username: admin" -ForegroundColor White
    Write-Host "Password: admin123" -ForegroundColor White
    
    Write-Host "`n📋 Available Features:" -ForegroundColor Yellow
    Write-Host "• User Management (사용자 관리)" -ForegroundColor White
    Write-Host "• Brand/Branch Management (브랜드/지점 관리)" -ForegroundColor White
    Write-Host "• Schedule Management (스케줄 관리)" -ForegroundColor White
    Write-Host "• Attendance Management (출퇴근 관리)" -ForegroundColor White
    Write-Host "• Order Management (발주 관리)" -ForegroundColor White
    Write-Host "• Inventory Management (재고 관리)" -ForegroundColor White
    Write-Host "• Real-time Notifications (실시간 알림)" -ForegroundColor White
    Write-Host "• AI-powered Analytics (AI 분석)" -ForegroundColor White
    Write-Host "• Mobile Responsive UI (모바일 반응형 UI)" -ForegroundColor White
}

function Show-ManagementCommands {
    Write-Host "`n🔧 Management Commands (관리 명령어)" -ForegroundColor Cyan
    Write-Host "================================================" -ForegroundColor Cyan
    
    Write-Host "Health Check: .\scripts\health_check.ps1" -ForegroundColor White
    Write-Host "Backup: .\scripts\backup_project.ps1" -ForegroundColor White
    Write-Host "Cleanup: .\scripts\cleanup_project.ps1" -ForegroundColor White
    Write-Host "Quick Fix: .\scripts\quick_fix.ps1" -ForegroundColor White
    Write-Host "Final Setup: .\scripts\final_setup.ps1" -ForegroundColor White
    
    Write-Host "`n📝 Development Commands:" -ForegroundColor Yellow
    Write-Host "Backend: python app.py" -ForegroundColor White
    Write-Host "Frontend: cd your_program_frontend && npm run dev" -ForegroundColor White
    Write-Host "Database: flask db upgrade" -ForegroundColor White
    Write-Host "Tests: pytest tests/ --cov=app --cov-report=xml" -ForegroundColor White
}

# 메인 실행
Write-Host "Starting final verification at: $(Get-Date)" -ForegroundColor Cyan

$startTime = Get-Date

# 시스템 구성 요소 테스트
$testResults = Test-SystemComponents

# 시스템 상태 표시
Show-SystemStatus

# 최종 결과 표시
Write-Host "`n📋 Final Verification Results (최종 검증 결과)" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "Backend: $(if ($testResults.backend) { '✅ Healthy' } else { '❌ Unhealthy' })" -ForegroundColor $(if ($testResults.backend) { 'Green' } else { 'Red' })
Write-Host "Frontend: $(if ($testResults.frontend) { '✅ Healthy' } else { '❌ Unhealthy' })" -ForegroundColor $(if ($testResults.frontend) { 'Green' } else { 'Red' })
Write-Host "Database: $(if ($testResults.database) { '✅ Healthy' } else { '❌ Unhealthy' })" -ForegroundColor $(if ($testResults.database) { 'Green' } else { 'Red' })
Write-Host "Models: $(if ($testResults.models) { '✅ Healthy' } else { '❌ Unhealthy' })" -ForegroundColor $(if ($testResults.models) { 'Green' } else { 'Red' })
Write-Host "Overall: $(if ($testResults.overall) { '✅ All Systems Healthy' } else { '❌ Some Systems Unhealthy' })" -ForegroundColor $(if ($testResults.overall) { 'Green' } else { 'Red' })

$endTime = Get-Date
$duration = $endTime - $startTime

Write-Host "`n⏱️ Verification Duration: $($duration.TotalSeconds) seconds" -ForegroundColor White

if ($testResults.overall) {
    Write-Host "`n🎉 Your Program is ready for use! (사용 준비 완료)" -ForegroundColor Green
    Show-AccessInfo
    Show-ManagementCommands
    
    Write-Host "`n🚀 Next Steps:" -ForegroundColor Yellow
    Write-Host "1. Open your browser and navigate to http://localhost:3001" -ForegroundColor White
    Write-Host "2. Login with admin/admin123" -ForegroundColor White
    Write-Host "3. Explore all features and test functionality" -ForegroundColor White
    Write-Host "4. Configure your business settings" -ForegroundColor White
    Write-Host "5. Add your staff and set up schedules" -ForegroundColor White
    
    Write-Host "`n⚠️ Important Security Notes:" -ForegroundColor Yellow
    Write-Host "• Change the default admin password immediately" -ForegroundColor White
    Write-Host "• Configure environment variables for production" -ForegroundColor White
    Write-Host "• Set up proper database for production use" -ForegroundColor White
    Write-Host "• Enable HTTPS for production deployment" -ForegroundColor White
} else {
    Write-Host "`n⚠️ Some systems need attention before use." -ForegroundColor Yellow
    Write-Host "   Please check the issues above and resolve them." -ForegroundColor White
    
    Write-Host "`n🔧 Recommended Actions:" -ForegroundColor Cyan
    if (!$testResults.backend) {
        Write-Host "• Start backend server: python app.py" -ForegroundColor White
    }
    if (!$testResults.frontend) {
        Write-Host "• Start frontend server: cd your_program_frontend && npm run dev" -ForegroundColor White
    }
    if (!$testResults.database) {
        Write-Host "• Check database configuration and run migrations" -ForegroundColor White
    }
    if (!$testResults.models) {
        Write-Host "• Check model definitions and database schema" -ForegroundColor White
    }
}

Write-Host "`nFinal verification completed at: $endTime" -ForegroundColor Cyan 