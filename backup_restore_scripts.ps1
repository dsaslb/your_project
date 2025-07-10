# your_program 백업 및 복원 스크립트
# 사용법: .\backup_restore_scripts.ps1

param(
    [Parameter(Mandatory=$false)]
    [string]$Action = "backup",  # backup, restore, list, cleanup
    
    [Parameter(Mandatory=$false)]
    [string]$BackupPath = "",
    
    [Parameter(Mandatory=$false)]
    [string]$RestorePath = "",
    
    [Parameter(Mandatory=$false)]
    [switch]$Force
)

function Create-Backup {
    $timestamp = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
    $backupDir = "backup_$timestamp"
    
    Write-Host "your_program 백업 생성 중: $backupDir" -ForegroundColor Green
    
    # 프로젝트 루트 파일들 (핵심 파일들)
    $filesToBackup = @(
        "*.py", "*.md", "*.json", "*.txt", "*.yml", "*.yaml", 
        ".env*", "requirements.txt", "package.json", "*.bat", "*.sh",
        "*.conf", "*.ini", "*.cfg", "*.ps1"
    )
    
    # 백업할 디렉토리들 (핵심 구조)
    $dirsToBackup = @(
        "restaurant_frontend", "mobile_app", "api", "routes", 
        "templates", "static", "tests", "migrations", "instance",
        "microservices", "kubernetes", "grafana", "helm-charts",
        "docs", "scripts", "services", "utils", "plugins", "core",
        "core_framework", "ai_models", "ai_plugins", "blueprints",
        "logs", "ai_env"
    )
    
    # 백업 디렉토리 생성
    New-Item -ItemType Directory -Path $backupDir -Force | Out-Null
    
    # 파일 백업
    foreach ($pattern in $filesToBackup) {
        Get-ChildItem -Path . -Name $pattern -ErrorAction SilentlyContinue | ForEach-Object {
            Copy-Item -Path $_ -Destination $backupDir -Force
            Write-Host "  백업됨: $_" -ForegroundColor Gray
        }
    }
    
    # 디렉토리 백업
    foreach ($dir in $dirsToBackup) {
        if (Test-Path $dir) {
            Copy-Item -Path $dir -Destination $backupDir -Recurse -Force
            Write-Host "  백업됨: $dir/" -ForegroundColor Gray
        }
    }
    
    # 데이터베이스 백업 (instance 폴더)
    if (Test-Path "instance") {
        Copy-Item -Path "instance" -Destination $backupDir -Recurse -Force
        Write-Host "  데이터베이스 백업됨: instance/" -ForegroundColor Gray
    }
    
    # 백업 정보 저장
    $backupInfo = @{
        timestamp = $timestamp
        date = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        description = "your_program 전체 백업"
        files = (Get-ChildItem -Path $backupDir -Recurse | Measure-Object).Count
        version = "2.0"
        project = "your_program"
    }
    
    $backupInfo | ConvertTo-Json | Out-File -FilePath "$backupDir\backup_info.json" -Encoding UTF8
    
    # 백업 완료 보고서
    $totalSize = (Get-ChildItem -Path $backupDir -Recurse | Measure-Object -Property Length -Sum).Sum
    $sizeMB = [math]::Round($totalSize / 1MB, 2)
    
    Write-Host "백업 완료: $backupDir" -ForegroundColor Green
    Write-Host "백업된 파일 수: $($backupInfo.files)" -ForegroundColor Yellow
    Write-Host "백업 크기: $sizeMB MB" -ForegroundColor Yellow
}

