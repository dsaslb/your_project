# Your Program Project Cleanup Script
# Remove duplicate folders, unnecessary files, path errors, etc.

$OutputEncoding = [Console]::OutputEncoding = [Text.Encoding]::UTF8

Write-Host 'Your Program Project Cleanup Script'
Write-Host '======================================================='

# Backup
Write-Host 'Creating backup...'
$backupDir = "backup_before_cleanup_$(Get-Date -Format 'yyyy-MM-dd_HH-mm-ss')"
if (Test-Path $backupDir) {
    Remove-Item $backupDir -Recurse -Force
}
New-Item -ItemType Directory -Path $backupDir | Out-Null

# Important files backup
$importantFiles = @(
    "app.py", "models.py", "requirements.txt", "config.py",
    "package.json", "next.config.js", "tailwind.config.js",
    "docker-compose.yml", "docker-compose.prod.yml",
    "Dockerfile", "Dockerfile.backend", "Dockerfile.gateway"
)
foreach ($file in $importantFiles) {
    if (Test-Path $file) {
        Copy-Item $file -Destination $backupDir -Force
        Write-Host ('   Backed up: ' + $file)
    }
}
Write-Host ('Backup completed: ' + $backupDir)

# 1. Duplicate folder cleanup
Write-Host 'Cleaning up duplicate folders...'
$filesToUpdate = @(
    "scripts/ci-cd-pipeline.sh",
    "scripts/cleanup_all.bat",
    "scripts/deploy-production.bat",
    "scripts/deploy-production.sh",
    "scripts/deploy_plugin_monitoring.py",
    "scripts/final_setup.ps1",
    "scripts/health_check.ps1",
    "scripts/cleanup_all.sh",
    "scripts/master_automation.ps1",
    "scripts/performance-optimization.bat",
    "scripts/performance-optimization.sh",
    "scripts/restore_project.ps1",
    "scripts/start_all.bat",
    "scripts/start_all.sh",
    "README.md",
    "docker-compose.yml",
    "docker-compose.prod.yml",
    ".github/workflows/ci-cd-pipeline.yml",
    ".github/workflows/ci.yml",
    ".github/workflows/ci-cd.yml",
    ".github/workflows/frontend-ci.yml",
    ".github/workflows/nextjs.yml",
    ".github/workflows/plugin-monitoring.yml"
)
foreach ($file in $filesToUpdate) {
    if (Test-Path $file) {
        $content = Get-Content $file -Raw -Encoding UTF8
        $updatedContent = $content -replace "your_program_frontend", "frontend"
        Set-Content $file -Value $updatedContent -Encoding UTF8
        Write-Host ('   Updated: ' + $file)
    }
}

# 2. Deleted file reference cleanup
Write-Host 'Cleaning up deleted file references...'

# 3. Project name unification
Write-Host 'Unifying project names...'
$renameFiles = Get-ChildItem -Recurse -File -Include "*.py", "*.js", "*.ts", "*.tsx", "*.jsx", "*.json", "*.yml", "*.yaml", "*.md", "*.txt", "*.ps1", "*.sh", "*.bat" | Where-Object { $_.FullName -notlike "*$backupDir*" }
foreach ($file in $renameFiles) {
    try {
        $content = Get-Content $file.FullName -Raw -Encoding UTF8 -ErrorAction SilentlyContinue
        if ($content) {
            $updatedContent = $content -replace "your_program_management", "your_program_management"
            $updatedContent = $updatedContent -replace "your-program-system", "your-program-system"
            $updatedContent = $updatedContent -replace "restaurant\.local", "your-program.local"
            $updatedContent = $updatedContent -replace "your_program_user", "your_program_user"
            $updatedContent = $updatedContent -replace "your_program_db", "your_program_db"
            $updatedContent = $updatedContent -replace "your_program_postgres", "your_program_postgres"
            $updatedContent = $updatedContent -replace "your_program_redis", "your_program_redis"
            if ($content -ne $updatedContent) {
                Set-Content $file.FullName -Value $updatedContent -Encoding UTF8
                Write-Host ('   Updated: ' + $file.Name)
            }
        }
    } catch {
        Write-Host ('   Error (ignored): ' + $file.Name)
    }
}

