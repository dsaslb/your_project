# Your Program 프로젝트명 변경 스크립트
# restaurant에서 your_program으로 일괄 변경

$OutputEncoding = [Console]::OutputEncoding = [Text.Encoding]::UTF8

Write-Host "🔄 Your Program Project Rename Script (프로젝트명 변경 스크립트)" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Cyan

# 변경 설정
$oldName = "restaurant"
$newName = "your_program"
$oldNameUpper = "Restaurant"
$newNameUpper = "Your_Program"

Write-Host "`n📝 Rename Configuration:" -ForegroundColor Yellow
Write-Host "   Old Name: $oldName" -ForegroundColor White
Write-Host "   New Name: $newName" -ForegroundColor White
Write-Host "   Old Name (Upper): $oldNameUpper" -ForegroundColor White
Write-Host "   New Name (Upper): $newNameUpper" -ForegroundColor White

# 백업 생성
Write-Host "`n💾 Creating backup before rename..." -ForegroundColor Yellow
$backupDir = "backup_before_rename_$(Get-Date -Format 'yyyy-MM-dd_HH-mm-ss')"
if (Test-Path $backupDir) {
    Remove-Item $backupDir -Recurse -Force
}
New-Item -ItemType Directory -Path $backupDir | Out-Null

# 중요 파일들 백업
$importantFiles = @(
    "app.py", "models.py", "requirements.txt", "config.py",
    "package.json", "next.config.js", "tailwind.config.js"
)

foreach ($file in $importantFiles) {
    if (Test-Path $file) {
        Copy-Item $file -Destination $backupDir -Force
        Write-Host "   Backed up: $file" -ForegroundColor White
    }
}

Write-Host "✅ Backup created: $backupDir" -ForegroundColor Green

# 파일 내용 변경 함수
function Update-FileContent {
    param(
        [string]$FilePath,
        [string]$OldText,
        [string]$NewText
    )
    
    try {
        if (Test-Path $FilePath) {
            $content = Get-Content $FilePath -Raw -Encoding UTF8
            $updatedContent = $content -replace $OldText, $NewText
            
            if ($content -ne $updatedContent) {
                Set-Content -Path $FilePath -Value $updatedContent -Encoding UTF8
                Write-Host "   Updated: $FilePath" -ForegroundColor Green
                return $true
            }
        }
        return $false
    } catch {
        Write-Host "   Error updating $FilePath : $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

# 파일명 변경 함수
function Rename-ProjectFile {
    param(
        [string]$FilePath,
        [string]$OldName,
        [string]$NewName
    )
    
    try {
        if (Test-Path $FilePath) {
            $newPath = $FilePath -replace $OldName, $NewName
            if ($FilePath -ne $newPath) {
                Rename-Item -Path $FilePath -NewName $newPath -Force
                Write-Host "   Renamed: $FilePath -> $newPath" -ForegroundColor Green
                return $true
            }
        }
        return $false
    } catch {
        Write-Host "   Error renaming $FilePath : $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

Write-Host "`n🔄 Starting project rename process..." -ForegroundColor Yellow

$updateCount = 0
$renameCount = 0

# 1. 파일 내용 변경
Write-Host "`n📝 Updating file contents..." -ForegroundColor Yellow

$filePatterns = @(
    "*.py", "*.js", "*.ts", "*.tsx", "*.jsx", "*.json", "*.yml", "*.yaml",
    "*.md", "*.txt", "*.bat", "*.ps1", "*.sh", "*.html", "*.css", "*.scss",
    "*.ini", "*.cfg", "*.conf", "Dockerfile*", "docker-compose*.yml"
)

foreach ($pattern in $filePatterns) {
    $files = Get-ChildItem -Path . -Filter $pattern -Recurse -File -ErrorAction SilentlyContinue
    foreach ($file in $files) {
        # restaurant -> your_program
        if (Update-FileContent -FilePath $file.FullName -OldText $oldName -NewText $newName) {
            $updateCount++
        }
        
        # Restaurant -> Your_Program
        if (Update-FileContent -FilePath $file.FullName -OldText $oldNameUpper -NewText $newNameUpper) {
            $updateCount++
        }
        
        # RESTAURANT -> YOUR_PROGRAM
        if (Update-FileContent -FilePath $file.FullName -OldText $oldName.ToUpper() -NewText $newName.ToUpper()) {
            $updateCount++
        }
    }
}

# 2. 디렉토리명 변경
Write-Host "`n📁 Renaming directories..." -ForegroundColor Yellow

$directories = Get-ChildItem -Path . -Directory -Recurse -ErrorAction SilentlyContinue | 
    Where-Object { $_.Name -like "*$oldName*" } | 
    Sort-Object FullName -Descending

foreach ($dir in $directories) {
    if (Rename-ProjectFile -FilePath $dir.FullName -OldName $oldName -NewName $newName) {
        $renameCount++
    }
}

# 3. 파일명 변경
Write-Host "`n📄 Renaming files..." -ForegroundColor Yellow

$files = Get-ChildItem -Path . -File -Recurse -ErrorAction SilentlyContinue | 
    Where-Object { $_.Name -like "*$oldName*" }

foreach ($file in $files) {
    if (Rename-ProjectFile -FilePath $file.FullName -OldName $oldName -NewName $newName) {
        $renameCount++
    }
}

# 4. 특별한 파일들 처리
Write-Host "`n🔧 Processing special files..." -ForegroundColor Yellow

# package.json 파일들
$packageFiles = Get-ChildItem -Path . -Filter "package.json" -Recurse -File
foreach ($file in $packageFiles) {
    try {
        $packageJson = Get-Content $file.FullName -Raw | ConvertFrom-Json
        if ($packageJson.name -like "*$oldName*") {
            $packageJson.name = $packageJson.name -replace $oldName, $newName
            $packageJson | ConvertTo-Json -Depth 10 | Set-Content $file.FullName -Encoding UTF8
            Write-Host "   Updated package.json: $($file.FullName)" -ForegroundColor Green
            $updateCount++
        }
    } catch {
        Write-Host "   Error updating package.json $($file.FullName) : $($_.Exception.Message)" -ForegroundColor Red
    }
}

# README 파일들
$readmeFiles = Get-ChildItem -Path . -Filter "README*.md" -Recurse -File
foreach ($file in $readmeFiles) {
    if (Update-FileContent -FilePath $file.FullName -OldText $oldName -NewText $newName) {
        $updateCount++
    }
}

# 완료 요약
Write-Host "`n📋 Rename Summary:" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "Files Updated: $updateCount" -ForegroundColor White
Write-Host "Items Renamed: $renameCount" -ForegroundColor White
Write-Host "Backup Location: $backupDir" -ForegroundColor White

Write-Host "`n✅ Project rename completed successfully!" -ForegroundColor Green
Write-Host "🔄 Please restart your development environment" -ForegroundColor Yellow
Write-Host "📝 Update any external references to the old project name" -ForegroundColor Yellow

Write-Host "`nProject rename completed at: $(Get-Date)" -ForegroundColor Cyan 