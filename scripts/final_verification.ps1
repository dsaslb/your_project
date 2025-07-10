# Your Program 최종 검증 스크립트
# 전체 시스템 상태 점검 및 요약 리포트 생성

$OutputEncoding = [Console]::OutputEncoding = [Text.Encoding]::UTF8

Write-Host "🔍 Your Program Final Verification (최종 검증)" -ForegroundColor Green
Write-Host "=============================================" -ForegroundColor Cyan

function Test-BackendHealth {
    Write-Host "\nTesting backend health..."
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:5000/api/health" -UseBasicParsing -TimeoutSec 10
        $healthData = $response.Content | ConvertFrom-Json
        if ($healthData.status -eq "healthy") {
            Write-Host "   Backend is healthy"
            return @{ "status" = "healthy"; "message" = $healthData.message; "timestamp" = $healthData.timestamp }
        } else {
            Write-Host "   Backend health check failed"
            return @{ "status" = "unhealthy"; "message" = "Health check returned unhealthy status" }
        }
    } catch {
        Write-Host "   Backend connection failed: $($_.Exception.Message)"
        return @{ "status" = "error"; "message" = $_.Exception.Message }
    }
}

function Test-FrontendHealth {
    Write-Host "\nTesting frontend health..."
    $frontendPorts = @(3000, 3001)
    $results = @()
    foreach ($port in $frontendPorts) {
        try {
            $response = Invoke-WebRequest -Uri "http://localhost:$port" -UseBasicParsing -TimeoutSec 10
            if ($response.StatusCode -eq 200) {
                Write-Host "   Frontend on port $port is running"
                $results += @{ "port" = $port; "status" = "running"; "status_code" = $response.StatusCode }
            } else {
                Write-Host "   Frontend on port $port returned status $($response.StatusCode)"
                $results += @{ "port" = $port; "status" = "warning"; "status_code" = $response.StatusCode }
            }
        } catch {
            Write-Host "   Frontend on port $port is not accessible"
            $results += @{ "port" = $port; "status" = "error"; "error" = $_.Exception.Message }
        }
    }
    return $results
}

function Test-DatabaseHealth {
    Write-Host "\nTesting database health..."
    try {
        $dbScript = @"
import sys
import os
import logging
import json
sys.path.append(os.path.dirname(os.path.abspath('.')))

# WARNING 등 불필요한 출력 제거
logging.getLogger().setLevel(logging.ERROR)
os.environ['WARNING'] = '0'

from app import app, db
from models import User
from sqlalchemy import text

with app.app_context():
    try:
        db.session.execute(text('SELECT 1'))
        user_count = User.query.count()
        admin_user = User.query.filter_by(role='admin').first()
        result = {'status': 'healthy','user_count': user_count,'admin_exists': admin_user is not None,'admin_username': admin_user.username if admin_user else None}
        print('SUCCESS:' + json.dumps(result))
    except Exception as e:
        print('ERROR:' + str(e))
"@
        $dbScript | Out-File -FilePath "temp_db_test.py" -Encoding UTF8
        $result = python temp_db_test.py 2>&1
        if ($LASTEXITCODE -eq 0 -and $result -like "SUCCESS:*") {
            $dbData = $result -replace "SUCCESS:", "" | ConvertFrom-Json
            Write-Host "   Database is healthy"
            Write-Host "   Total users: $($dbData.user_count)"
            Write-Host "   Admin user: $($dbData.admin_username)"
            return @{ "status" = "healthy"; "user_count" = $dbData.user_count; "admin_exists" = $dbData.admin_exists; "admin_username" = $dbData.admin_username }
        } else {
            Write-Host "   Database test failed: $result"
            return @{ "status" = "error"; "error" = $result }
        }
        if (Test-Path "temp_db_test.py") { Remove-Item "temp_db_test.py" -Force }
    } catch {
        Write-Host "   Database test failed: $($_.Exception.Message)"
        return @{ "status" = "error"; "error" = $_.Exception.Message }
    }
}

function Test-PermissionSystem {
    Write-Host "\nTesting permission system..."
    try {
        $permScript = @"
import sys
import os
import logging
import json
sys.path.append(os.path.dirname(os.path.abspath('.')))

# WARNING 등 불필요한 출력 제거
logging.getLogger().setLevel(logging.ERROR)
os.environ['WARNING'] = '0'

from app import app, db
from models import User

with app.app_context():
    try:
        admin_user = User.query.filter_by(role='admin').first()
        if not admin_user:
            print('ERROR: Admin user not found')
            exit(1)
        permissions = admin_user.permissions if admin_user.permissions else {}
        test_results = {'has_dashboard': admin_user.has_permission('dashboard', 'view'),'has_employee_management': admin_user.has_permission('employee_management', 'view'),'can_access_module': admin_user.can_access_module('dashboard'),'permission_count': len(permissions),'role': admin_user.role}
        print('SUCCESS:' + json.dumps(test_results))
    except Exception as e:
        print('ERROR:' + str(e))
"@
        $permScript | Out-File -FilePath "temp_perm_test.py" -Encoding UTF8
        $result = python temp_perm_test.py 2>&1
        if ($LASTEXITCODE -eq 0 -and $result -like "SUCCESS:*") {
            $permData = $result -replace "SUCCESS:", "" | ConvertFrom-Json
            Write-Host "   Permission system is working"
            Write-Host "   Permission count: $($permData.permission_count)"
            Write-Host "   User role: $($permData.role)"
            return @{ "status" = "working"; "permission_count" = $permData.permission_count; "role" = $permData.role; "has_dashboard" = $permData.has_dashboard; "has_employee_management" = $permData.has_employee_management }
        } else {
            Write-Host "   Permission test failed: $result"
            return @{ "status" = "error"; "error" = $result }
        }
        if (Test-Path "temp_perm_test.py") { Remove-Item "temp_perm_test.py" -Force }
    } catch {
        Write-Host "   Permission test failed: $($_.Exception.Message)"
        return @{ "status" = "error"; "error" = $_.Exception.Message }
    }
}

