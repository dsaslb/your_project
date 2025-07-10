# Your Program 프로젝트 정리 스크립트
# 중복/불필요/캐시 파일 정리

$OutputEncoding = [Console]::OutputEncoding = [Text.Encoding]::UTF8

param(
    [string]$CleanupType = "all",  # all, cache, backup, temp, venv
    [switch]$Force  # 강제 삭제 (확인 없이)
)

Write-Host "🧹 Your Program Cleanup Start... (프로젝트 정리 시작)" -ForegroundColor Green
Write-Host "Cleanup type: $CleanupType (정리 타입)" -ForegroundColor Yellow

# 정리 로그 파일
$cleanupLogFile = "cleanup_log_$(Get-Date -Format 'yyyy-MM-dd_HH-mm-ss').txt"
$startTime = Get-Date
$totalSizeFreed = 0

function Write-Log {
    param([string]$Message)
    $logMessage = "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss'): $Message"
    Write-Host $logMessage -ForegroundColor Cyan
    Add-Content -Path $cleanupLogFile -Value $logMessage
}

function Get-FolderSize {
    param([string]$Path)
    if (Test-Path $Path) {
        return (Get-ChildItem -Path $Path -Recurse -File | Measure-Object -Property Length -Sum).Sum
    }
    return 0
}

Write-Log "Cleanup start: $startTime (정리 시작)"

# 강제 삭제 확인
if (!$Force) {
    $confirm = Read-Host "⚠️ This will delete unnecessary files. Continue? (y/N) (불필요한 파일들을 삭제합니다. 계속하시겠습니까?)"
    if ($confirm -ne "y" -and $confirm -ne "Y") {
        Write-Host "❌ Cleanup cancelled. (정리가 취소되었습니다.)" -ForegroundColor Red
        exit 0
    }
}

try {
    # 1. 캐시 파일 정리 (all 또는 cache)
    if ($CleanupType -eq "all" -or $CleanupType -eq "cache") {
        Write-Log "🗑️ Cleaning cache files... (캐시 파일 정리 중)"
        
        $cacheItems = @(
            "__pycache__",
            ".pytest_cache",
            ".coverage",
            "coverage.xml",
            ".next",
            "dist",
            "build",
            "*.egg-info",
            ".parcel-cache",
            ".cache"
        )
        
        foreach ($item in $cacheItems) {
            if (Test-Path $item) {
                $sizeBefore = Get-FolderSize $item
                Remove-Item -Path $item -Recurse -Force
                $totalSizeFreed += $sizeBefore
                Write-Log "Cache deleted: $item (${sizeBefore} bytes) (캐시 삭제)"
            }
        }
    }
    
    # 2. 백업 폴더 정리 (all 또는 backup)
    if ($CleanupType -eq "all" -or $CleanupType -eq "backup") {
        Write-Log "🗑️ Cleaning backup folders... (백업 폴더 정리 중)"
        
        $backupItems = @(
            "backup_*",
            "backups"
        )
        
        foreach ($item in $backupItems) {
            if (Test-Path $item) {
                $sizeBefore = Get-FolderSize $item
                Remove-Item -Path $item -Recurse -Force
                $totalSizeFreed += $sizeBefore
                Write-Log "Backup deleted: $item (${sizeBefore} bytes) (백업 삭제)"
            }
        }
    }
    
    # 3. 임시 파일 정리 (all 또는 temp)
    if ($CleanupType -eq "all" -or $CleanupType -eq "temp") {
        Write-Log "🗑️ Cleaning temp files... (임시 파일 정리 중)"
        
        $tempItems = @(
            "*.tmp",
            "*.temp",
            "*.log",
            "logs",
            "test-results",
            "tmp",
            "temp"
        )
        
        foreach ($item in $tempItems) {
            if (Test-Path $item) {
                $sizeBefore = Get-FolderSize $item
                Remove-Item -Path $item -Recurse -Force
                $totalSizeFreed += $sizeBefore
                Write-Log "Temp deleted: $item (${sizeBefore} bytes) (임시 파일 삭제)"
            }
        }
    }
    
    # 4. 가상환경 정리 (all 또는 venv)
    if ($CleanupType -eq "all" -or $CleanupType -eq "venv") {
        Write-Log "🗑️ Cleaning virtual environments... (가상환경 정리 중)"
        
        $venvItems = @(
            "venv_py313",
            "ai_env",
            "env",
            ".venv"
        )
        
        foreach ($item in $venvItems) {
            if (Test-Path $item) {
                $sizeBefore = Get-FolderSize $item
                Remove-Item -Path $item -Recurse -Force
                $totalSizeFreed += $sizeBefore
                Write-Log "Venv deleted: $item (${sizeBefore} bytes) (가상환경 삭제)"
            }
        }
    }
    
    # 5. 중복/불필요 파일 정리
    if ($CleanupType -eq "all") {
        Write-Log "🗑️ Cleaning unnecessary files... (중복/불필요 파일 정리 중)"
        
        $unnecessaryItems = @(
            "cleanup_unnecessary_files.ps1",
            "backup_restore_scripts.ps1",
            "*.backup",
            "*.bak",
            "*_backup.*"
        )
        
        foreach ($item in $unnecessaryItems) {
            if (Test-Path $item) {
                $sizeBefore = Get-FolderSize $item
                Remove-Item -Path $item -Recurse -Force
                $totalSizeFreed += $sizeBefore
                Write-Log "Unnecessary deleted: $item (${sizeBefore} bytes) (불필요 파일 삭제)"
            }
        }
    }
    
    # 6. 정리 완료 요약
    $endTime = Get-Date
    $duration = $endTime - $startTime
    $sizeFreedMB = [math]::Round($totalSizeFreed / 1MB, 2)
    
    Write-Log "✅ Cleanup complete! (정리 완료)"
    Write-Log "Duration: $($duration.TotalSeconds) sec (소요 시간)"
    Write-Log "Freed: ${sizeFreedMB}MB (정리된 용량)"
    
    # 정리 완료 알림
    Write-Host "`n🎉 Cleanup completed successfully! (정리가 성공적으로 완료되었습니다!)" -ForegroundColor Green
    Write-Host "📊 Freed: ${sizeFreedMB}MB (정리된 용량)" -ForegroundColor Yellow
    Write-Host "📋 Log file: $cleanupLogFile (로그 파일)" -ForegroundColor Yellow
    
    # 다음 단계 안내
    Write-Host "`n📋 Next steps: (다음 단계 권장사항)" -ForegroundColor Cyan
    Write-Host "1. Recreate venv: python -m venv venv (가상환경 재생성)" -ForegroundColor White
    Write-Host "2. Reinstall dependencies: pip install -r requirements.txt (의존성 재설치)" -ForegroundColor White
    Write-Host "3. Project rename: run rename script (프로젝트명 변경 작업 진행)" -ForegroundColor White
    
} catch {
    Write-Log "❌ Cleanup error: $($_.Exception.Message) (정리 중 오류 발생)"
    Write-Host "❌ Cleanup failed: $($_.Exception.Message) (정리 실패)" -ForegroundColor Red
    exit 1
}

Write-Log "Cleanup script end. (정리 스크립트 종료)" 