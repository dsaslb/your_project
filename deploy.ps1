# Your Program Production Deployment Script
# PowerShell Script

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet("dev", "staging", "production")]
    [string]$Environment = "production",
    
    [Parameter(Mandatory=$false)]
    [switch]$Build = $false,
    
    [Parameter(Mandatory=$false)]
    [switch]$Migrate = $false,
    
    [Parameter(Mandatory=$false)]
    [switch]$Backup = $false
)

Write-Host "Your Program Deployment Starting - Environment: $Environment" -ForegroundColor Green

# Environment-specific configuration files
$ComposeFile = switch ($Environment) {
    "dev" { "docker-compose.yml" }
    "staging" { "docker-compose.prod.yml" }
    "production" { "docker-compose.production.yml" }
}

Write-Host "Using Docker Compose file: $ComposeFile" -ForegroundColor Cyan

# Check environment variables file
$EnvFile = "config/$Environment.env"
if (!(Test-Path $EnvFile)) {
    Write-Host "Environment file not found: $EnvFile" -ForegroundColor Yellow
    Write-Host "Please create it using config/production.env.template as reference." -ForegroundColor Yellow
    exit 1
}

# Backup database (for production environment)
if ($Backup -and $Environment -eq "production") {
    Write-Host "Creating database backup..." -ForegroundColor Yellow
    docker-compose -f $ComposeFile exec postgres pg_dump -U your_user your_program_prod > "backups/backup_$(Get-Date -Format 'yyyyMMdd_HHmmss').sql"
    Write-Host "Backup completed" -ForegroundColor Green
}

# Build Docker images (if needed)
if ($Build) {
    Write-Host "Building Docker images..." -ForegroundColor Yellow
    docker-compose -f $ComposeFile build --no-cache
    Write-Host "Build completed" -ForegroundColor Green
}

# Stop existing services
Write-Host "Stopping existing services..." -ForegroundColor Yellow
docker-compose -f $ComposeFile down

# Start services
Write-Host "Starting services..." -ForegroundColor Yellow
docker-compose -f $ComposeFile up -d

# Database migration (if needed)
if ($Migrate) {
    Write-Host "Running database migration..." -ForegroundColor Yellow
    Start-Sleep 10  # Wait for database startup
    docker-compose -f $ComposeFile exec backend python -c "from app import db; db.create_all()"
    Write-Host "Migration completed" -ForegroundColor Green
}

# Check service status
Write-Host "Checking service status..." -ForegroundColor Yellow
Start-Sleep 15  # Wait for service startup

# Health checks
$Services = @("nginx", "backend", "postgres", "redis")
foreach ($Service in $Services) {
    $Status = docker-compose -f $ComposeFile ps $Service
    if ($Status -match "Up") {
        Write-Host "${Service}: Running normally" -ForegroundColor Green
    } else {
        Write-Host "${Service}: Issue detected" -ForegroundColor Red
    }
}

# Application health check
Write-Host "Application health check..." -ForegroundColor Yellow
try {
    $Response = Invoke-WebRequest -Uri "http://localhost/health" -Method GET -TimeoutSec 10
    if ($Response.StatusCode -eq 200) {
        Write-Host "Application health check successful" -ForegroundColor Green
    }
} catch {
    Write-Host "Application health check failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "Deployment completed!" -ForegroundColor Green
Write-Host "Monitoring dashboards:" -ForegroundColor Cyan
Write-Host "   - Application: http://localhost" -ForegroundColor White
Write-Host "   - Grafana: http://localhost:3001" -ForegroundColor White
Write-Host "   - Prometheus: http://localhost:9090" -ForegroundColor White

if ($Environment -eq "production") {
    Write-Host "Production environment checklist:" -ForegroundColor Yellow
    Write-Host "   [] SSL certificate setup" -ForegroundColor White
    Write-Host "   [] Firewall rules configuration" -ForegroundColor White
    Write-Host "   [] Backup schedule setup" -ForegroundColor White
    Write-Host "   [] Monitoring alerts setup" -ForegroundColor White
}