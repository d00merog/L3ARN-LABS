# setup-environment.ps1
# L3ARN-Labs Environment Setup Script v2.0
# Enhanced AI School Platform

param(
    [string]$Environment = "development",
    [switch]$SkipPrerequisites = $false,
    [switch]$InstallDependencies = $true,
    [switch]$ConfigureServices = $true
)

# Set error action preference
$ErrorActionPreference = "Stop"

# Script configuration
$ScriptVersion = "2.0"
$ProjectRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)

Write-Host "=== L3ARN-Labs Environment Setup v$ScriptVersion ===" -ForegroundColor Cyan
Write-Host "Environment: $Environment" -ForegroundColor Yellow
Write-Host "Project Root: $ProjectRoot" -ForegroundColor Yellow

# Function to check and install prerequisites
function Test-AndInstall-Prerequisites {
    if ($SkipPrerequisites) {
        Write-Host "Skipping prerequisite checks as requested" -ForegroundColor Yellow
        return
    }
    
    Write-Host "Checking and installing prerequisites..." -ForegroundColor Green
    
    # Check Python
    try {
        $pythonVersion = python --version
        Write-Host "✓ Python found: $pythonVersion" -ForegroundColor Green
    } catch {
        Write-Host "Installing Python..." -ForegroundColor Yellow
        winget install Python.Python.3.11
        Refresh-Environment
    }
    
    # Check Node.js
    try {
        $nodeVersion = node --version
        Write-Host "✓ Node.js found: $nodeVersion" -ForegroundColor Green
    } catch {
        Write-Host "Installing Node.js..." -ForegroundColor Yellow
        winget install OpenJS.NodeJS
        Refresh-Environment
    }
    
    # Check Docker
    try {
        $dockerVersion = docker --version
        Write-Host "✓ Docker found: $dockerVersion" -ForegroundColor Green
    } catch {
        Write-Host "Installing Docker Desktop..." -ForegroundColor Yellow
        winget install Docker.DockerDesktop
        Write-Host "Please start Docker Desktop manually after installation" -ForegroundColor Yellow
    }
    
    # Check Git
    try {
        $gitVersion = git --version
        Write-Host "✓ Git found: $gitVersion" -ForegroundColor Green
    } catch {
        Write-Host "Installing Git..." -ForegroundColor Yellow
        winget install Git.Git
        Refresh-Environment
    }
}

# Function to install dependencies
function Install-ProjectDependencies {
    if (-not $InstallDependencies) {
        Write-Host "Skipping dependency installation as requested" -ForegroundColor Yellow
        return
    }
    
    Write-Host "Installing project dependencies..." -ForegroundColor Green
    
    try {
        # Install Python dependencies
        Write-Host "Installing Python dependencies..." -ForegroundColor Yellow
        Push-Location $ProjectRoot
        pip install -r requirements.txt
        
        # Install Node.js dependencies
        Write-Host "Installing Node.js dependencies..." -ForegroundColor Yellow
        Push-Location "frontend"
        npm install
        Pop-Location
        
        Write-Host "✓ All dependencies installed successfully" -ForegroundColor Green
    } catch {
        Write-Error "Failed to install dependencies: $($_.Exception.Message)"
        exit 1
    } finally {
        Pop-Location
    }
}

