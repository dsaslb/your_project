# Your Program 마스터 자동화 스크립트
# 백업, 정리, 프로젝트명 변경, 복원을 통합 관리

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet("backup", "cleanup", "rename", "restore", "full", "setup", "help")]
    [string]$Action = "help",
    
    [string]$BackupType = "full",
    [string]$BackupPath = "backups",
    [string]$RestorePath = "",
    [string]$CleanupType = "all",
    [switch]$Force,
    [switch]$DryRun
)

function Show-Help {
    Write-Host "🚀 Your Program 마스터 자동화 스크립트" -ForegroundColor Green
    Write-Host "================================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "사용법:" -ForegroundColor Yellow
    Write-Host "  .\scripts\master_automation.ps1 -Action <action> [옵션]" -ForegroundColor White
    Write-Host ""
    Write-Host "액션:" -ForegroundColor Yellow
    Write-Host "  backup    - 프로젝트 백업" -ForegroundColor White
    Write-Host "  cleanup   - 불필요 파일 정리" -ForegroundColor White
    Write-Host "  rename    - 프로젝트명 변경 (restaurant → your_program)" -ForegroundColor White
    Write-Host "  restore   - 백업에서 복원" -ForegroundColor White
    Write-Host "  full      - 전체 프로세스 (백업 → 정리 → 변경)" -ForegroundColor White
    Write-Host "  setup     - 초기 설정 (가상환경, 의존성 설치)" -ForegroundColor White
    Write-Host "  help      - 도움말 표시" -ForegroundColor White
    Write-Host ""
    Write-Host "옵션:" -ForegroundColor Yellow
    Write-Host "  -BackupType <type>     - 백업 타입 (full, db, config, code)" -ForegroundColor White
    Write-Host "  -BackupPath <path>     - 백업 경로" -ForegroundColor White
    Write-Host "  -RestorePath <path>    - 복원할 백업 경로" -ForegroundColor White
    Write-Host "  -CleanupType <type>    - 정리 타입 (all, cache, backup, temp, venv)" -ForegroundColor White
    Write-Host "  -Force                 - 강제 실행 (확인 없이)" -ForegroundColor White
    Write-Host "  -DryRun                - 미리보기 모드 (실제 변경 없음)" -ForegroundColor White
    Write-Host ""
    Write-Host "예시:" -ForegroundColor Yellow
    Write-Host "  .\scripts\master_automation.ps1 -Action backup" -ForegroundColor White
    Write-Host "  .\scripts\master_automation.ps1 -Action cleanup -CleanupType cache" -ForegroundColor White
    Write-Host "  .\scripts\master_automation.ps1 -Action rename -DryRun" -ForegroundColor White
    Write-Host "  .\scripts\master_automation.ps1 -Action restore -RestorePath backups\backup_2024-01-01_12-00-00" -ForegroundColor White
    Write-Host "  .\scripts\master_automation.ps1 -Action full -Force" -ForegroundColor White
    Write-Host "  .\scripts\master_automation.ps1 -Action setup" -ForegroundColor White
}

function Invoke-Backup {
    Write-Host "🔄 백업 실행 중..." -ForegroundColor Green
    $backupScript = ".\scripts\backup_project.ps1"
    if (Test-Path $backupScript) {
        & $backupScript -BackupType $BackupType -BackupPath $BackupPath
    } else {
        Write-Host "❌ 백업 스크립트를 찾을 수 없습니다: $backupScript" -ForegroundColor Red
        return $false
    }
    return $true
}

function Invoke-Cleanup {
    Write-Host "🔄 정리 실행 중..." -ForegroundColor Green
    $cleanupScript = ".\scripts\cleanup_project.ps1"
    if (Test-Path $cleanupScript) {
        & $cleanupScript -CleanupType $CleanupType -Force:$Force
    } else {
        Write-Host "❌ 정리 스크립트를 찾을 수 없습니다: $cleanupScript" -ForegroundColor Red
        return $false
    }
    return $true
}

function Invoke-Rename {
    Write-Host "🔄 프로젝트명 변경 실행 중..." -ForegroundColor Green
    $renameScript = ".\scripts\rename_project.ps1"
    if (Test-Path $renameScript) {
        & $renameScript -Force:$Force -DryRun:$DryRun
    } else {
        Write-Host "❌ 변경 스크립트를 찾을 수 없습니다: $renameScript" -ForegroundColor Red
        return $false
    }
    return $true
}

function Invoke-Restore {
    if ([string]::IsNullOrEmpty($RestorePath)) {
        Write-Host "❌ 복원 경로를 지정해주세요: -RestorePath <path>" -ForegroundColor Red
        return $false
    }
    
    Write-Host "🔄 복원 실행 중..." -ForegroundColor Green
    $restoreScript = ".\scripts\restore_project.ps1"
    if (Test-Path $restoreScript) {
        & $restoreScript -BackupPath $RestorePath -Force:$Force
    } else {
        Write-Host "❌ 복원 스크립트를 찾을 수 없습니다: $restoreScript" -ForegroundColor Red
        return $false
    }
    return $true
}