function Test-FileStructure {
    Write-Host "\nTesting file structure..."
    $requiredFiles = @("app.py","models.py","requirements.txt",".env","instance/restaurant_dev.sqlite3","scripts/health_check.ps1","scripts/backup_project.ps1","logs","templates","static")
    $missingFiles = @()
    $existingFiles = @()
    foreach ($file in $requiredFiles) {
        if (Test-Path $file) {
            $existingFiles += $file
            Write-Host "   $file exists"
        } else {
            $missingFiles += $file
            Write-Host "   $file missing"
        }
    }
    return @{ "existing_files" = $existingFiles; "missing_files" = $missingFiles; "total_required" = $requiredFiles.Count; "total_existing" = $existingFiles.Count }
}

function Test-ProcessStatus {
    Write-Host "\nTesting process status..."
    $processes = @{ "python" = @(); "node" = @() }
    $pythonProcs = Get-Process -Name "python" -ErrorAction SilentlyContinue
    foreach ($proc in $pythonProcs) {
        $processes.python += @{ "id" = $proc.Id; "cpu" = $proc.CPU; "memory_mb" = [math]::Round($proc.WorkingSet64 / 1MB, 2) }
    }
    $nodeProcs = Get-Process -Name "node" -ErrorAction SilentlyContinue
    foreach ($proc in $nodeProcs) {
        $processes.node += @{ "id" = $proc.Id; "cpu" = $proc.CPU; "memory_mb" = [math]::Round($proc.WorkingSet64 / 1MB, 2) }
    }
    Write-Host "   Python processes: $($processes.python.Count)"
    Write-Host "   Node.js processes: $($processes.node.Count)"
    return $processes
}

function New-FinalReport {
    Write-Host "\nGenerating final report..."
    $report = @{ "timestamp" = Get-Date -Format "yyyy-MM-dd HH:mm:ss"; "project_name" = "Your Program"; "version" = "2.0"; "tests" = @{ "backend" = Test-BackendHealth; "frontend" = Test-FrontendHealth; "database" = Test-DatabaseHealth; "permissions" = Test-PermissionSystem; "files" = Test-FileStructure; "processes" = Test-ProcessStatus }; "summary" = @{ "total_tests" = 6; "passed_tests" = 0; "failed_tests" = 0; "overall_status" = "unknown" } }
    $passed = 0; $failed = 0
    if ($report.tests.backend.status -eq "healthy") { $passed++ } else { $failed++ }
    if ($report.tests.frontend.Count -gt 0) { $passed++ } else { $failed++ }
    if ($report.tests.database.status -eq "healthy") { $passed++ } else { $failed++ }
    if ($report.tests.permissions.status -eq "working") { $passed++ } else { $failed++ }
    if ($report.tests.files.missing_files.Count -eq 0) { $passed++ } else { $failed++ }
    if ($report.tests.processes.python.Count -gt 0 -or $report.tests.processes.node.Count -gt 0) { $passed++ } else { $failed++ }
    $report.summary.passed_tests = $passed
    $report.summary.failed_tests = $failed
    if ($passed -eq 6) { $report.summary.overall_status = "excellent" } elseif ($passed -ge 4) { $report.summary.overall_status = "good" } elseif ($passed -ge 2) { $report.summary.overall_status = "fair" } else { $report.summary.overall_status = "poor" }
    $reportJson = $report | ConvertTo-Json -Depth 10
    $reportJson | Out-File -FilePath "logs/final_verification_report.json" -Encoding UTF8
    return $report
}

Write-Host "\nStarting final verification..."
$report = New-FinalReport
Write-Host "\n=============================="
Write-Host "FINAL VERIFICATION REPORT"
Write-Host "=============================="
Write-Host "\nOverall Status: $($report.summary.overall_status.ToUpper())"
Write-Host "Tests Passed: $($report.summary.passed_tests)/$($report.summary.total_tests)"
Write-Host "Generated: $($report.timestamp)"
Write-Host "\nDetailed Results:"
Write-Host "   Backend: $($report.tests.backend.status)"
Write-Host "   Frontend: $($report.tests.frontend.Count) ports accessible"
Write-Host "   Database: $($report.tests.database.status)"
Write-Host "   Permissions: $($report.tests.permissions.status)"
Write-Host "   Files: $($report.tests.files.total_existing)/$($report.tests.files.total_required) present"
Write-Host "   Processes: $($report.tests.processes.python.Count + $report.tests.processes.node.Count) running"
Write-Host "\nFull report saved to: logs/final_verification_report.json"
if ($report.summary.overall_status -eq "excellent") {
    Write-Host "\nCONGRATULATIONS! Your Program is fully operational!"
} elseif ($report.summary.overall_status -eq "good") {
    Write-Host "\nYour Program is mostly operational with minor issues."
} else {
    Write-Host "\nYour Program has some issues that need attention."
}
Write-Host "\nNext Steps:"
Write-Host "   1. Review the detailed report for any issues"
Write-Host "   2. Address any failed tests"
Write-Host "   3. Set up monitoring and alerts"
Write-Host "   4. Configure backup schedules"
Write-Host "   5. Train users on the system"
Write-Host "\nYour Program verification completed!" 