function Restore-Backup {
    param([string]$BackupPath, [switch]$Force)
    
    if (-not $BackupPath) {
        Write-Host "복원할 백업 경로를 지정해주세요." -ForegroundColor Red
        return
    }
    
    if (-not (Test-Path $BackupPath)) {
        Write-Host "백업 경로를 찾을 수 없습니다: $BackupPath" -ForegroundColor Red
        return
    }
    
    if (-not $Force) {
        Write-Host "⚠️  경고: 현재 프로젝트가 덮어써집니다!" -ForegroundColor Red
        $confirm = Read-Host "계속하시겠습니까? (y/N)"
        if ($confirm -ne "y" -and $confirm -ne "Y") {
            Write-Host "복원이 취소되었습니다." -ForegroundColor Yellow
            return
        }
    }
    
    Write-Host "백업 복원 중: $BackupPath" -ForegroundColor Green
    
    # 현재 상태 안전 백업 (자동)
    $safetyBackup = "safety_backup_$(Get-Date -Format 'yyyy-MM-dd_HH-mm-ss')"
    Write-Host "안전 백업 생성 중: $safetyBackup" -ForegroundColor Yellow
    Create-Backup
    
    # 복원 실행
    Copy-Item -Path "$BackupPath\*" -Destination . -Recurse -Force
    
    Write-Host "복원 완료" -ForegroundColor Green
    Write-Host "안전 백업 위치: $safetyBackup" -ForegroundColor Cyan
}

function List-Backups {
    $backups = Get-ChildItem -Path . -Name "backup_*" -Directory | Sort-Object -Descending
    
    if ($backups.Count -eq 0) {
        Write-Host "백업이 없습니다." -ForegroundColor Yellow
        return
    }
    
    Write-Host "사용 가능한 백업:" -ForegroundColor Green
    foreach ($backup in $backups) {
        $infoPath = "$backup\backup_info.json"
        if (Test-Path $infoPath) {
            $info = Get-Content $infoPath | ConvertFrom-Json
            $size = (Get-ChildItem -Path $backup -Recurse | Measure-Object -Property Length -Sum).Sum
            $sizeMB = [math]::Round($size / 1MB, 2)
            Write-Host "  $backup - $($info.date) ($($info.files) files, $sizeMB MB)" -ForegroundColor Cyan
        } else {
            Write-Host "  $backup" -ForegroundColor Cyan
        }
    }
}

function Cleanup-OldBackups {
    param([int]$KeepDays = 7)
    
    Write-Host "오래된 백업 정리 중 (최근 $KeepDays일 유지)..." -ForegroundColor Yellow
    
    $cutoffDate = (Get-Date).AddDays(-$KeepDays)
    $oldBackups = Get-ChildItem -Path . -Name "backup_*" -Directory | Where-Object {
        $backupDate = [datetime]::ParseExact($_.Split('_')[1..3] -join '-', "yyyy-MM-dd", $null)
        $backupDate -lt $cutoffDate
    }
    
    if ($oldBackups.Count -eq 0) {
        Write-Host "정리할 오래된 백업이 없습니다." -ForegroundColor Green
        return
    }
    
    foreach ($backup in $oldBackups) {
        Remove-Item -Path $backup -Recurse -Force
        Write-Host "  삭제됨: $backup" -ForegroundColor Red
    }
    
    Write-Host "정리 완료: $($oldBackups.Count)개 백업 삭제" -ForegroundColor Green
}

# 메인 실행
switch ($Action.ToLower()) {
    "backup" { Create-Backup }
    "restore" { Restore-Backup -BackupPath $RestorePath -Force:$Force }
    "list" { List-Backups }
    "cleanup" { Cleanup-OldBackups }
    default { 
        Write-Host "your_program 백업/복원 스크립트 사용법:" -ForegroundColor Yellow
        Write-Host "  .\backup_restore_scripts.ps1 -Action backup" -ForegroundColor White
        Write-Host "  .\backup_restore_scripts.ps1 -Action restore -RestorePath backup_2025-07-10_16-25-52" -ForegroundColor White
        Write-Host "  .\backup_restore_scripts.ps1 -Action list" -ForegroundColor White
        Write-Host "  .\backup_restore_scripts.ps1 -Action cleanup" -ForegroundColor White
    }
} 