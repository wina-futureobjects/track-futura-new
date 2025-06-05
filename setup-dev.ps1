# Track-Futura Development Setup Script for Windows PowerShell
# This script sets up the development environment for new team members

# Set error handling
$ErrorActionPreference = "Stop"

Write-Host "🚀 Setting up Track-Futura Development Environment..." -ForegroundColor Green

# Function to print colored output
function Write-Status {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor Blue
}

function Write-Success {
    param([string]$Message)
    Write-Host "[SUCCESS] $Message" -ForegroundColor Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[WARNING] $Message" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

# Check if Docker is installed
try {
    $dockerVersion = docker --version
    Write-Success "Docker is installed: $dockerVersion"
} catch {
    Write-Error "Docker is not installed. Please install Docker Desktop first."
    Write-Host "Download from: https://www.docker.com/products/docker-desktop" -ForegroundColor Cyan
    exit 1
}

# Check if Docker Compose is available
try {
    $composeVersion = docker-compose --version
    Write-Success "Docker Compose is available: $composeVersion"
} catch {
    try {
        $composeVersion = docker compose version
        Write-Success "Docker Compose is available: $composeVersion"
    } catch {
        Write-Error "Docker Compose is not available. Please install Docker Compose."
        exit 1
    }
}

# Check if .env file exists
if (-not (Test-Path ".env")) {
    Write-Status "Creating .env file from template..."
    Copy-Item "env.development.template" ".env"
    Write-Warning "Please review and update the .env file with your specific configuration"
    Write-Warning "Ask your team lead for the BrightData API key"
} else {
    Write-Status ".env file already exists"
}

# Create necessary directories
Write-Status "Creating necessary directories..."
New-Item -ItemType Directory -Force -Path "backend\staticfiles" | Out-Null
New-Item -ItemType Directory -Force -Path "backend\media" | Out-Null
New-Item -ItemType Directory -Force -Path "logs" | Out-Null

# Build development containers
Write-Status "Building Docker containers (this may take a few minutes)..."
try {
    docker-compose -f docker-compose.dev.yml build
} catch {
    try {
        docker compose -f docker-compose.dev.yml build
    } catch {
        Write-Error "Failed to build Docker containers"
        exit 1
    }
}

Write-Success "Docker containers built successfully ✓"

# Start the development environment
Write-Status "Starting development environment..."
try {
    docker-compose -f docker-compose.dev.yml up -d
} catch {
    try {
        docker compose -f docker-compose.dev.yml up -d
    } catch {
        Write-Error "Failed to start development environment"
        exit 1
    }
}

# Wait for services to be ready
Write-Status "Waiting for services to start..."
Start-Sleep -Seconds 10

# Run database migrations
Write-Status "Running database migrations..."
try {
    docker-compose -f docker-compose.dev.yml exec backend python manage.py migrate
} catch {
    try {
        docker compose -f docker-compose.dev.yml exec backend python manage.py migrate
    } catch {
        Write-Warning "Failed to run migrations. You may need to run them manually."
    }
}

# Create superuser (optional)
$response = Read-Host "Would you like to create a Django superuser? (y/n)"
if ($response -match '^([yY][eE][sS]|[yY])$') {
    try {
        docker-compose -f docker-compose.dev.yml exec backend python manage.py createsuperuser
    } catch {
        try {
            docker compose -f docker-compose.dev.yml exec backend python manage.py createsuperuser
        } catch {
            Write-Warning "Failed to create superuser. You can create one later."
        }
    }
}

# Load demo data (optional)
$response = Read-Host "Would you like to load demo data? (y/n)"
if ($response -match '^([yY][eE][sS]|[yY])$') {
    try {
        docker-compose -f docker-compose.dev.yml exec backend python manage.py loaddata demo_data.json
    } catch {
        try {
            docker compose -f docker-compose.dev.yml exec backend python manage.py loaddata demo_data.json
        } catch {
            Write-Warning "Demo data not found, skipping..."
        }
    }
}

Write-Success "🎉 Development environment setup complete!"
Write-Host ""
Write-Host "Access your application at:" -ForegroundColor Cyan
Write-Host "  📱 Frontend: http://localhost:3000" -ForegroundColor White
Write-Host "  🔧 Backend API: http://localhost:8000" -ForegroundColor White
Write-Host "  👨‍💼 Django Admin: http://localhost:8000/admin" -ForegroundColor White
Write-Host ""
Write-Host "Useful commands:" -ForegroundColor Cyan
Write-Host "  📊 View logs: docker-compose -f docker-compose.dev.yml logs -f" -ForegroundColor White
Write-Host "  🛑 Stop services: docker-compose -f docker-compose.dev.yml down" -ForegroundColor White
Write-Host "  🔄 Restart services: docker-compose -f docker-compose.dev.yml restart" -ForegroundColor White
Write-Host "  🧹 Clean up: docker-compose -f docker-compose.dev.yml down -v" -ForegroundColor White
Write-Host ""
Write-Host "For more information, see DEVELOPER_ONBOARDING.md" -ForegroundColor Cyan 