# Function to configure services
function Configure-Services {
    if (-not $ConfigureServices) {
        Write-Host "Skipping service configuration as requested" -ForegroundColor Yellow
        return
    }
    
    Write-Host "Configuring services..." -ForegroundColor Green
    
    try {
        # Create environment file if it doesn't exist
        $envFile = Join-Path $ProjectRoot ".env"
        if (-not (Test-Path $envFile)) {
            Write-Host "Creating .env file..." -ForegroundColor Yellow
            $envContent = @"
# L3ARN-Labs Environment Configuration v2.0
ENVIRONMENT=$Environment

# Database Configuration
DATABASE_URL=sqlite:///./l3arn_labs.db

# AI Model Configuration
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
HUGGINGFACE_API_KEY=your_huggingface_api_key_here

# Web3 Configuration
WEB3_PROVIDER_URL=your_web3_provider_url_here
CONTRACT_ADDRESS=your_contract_address_here

# Redis Configuration
REDIS_URL=redis://localhost:6379

# Email Configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password

# File Storage
STORAGE_PATH=./uploads
MAX_FILE_SIZE=10485760

# Security
SECRET_KEY=your_secret_key_here
JWT_SECRET=your_jwt_secret_here

# PWA Configuration
PWA_ENABLED=true
PWA_NAME=L3ARN-Labs
PWA_SHORT_NAME=L3ARN-Labs
PWA_DESCRIPTION=Enhanced AI School Platform

# Analytics
ANALYTICS_ENABLED=true
ANALYTICS_PROVIDER=mixpanel

# Multimodal Features
SPEECH_RECOGNITION_ENABLED=true
COMPUTER_VISION_ENABLED=true
GESTURE_RECOGNITION_ENABLED=true

# Collaboration Features
WEBRTC_ENABLED=true
WHITEBOARD_ENABLED=true
PEER_TUTORING_ENABLED=true

# Gamification Features
GAMIFICATION_ENABLED=true
ACHIEVEMENTS_ENABLED=true
LEADERBOARDS_ENABLED=true
"@
            Set-Content -Path $envFile -Value $envContent -Encoding UTF8
            Write-Host "✓ .env file created" -ForegroundColor Green
        }
        
        # Create logs directory
        $logsDir = Join-Path $ProjectRoot "logs"
        if (-not (Test-Path $logsDir)) {
            New-Item -ItemType Directory -Path $logsDir -Force | Out-Null
            Write-Host "✓ Logs directory created" -ForegroundColor Green
        }
        
        # Create uploads directory
        $uploadsDir = Join-Path $ProjectRoot "uploads"
        if (-not (Test-Path $uploadsDir)) {
            New-Item -ItemType Directory -Path $uploadsDir -Force | Out-Null
            Write-Host "✓ Uploads directory created" -ForegroundColor Green
        }
        
        # Create static directory for PWA
        $staticDir = Join-Path $ProjectRoot "backend/static"
        if (-not (Test-Path $staticDir)) {
            New-Item -ItemType Directory -Path $staticDir -Force | Out-Null
            Write-Host "✓ Static directory created" -ForegroundColor Green
        }
        
    } catch {
        Write-Error "Failed to configure services: $($_.Exception.Message)"
        exit 1
    }
}

# Function to setup database
function Setup-Database {
    Write-Host "Setting up database..." -ForegroundColor Green
    
    try {
        Push-Location $ProjectRoot
        
        # Run database migrations
        Write-Host "Running database migrations..." -ForegroundColor Yellow
        alembic upgrade head
        
        Write-Host "✓ Database setup completed" -ForegroundColor Green
    } catch {
        Write-Error "Failed to setup database: $($_.Exception.Message)"
        exit 1
    } finally {
        Pop-Location
    }
}

# Function to validate setup
function Test-Setup {
    Write-Host "Validating setup..." -ForegroundColor Green
    
    try {
        # Test Python
        $pythonTest = python -c "import fastapi, uvicorn, sqlalchemy; print('Python dependencies OK')"
        Write-Host "✓ Python dependencies validated" -ForegroundColor Green
        
        # Test Node.js
        $nodeTest = node -e "console.log('Node.js OK')"
        Write-Host "✓ Node.js validated" -ForegroundColor Green
        
        # Test Docker
        $dockerTest = docker --version
        Write-Host "✓ Docker validated" -ForegroundColor Green
        
        Write-Host "✓ All components validated successfully" -ForegroundColor Green
        
    } catch {
        Write-Error "Setup validation failed: $($_.Exception.Message)"
        exit 1
    }
}

# Function to display next steps
function Show-NextSteps {
    Write-Host "`n=== Setup Complete ===" -ForegroundColor Green
    Write-Host "Next steps:" -ForegroundColor Cyan
    Write-Host "1. Update .env file with your API keys" -ForegroundColor White
    Write-Host "2. Start the backend: .\scripts\deployment\deploy-backend.ps1" -ForegroundColor White
    Write-Host "3. Start the frontend: .\scripts\deployment\deploy-frontend.ps1" -ForegroundColor White
    Write-Host "4. Access the platform at: http://localhost:3000" -ForegroundColor White
    Write-Host "5. API documentation at: http://localhost:8000/docs" -ForegroundColor White
    Write-Host "`nFor monitoring: .\scripts\monitoring\monitor-services.ps1" -ForegroundColor Yellow
}

# Main setup logic
try {
    # Check prerequisites
    Test-AndInstall-Prerequisites
    
    # Install dependencies
    Install-ProjectDependencies
    
    # Configure services
    Configure-Services
    
    # Setup database
    Setup-Database
    
    # Validate setup
    Test-Setup
    
    # Show next steps
    Show-NextSteps
    
} catch {
    Write-Error "Environment setup failed: $($_.Exception.Message)"
    exit 1
} 