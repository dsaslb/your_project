# your_program 불필요 파일 정리 스크립트
# 사용법: .\cleanup_unnecessary_files.ps1

Write-Host "your_program 불필요 파일 정리 시작..." -ForegroundColor Green

# 1. Python 캐시 파일들
Write-Host "1. Python 캐시 파일 정리 중..." -ForegroundColor Yellow
Get-ChildItem -Recurse -Name "*.pyc" -ErrorAction SilentlyContinue | Remove-Item -Force
Get-ChildItem -Recurse -Directory -Name "__pycache__" -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force
Get-ChildItem -Recurse -Directory -Name ".pytest_cache" -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force

# 2. Node.js 관련 캐시
Write-Host "2. Node.js 캐시 파일 정리 중..." -ForegroundColor Yellow
Get-ChildItem -Recurse -Directory -Name "node_modules" -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force
Get-ChildItem -Recurse -Directory -Name ".next" -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force
Get-ChildItem -Recurse -Directory -Name ".swc" -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force

# 3. 임시 파일들
Write-Host "3. 임시 파일 정리 중..." -ForegroundColor Yellow
Get-ChildItem -Recurse -Name "*.tmp" -ErrorAction SilentlyContinue | Remove-Item -Force
Get-ChildItem -Recurse -Name "*.temp" -ErrorAction SilentlyContinue | Remove-Item -Force
Get-ChildItem -Recurse -Name "*.log" -ErrorAction SilentlyContinue | Remove-Item -Force
Get-ChildItem -Recurse -Name ".DS_Store" -ErrorAction SilentlyContinue | Remove-Item -Force
Get-ChildItem -Recurse -Name "Thumbs.db" -ErrorAction SilentlyContinue | Remove-Item -Force

# 4. 더미/테스트 파일들 (확인 후 삭제)
Write-Host "4. 더미/테스트 파일 확인 중..." -ForegroundColor Yellow
$dummyFiles = @(
    "create_hierarchical_data.py",
    "create_staff_templates.py", 
    "setup_ai_environment.py",
    "ai_client.py",
    "ai_server.py",
    "websocket_server.py",
    "app_plugin_integration.py"
)

foreach ($file in $dummyFiles) {
    if (Test-Path $file) {
        Write-Host "  삭제됨: $file" -ForegroundColor Red
        Remove-Item -Path $file -Force
    }
}

# 5. 불필요한 문서 파일들
Write-Host "5. 불필요한 문서 파일 정리 중..." -ForegroundColor Yellow
$unnecessaryDocs = @(
    "PHASE10_4_COMPLETION_SUMMARY.md",
    "PLUGIN_PLATFORM_ARCHITECTURE.md",
    "EFFICIENT_STAFF_MANAGEMENT_PROPOSAL.md",
    "ATTENDANCE_FEATURES_SUMMARY.md",
    "MENU_CSS_GUIDE.md",
    "SENTRY_SLACK_README.md",
    "OPERATOR_MANUAL.md",
    "ONBOARDING.md",
    "FAQ.md",
    "CHANGELOG.md",
    "BACKLOG.md"
)

foreach ($doc in $unnecessaryDocs) {
    if (Test-Path $doc) {
        Write-Host "  삭제됨: $doc" -ForegroundColor Red
        Remove-Item -Path $doc -Force
    }
}

# 6. 불필요한 디렉토리들
Write-Host "6. 불필요한 디렉토리 정리 중..." -ForegroundColor Yellow
$unnecessaryDirs = @(
    "ai_models",
    "ai_plugins", 
    "ai_env",
    "plugins",
    "microservices",
    "helm-charts"
)

foreach ($dir in $unnecessaryDirs) {
    if (Test-Path $dir) {
        Write-Host "  삭제됨: $dir/" -ForegroundColor Red
        Remove-Item -Path $dir -Recurse -Force
    }
}

# 7. 가상환경 정리 (venv 폴더는 유지, 다른 것들 삭제)
Write-Host "7. 가상환경 정리 중..." -ForegroundColor Yellow
Get-ChildItem -Directory -Name "venv_*" -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force

# 8. 백업 파일들 (최근 3개만 유지)
Write-Host "8. 오래된 백업 파일 정리 중..." -ForegroundColor Yellow
$backups = Get-ChildItem -Directory -Name "backup_*" | Sort-Object -Descending
if ($backups.Count -gt 3) {
    $oldBackups = $backups[3..($backups.Count-1)]
    foreach ($backup in $oldBackups) {
        Write-Host "  삭제됨: $backup" -ForegroundColor Red
        Remove-Item -Path $backup -Recurse -Force
    }
}

Write-Host "정리 완료!" -ForegroundColor Green

# 정리 후 상태 확인
$remainingFiles = (Get-ChildItem -Recurse | Measure-Object).Count
Write-Host "남은 파일 수: $remainingFiles" -ForegroundColor Cyan 