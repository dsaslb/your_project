# Your Program 프로젝트 복원 스크립트
# 백업에서 프로젝트 복원 및 롤백 기능

param(
    [Parameter(Mandatory=$true)]
    [string]$BackupPath,  # 복원할 백업 경로
    [string]$RestoreType = "full",  # full, db, config, code
    [switch]$Force  # 강제 복원 (기존 파일 덮어쓰기)
)

Write-Host "🔄 Your Program 프로젝트 복원 시작..." -ForegroundColor Green
Write-Host "백업 경로: $BackupPath" -ForegroundColor Yellow
Write-Host "복원 타입: $RestoreType" -ForegroundColor Yellow

# 백업 경로 확인
if (!(Test-Path $BackupPath)) {
    Write-Host "❌ 백업 경로를 찾을 수 없습니다: $BackupPath" -ForegroundColor Red
    exit 1
}

# 백업 메타데이터 확인
$metadataFile = "$BackupPath\backup_metadata.json"
if (!(Test-Path $metadataFile)) {
    Write-Host "❌ 백업 메타데이터를 찾을 수 없습니다: $metadataFile" -ForegroundColor Red
    exit 1
}

# 메타데이터 로드
$metadata = Get-Content -Path $metadataFile | ConvertFrom-Json
Write-Host "📋 백업 정보:" -ForegroundColor Cyan
Write-Host "  - 백업 타입: $($metadata.backup_type)" -ForegroundColor White
Write-Host "  - 백업 시간: $($metadata.timestamp)" -ForegroundColor White
Write-Host "  - 파일 수: $($metadata.files_count)개" -ForegroundColor White
Write-Host "  - 백업 크기: $($metadata.total_size_mb)MB" -ForegroundColor White

# 복원 로그 파일
$restoreLogFile = "restore_log_$(Get-Date -Format 'yyyy-MM-dd_HH-mm-ss').txt"
$startTime = Get-Date

function Write-Log {
    param([string]$Message)
    $logMessage = "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss'): $Message"
    Write-Host $logMessage -ForegroundColor Cyan
    Add-Content -Path $restoreLogFile -Value $logMessage
}

Write-Log "복원 시작: $startTime"

# 강제 복원 확인
if (!$Force) {
    $confirm = Read-Host "⚠️ 기존 파일을 덮어쓰게 됩니다. 계속하시겠습니까? (y/N)"
    if ($confirm -ne "y" -and $confirm -ne "Y") {
        Write-Host "❌ 복원이 취소되었습니다." -ForegroundColor Red
        exit 0
    }
}

try {
    # 1. 전체 프로젝트 복원 (full 또는 code)
    if ($RestoreType -eq "full" -or $RestoreType -eq "code") {
        Write-Log "📁 전체 프로젝트 파일 복원 중..."
        
        # 복원할 폴더 목록
        $restoreFolders = @(
            "templates", "static", "api", "routes", "utils",
            "your_program_frontend", "mobile_app",
            "kubernetes", "scripts", "docs",
            ".github", ".vscode"
        )
        
        foreach ($folder in $restoreFolders) {
            $sourcePath = "$BackupPath\$folder"
            if (Test-Path $sourcePath) {
                if (Test-Path $folder) {
                    Remove-Item -Path $folder -Recurse -Force
                }
                Copy-Item -Path $sourcePath -Destination $folder -Recurse -Force
                Write-Log "폴더 복원: $folder"
            }
        }
        
        # 복원할 파일 목록
        $restoreFiles = @(
            "*.py", "*.js", "*.ts", "*.tsx", "*.jsx",
            "*.json", "*.yml", "*.yaml", "*.md", "*.txt",
            "*.bat", "*.ps1", "*.sh", "*.html", "*.css", "*.scss",
            "requirements.txt", "ai_requirements.txt",
            "Dockerfile*", "docker-compose*.yml",
            "alembic.ini", "config.py"
        )
        
        foreach ($filePattern in $restoreFiles) {
            $sourceFiles = Get-ChildItem -Path $BackupPath -Filter $filePattern -File
            foreach ($file in $sourceFiles) {
                Copy-Item -Path $file.FullName -Destination $file.Name -Force
                Write-Log "파일 복원: $($file.Name)"
            }
        }
    }
    
    # 2. 데이터베이스 복원 (full 또는 db)
    if ($RestoreType -eq "full" -or $RestoreType -eq "db") {
        Write-Log "🗄️ 데이터베이스 복원 중..."
        
        # instance 폴더 생성
        if (!(Test-Path "instance")) {
            New-Item -ItemType Directory -Path "instance" -Force
        }
        
        # 데이터베이스 파일 복원
        $dbBackupPath = "$BackupPath\database"
        if (Test-Path $dbBackupPath) {
            $dbFiles = Get-ChildItem -Path $dbBackupPath -Filter "*.db"
            foreach ($dbFile in $dbFiles) {
                Copy-Item -Path $dbFile.FullName -Destination "instance\$($dbFile.Name)" -Force
                Write-Log "DB 복원: $($dbFile.Name)"
            }
        }
        
        # 마이그레이션 복원
        $migrationsBackupPath = "$BackupPath\migrations"
        if (Test-Path $migrationsBackupPath) {
            if (Test-Path "migrations") {
                Remove-Item -Path "migrations" -Recurse -Force
            }
            Copy-Item -Path $migrationsBackupPath -Destination "migrations" -Recurse -Force
            Write-Log "마이그레이션 복원 완료"
        }
    }
    
    # 3. 설정 파일 복원 (full 또는 config)
    if ($RestoreType -eq "full" -or $RestoreType -eq "config") {
        Write-Log "⚙️ 설정 파일 복원 중..."
        
        $configBackupPath = "$BackupPath\config"
        if (Test-Path $configBackupPath) {
            $configFiles = Get-ChildItem -Path $configBackupPath -File
            foreach ($configFile in $configFiles) {
                Copy-Item -Path $configFile.FullName -Destination $configFile.Name -Force
                Write-Log "설정 복원: $($configFile.Name)"
            }
        }
    }
    
    # 4. 복원 완료 요약
    $endTime = Get-Date
    $duration = $endTime - $startTime
    
    Write-Log "✅ 복원 완료!"
    Write-Log "소요 시간: $($duration.TotalSeconds)초"
    
    # 복원 완료 알림
    Write-Host "`n🎉 복원이 성공적으로 완료되었습니다!" -ForegroundColor Green
    Write-Host "📋 로그 파일: $restoreLogFile" -ForegroundColor Yellow
    
    # 다음 단계 안내
    Write-Host "`n📋 다음 단계 권장사항:" -ForegroundColor Cyan
    Write-Host "1. 가상환경 재설정: python -m venv venv" -ForegroundColor White
    Write-Host "2. 의존성 설치: pip install -r requirements.txt" -ForegroundColor White
    Write-Host "3. 데이터베이스 마이그레이션: flask db upgrade" -ForegroundColor White
    Write-Host "4. 서버 실행 테스트: python app.py" -ForegroundColor White
    
} catch {
    Write-Log "❌ 복원 중 오류 발생: $($_.Exception.Message)"
    Write-Host "❌ 복원 실패: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

Write-Log "복원 스크립트 종료" 