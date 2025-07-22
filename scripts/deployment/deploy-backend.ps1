# L3ARN-Labs Backend Deployment Script v2.0
# Enhanced deployment automation with PowerShell

param(
    [string]$Environment = "development",
    [string]$Region = "eastus",
    [string]$ResourceGroup = "l3arn-rg",
    [string]$ImageTag = "v2.0",
    [switch]$SkipTests = $false,
    [switch]$Force = $false
)

# Error handling setup
$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

# Logging function
function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Write-Host "[$timestamp] [$Level] $Message"
}

# Validate environment
$validEnvironments = @("development", "staging", "production")
if ($Environment -notin $validEnvironments) {
    Write-Log "Invalid environment: $Environment. Valid options: $($validEnvironments -join ', ')" "ERROR"
    exit 1
}

Write-Log "Starting L3ARN-Labs Backend Deployment v2.0" "INFO"
Write-Log "Environment: $Environment" "INFO"
Write-Log "Region: $Region" "INFO"

try {
    # Check prerequisites
    Write-Log "Checking prerequisites..." "INFO"
    
    # Check Docker
    try {
        $dockerVersion = docker --version
        Write-Log "Docker found: $dockerVersion" "INFO"
    } catch {
        Write-Log "Docker not found. Please install Docker Desktop." "ERROR"
        exit 1
    }
    
    # Check Azure CLI if production
    if ($Environment -eq "production") {
        try {
            $azVersion = az version --output json | ConvertFrom-Json
            Write-Log "Azure CLI found: $($azVersion.'azure-cli')" "INFO"
        } catch {
            Write-Log "Azure CLI not found. Please install Azure CLI for production deployment." "ERROR"
            exit 1
        }
    }
    
    # Navigate to project root
    $projectRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
    Set-Location $projectRoot
    Write-Log "Project root: $projectRoot" "INFO"
    
    # Build Docker image
    Write-Log "Building Docker image..." "INFO"
    $imageName = "l3arn-backend:$ImageTag"
    
    docker build -t $imageName ./backend
    if ($LASTEXITCODE -ne 0) {
        Write-Log "Docker build failed" "ERROR"
        exit 1
    }
    Write-Log "Docker image built successfully: $imageName" "INFO"
    
    # Run tests if not skipped
    if (-not $SkipTests) {
        Write-Log "Running backend tests..." "INFO"
        docker run --rm $imageName python -m pytest tests/ -v
        if ($LASTEXITCODE -ne 0) {
            Write-Log "Tests failed. Deployment aborted." "ERROR"
            exit 1
        }
        Write-Log "All tests passed" "INFO"
    }
    
    # Deploy based on environment
    switch ($Environment) {
        "development" {
            Write-Log "Starting development environment..." "INFO"
            docker-compose -f docker-compose.yml up -d backend
            if ($LASTEXITCODE -ne 0) {
                Write-Log "Development deployment failed" "ERROR"
                exit 1
            }
        }
        "staging" {
            Write-Log "Deploying to staging environment..." "INFO"
            # Staging deployment logic
            docker run -d --name l3arn-backend-staging -p 8000:8000 $imageName
        }
        "production" {
            Write-Log "Deploying to production environment..." "INFO"
            
            # Azure Container Apps deployment
            $containerAppName = "l3arn-backend-prod"
            
            # Check if resource group exists
            $rgExists = az group exists --name $ResourceGroup
            if ($rgExists -eq "false") {
                Write-Log "Creating resource group: $ResourceGroup" "INFO"
                az group create --name $ResourceGroup --location $Region
            }
            
            # Deploy to Azure Container Apps
            az containerapp create `
                --name $containerAppName `
                --resource-group $ResourceGroup `
                --image $imageName `
                --target-port 8000 `
                --ingress external `
                --min-replicas 2 `
                --max-replicas 10 `
                --cpu 1 `
                --memory 2Gi
            
            if ($LASTEXITCODE -ne 0) {
                Write-Log "Production deployment failed" "ERROR"
                exit 1
            }
            
            Write-Log "Production deployment completed successfully" "INFO"
        }
    }
    
    # Health check
    Write-Log "Performing health check..." "INFO"
    Start-Sleep -Seconds 10  # Wait for services to start
    
    $healthUrl = switch ($Environment) {
        "development" { "http://localhost:8000/health" }
        "staging" { "http://localhost:8000/health" }
        "production" { "https://$containerAppName.$Region.azurecontainerapps.io/health" }
    }
    
    try {
        $response = Invoke-RestMethod -Uri $healthUrl -Method GET -TimeoutSec 30
        if ($response.status -eq "healthy") {
            Write-Log "Health check passed" "INFO"
        } else {
            Write-Log "Health check failed: $($response.status)" "ERROR"
            exit 1
        }
    } catch {
        Write-Log "Health check failed: $($_.Exception.Message)" "ERROR"
        exit 1
    }
    
    # Performance test
    Write-Log "Running performance test..." "INFO"
    $testUrl = switch ($Environment) {
        "development" { "http://localhost:8000/api/v1/health" }
        "staging" { "http://localhost:8000/api/v1/health" }
        "production" { "https://$containerAppName.$Region.azurecontainerapps.io/api/v1/health" }
    }
    
    $stopwatch = [System.Diagnostics.Stopwatch]::StartNew()
    $response = Invoke-RestMethod -Uri $testUrl -Method GET
    $stopwatch.Stop()
    
    Write-Log "Response time: $($stopwatch.ElapsedMilliseconds)ms" "INFO"
    
    if ($stopwatch.ElapsedMilliseconds -gt 5000) {
        Write-Log "Warning: Response time is slow" "WARN"
    }
    
    Write-Log "Backend deployment completed successfully!" "INFO"
    
    # Generate deployment report
    $report = @{
        timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        environment = $Environment
        region = $Region
        imageTag = $ImageTag
        responseTime = $stopwatch.ElapsedMilliseconds
        status = "success"
    }
    
    $reportPath = "deployment-report-$Environment-$(Get-Date -Format 'yyyyMMdd-HHmmss').json"
    $report | ConvertTo-Json | Out-File -FilePath $reportPath
    Write-Log "Deployment report saved: $reportPath" "INFO"
    
} catch {
    Write-Log "Deployment failed: $($_.Exception.Message)" "ERROR"
    Write-Log "Stack trace: $($_.ScriptStackTrace)" "ERROR"
    exit 1
} finally {
    Write-Log "Deployment script completed" "INFO"
} 