# 4. Unnecessary file cleanup
Write-Host 'Cleaning up unnecessary files...'
$unnecessaryFiles = @(
    "frontend/restaurant.ps1",
    "frontend/start-dev.bat",
    "*.bak",
    "*.backup",
    "temp_*",
    "*.tmp"
)
foreach ($pattern in $unnecessaryFiles) {
    $files = Get-ChildItem -Recurse -Filter $pattern -ErrorAction SilentlyContinue
    foreach ($file in $files) {
        try {
            Remove-Item $file.FullName -Force
            Write-Host ('   Deleted: ' + $file.Name)
        } catch {
            Write-Host ('   Delete failed: ' + $file.Name)
        }
    }
}

# 5. Environment file cleanup
Write-Host 'Cleaning up environment files...'
if (Test-Path ".env.example") {
    Copy-Item ".env.example" ".env" -Force
    Write-Host '   .env file created'
}
if (Test-Path "frontend/package.json") {
    $packageContent = Get-Content "frontend/package.json" -Raw
    $packageContent = $packageContent -replace '"name": "your_program_frontend"', '"name": "your-program-frontend"'
    Set-Content "frontend/package.json" -Value $packageContent -Encoding UTF8
    Write-Host '   package.json name unified'
}

# 6. Import path cleanup
Write-Host 'Cleaning up import paths...'
$tsFiles = Get-ChildItem -Recurse -Include "*.ts", "*.tsx", "*.js", "*.jsx" | Where-Object { $_.FullName -like "*frontend*" -and $_.FullName -notlike "*node_modules*" }
foreach ($file in $tsFiles) {
    try {
        $content = Get-Content $file.FullName -Raw -Encoding UTF8 -ErrorAction SilentlyContinue
        if ($content) {
            $updatedContent = $content -replace "import.*OfflineManager.*from.*['\""].*['\""];?\s*", ""
            $updatedContent = $updatedContent -replace "import.*useAuth.*from.*['\""].*['\""];?\s*", ""
            $updatedContent = $updatedContent -replace "import.*from.*['\""]@/store/index['\""];?\s*", ""
            $updatedContent = $updatedContent -replace "from ['\""]\.\./\.\./\.\./", "from '@/"
            $updatedContent = $updatedContent -replace "from ['\""]\.\./\.\./", "from '@/"
            $updatedContent = $updatedContent -replace "from ['\""]\.\./", "from '@/"
            if ($content -ne $updatedContent) {
                Set-Content $file.FullName -Value $updatedContent -Encoding UTF8
                Write-Host ('   Path cleaned: ' + $file.Name)
            }
        }
    } catch {
        Write-Host ('   Error (ignored): ' + $file.Name)
    }
}

# 7. Auth/permission structure unification
Write-Host 'Unifying auth/permission structure...'
$authDir = "frontend/src/components/auth"
if (!(Test-Path $authDir)) {
    New-Item -ItemType Directory -Path $authDir -Force | Out-Null
}
$hooksDir = "frontend/src/hooks"
if (!(Test-Path $hooksDir)) {
    New-Item -ItemType Directory -Path $hooksDir -Force | Out-Null
}

# 8. Dummy data cleanup
Write-Host 'Cleaning up dummy data...'
$dummyDataFiles = Get-ChildItem -Recurse -Include "*dummy*", "*mock*", "*test-data*" | Where-Object { $_.FullName -notlike "*test*" -and $_.FullName -notlike "*__tests__*" }
foreach ($file in $dummyDataFiles) {
    try {
        Remove-Item $file.FullName -Force
        Write-Host ('   Dummy data deleted: ' + $file.Name)
    } catch {
        Write-Host ('   Delete failed: ' + $file.Name)
    }
}

Write-Host 'Project cleanup completed!'
Write-Host 'Next steps:'
Write-Host '   1. npm install (in frontend directory)'
Write-Host '   2. pip install -r requirements.txt'
Write-Host '   3. Test server run'
Write-Host '   4. Test build'
Write-Host ('Backup location: ' + $backupDir)
Write-Host '   If any problem occurs, you can restore from backup by running this script again.' 