function Invoke-Setup {
    Write-Host "🔄 초기 설정 실행 중..." -ForegroundColor Green
    
    # 1. 가상환경 생성
    Write-Host "📦 가상환경 생성 중..." -ForegroundColor Yellow
    if (Test-Path "venv") {
        Write-Host "⚠️ 기존 venv 폴더가 있습니다. 삭제하시겠습니까? (y/N)" -ForegroundColor Yellow
        $confirm = Read-Host
        if ($confirm -eq "y" -or $confirm -eq "Y") {
            Remove-Item -Path "venv" -Recurse -Force
        } else {
            Write-Host "❌ 가상환경 생성이 취소되었습니다." -ForegroundColor Red
            return $false
        }
    }
    
    python -m venv venv
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ 가상환경 생성 실패" -ForegroundColor Red
        return $false
    }
    
    # 2. 가상환경 활성화
    Write-Host "🔧 가상환경 활성화 중..." -ForegroundColor Yellow
    & ".\venv\Scripts\Activate.ps1"
    
    # 3. 의존성 설치
    Write-Host "📦 의존성 설치 중..." -ForegroundColor Yellow
    if (Test-Path "requirements.txt") {
        pip install -r requirements.txt
        if ($LASTEXITCODE -ne 0) {
            Write-Host "❌ 의존성 설치 실패" -ForegroundColor Red
            return $false
        }
    }
    
    if (Test-Path "ai_requirements.txt") {
        pip install -r ai_requirements.txt
        if ($LASTEXITCODE -ne 0) {
            Write-Host "❌ AI 의존성 설치 실패" -ForegroundColor Red
            return $false
        }
    }
    
    # 4. 데이터베이스 마이그레이션
    Write-Host "🗄️ 데이터베이스 마이그레이션 중..." -ForegroundColor Yellow
    flask db upgrade
    if ($LASTEXITCODE -ne 0) {
        Write-Host "⚠️ 데이터베이스 마이그레이션 실패 (무시하고 계속)" -ForegroundColor Yellow
    }
    
    # 5. 프론트엔드 의존성 설치
    Write-Host "🎨 프론트엔드 의존성 설치 중..." -ForegroundColor Yellow
    if (Test-Path "frontend") {
        Push-Location "frontend"
        npm install
        if ($LASTEXITCODE -ne 0) {
            Write-Host "❌ 프론트엔드 의존성 설치 실패" -ForegroundColor Red
            Pop-Location
            return $false
        }
        Pop-Location
    }
    
    Write-Host "✅ 초기 설정 완료!" -ForegroundColor Green
    return $true
}

# 메인 실행 로직
Write-Host "🚀 Your Program 마스터 자동화 시작..." -ForegroundColor Green
Write-Host "액션: $Action" -ForegroundColor Yellow

$startTime = Get-Date
$success = $false

try {
    switch ($Action) {
        "backup" {
            $success = Invoke-Backup
        }
        "cleanup" {
            $success = Invoke-Cleanup
        }
        "rename" {
            $success = Invoke-Rename
        }
        "restore" {
            $success = Invoke-Restore
        }
        "full" {
            Write-Host "🔄 전체 프로세스 실행 중..." -ForegroundColor Green
            Write-Host "1. 백업 → 2. 정리 → 3. 프로젝트명 변경" -ForegroundColor Cyan
            
            $success = Invoke-Backup
            if ($success) {
                $success = Invoke-Cleanup
            }
            if ($success) {
                $success = Invoke-Rename
            }
        }
        "setup" {
            $success = Invoke-Setup
        }
        "help" {
            Show-Help
            $success = $true
        }
        default {
            Write-Host "❌ 알 수 없는 액션: $Action" -ForegroundColor Red
            Show-Help
            $success = $false
        }
    }
} catch {
    Write-Host "❌ 실행 중 오류 발생: $($_.Exception.Message)" -ForegroundColor Red
    $success = $false
}

# 실행 완료 요약
$endTime = Get-Date
$duration = $endTime - $startTime

Write-Host "`n📋 실행 완료 요약:" -ForegroundColor Cyan
Write-Host "액션: $Action" -ForegroundColor White
Write-Host "소요 시간: $($duration.TotalSeconds)초" -ForegroundColor White
Write-Host "결과: $(if ($success) { '성공' } else { '실패' })" -ForegroundColor $(if ($success) { 'Green' } else { 'Red' })

if ($success) {
    Write-Host "`n🎉 작업이 성공적으로 완료되었습니다!" -ForegroundColor Green
} else {
    Write-Host "`n❌ 작업이 실패했습니다. 로그를 확인해주세요." -ForegroundColor Red
    exit 1
} 
