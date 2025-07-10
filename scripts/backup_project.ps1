# Your Program 백업 스크립트
# 프로젝트 전체를 백업하고 압축

$OutputEncoding = [Console]::OutputEncoding = [Text.Encoding]::UTF8

Write-Host "💾 Your Program Backup Script (백업 스크립트)" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Cyan

# 백업 설정
$backupDir = "backup_$(Get-Date -Format 'yyyy-MM-dd_HH-mm-ss')"
$backupPath = Join-Path $PWD $backupDir
$zipPath = "$backupPath.zip"

# 제외할 항목들
$excludePatterns = @(
    "venv",
    "node_modules",
    "__pycache__",
    "*.pyc",
    ".git",
    "*.log",
    "temp_*",
    "*.tmp",
    "instance",
    "logs",
    "test-results",
    "coverage",
    ".pytest_cache",
    ".coverage",
    "*.sqlite",
    "*.db"
)

Write-Host "`n📁 Creating backup directory: $backupDir" -ForegroundColor Yellow

# 백업 디렉토리 생성
if (Test-Path $backupPath) {
    Remove-Item $backupPath -Recurse -Force
}
New-Item -ItemType Directory -Path $backupPath | Out-Null

Write-Host "`n📋 Copying project files..." -ForegroundColor Yellow

# 파일 복사 함수
function Copy-ProjectFiles {
    param(
        [string]$SourcePath,
        [string]$DestinationPath
    )
    
    try {
        # 제외 패턴을 제외하고 파일 복사
        $excludeParams = @()
        foreach ($pattern in $excludePatterns) {
            $excludeParams += @("-exclude", $pattern)
        }
        
        # robocopy 사용 (더 안정적)
        $robocopyArgs = @(
            $SourcePath,
            $DestinationPath,
            "/E",           # 모든 하위 디렉토리 포함
            "/XD",          # 디렉토리 제외
            "venv",
            "node_modules",
            "__pycache__",
            ".git",
            "instance",
            "logs",
            "test-results",
            "coverage",
            ".pytest_cache",
            "/XF",          # 파일 제외
            "*.pyc",
            "*.log",
            "temp_*",
            "*.tmp",
            "*.sqlite",
            "*.db",
            "/R:3",         # 재시도 3회
            "/W:1",         # 대기 1초
            "/MT:4"         # 멀티스레드 4개
        )
        
        $result = & robocopy @robocopyArgs
        
        # robocopy는 성공 시에도 1-8을 반환할 수 있음
        if ($result -le 8) {
            Write-Host "✅ Files copied successfully" -ForegroundColor Green
            return $true
        } else {
            Write-Host "❌ File copy failed with exit code: $result" -ForegroundColor Red
            return $false
        }
    } catch {
        Write-Host "❌ Error copying files: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

# 프로젝트 파일 복사
$copySuccess = Copy-ProjectFiles -SourcePath $PWD -DestinationPath $backupPath

if ($copySuccess) {
    Write-Host "`n📦 Creating backup archive..." -ForegroundColor Yellow
    
    try {
        # PowerShell의 Compress-Archive 사용
        Compress-Archive -Path $backupPath\* -DestinationPath $zipPath -Force
        
        # 원본 디렉토리 삭제
        Remove-Item $backupPath -Recurse -Force
        
        # 백업 정보 표시
        $zipSize = (Get-Item $zipPath).Length
        $zipSizeMB = [math]::Round($zipSize / 1MB, 2)
        
        Write-Host "`n✅ Backup completed successfully!" -ForegroundColor Green
        Write-Host "📁 Backup file: $zipPath" -ForegroundColor White
        Write-Host "📊 Size: $zipSizeMB MB" -ForegroundColor White
        Write-Host "🕒 Created: $(Get-Date)" -ForegroundColor White
        
        # 백업 목록 표시
        Write-Host "`n📋 Recent backups:" -ForegroundColor Yellow
        Get-ChildItem -Path $PWD -Filter "backup_*.zip" | 
            Sort-Object LastWriteTime -Descending | 
            Select-Object -First 5 | 
            ForEach-Object {
                $size = [math]::Round($_.Length / 1MB, 2)
                Write-Host "   $($_.Name) - $size MB - $($_.LastWriteTime)" -ForegroundColor White
            }
        
    } catch {
        Write-Host "❌ Error creating backup archive: $($_.Exception.Message)" -ForegroundColor Red
        Write-Host "📁 Backup files are still available in: $backupPath" -ForegroundColor Yellow
    }
} else {
    Write-Host "❌ Backup failed due to file copy errors" -ForegroundColor Red
}

Write-Host "`nBackup process completed at: $(Get-Date)" -ForegroundColor Cyan 