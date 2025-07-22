# L3ARN-Labs Frontend Deployment Script v2.0
# Enhanced frontend deployment automation with PWA support

param(
    [string]$Environment = "development",
    [string]$Region = "eastus",
    [string]$ResourceGroup = "l3arn-rg",
    [string]$BuildMode = "production",
    [switch]$SkipBuild = $false,
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

Write-Log "Starting L3ARN-Labs Frontend Deployment v2.0" "INFO"
Write-Log "Environment: $Environment" "INFO"
Write-Log "Build Mode: $BuildMode" "INFO"

try {
    # Check prerequisites
    Write-Log "Checking prerequisites..." "INFO"
    
    # Check Node.js
    try {
        $nodeVersion = node --version
        Write-Log "Node.js found: $nodeVersion" "INFO"
    } catch {
        Write-Log "Node.js not found. Please install Node.js." "ERROR"
        exit 1
    }
    
    # Check npm
    try {
        $npmVersion = npm --version
        Write-Log "npm found: $npmVersion" "INFO"
    } catch {
        Write-Log "npm not found. Please install npm." "ERROR"
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
    
    # Navigate to frontend directory
    Set-Location "frontend"
    Write-Log "Frontend directory: $(Get-Location)" "INFO"
    
    # Install dependencies
    Write-Log "Installing frontend dependencies..." "INFO"
    npm install
    if ($LASTEXITCODE -ne 0) {
        Write-Log "npm install failed" "ERROR"
        exit 1
    }
    Write-Log "Dependencies installed successfully" "INFO"
    
    # Create PWA service worker
    Write-Log "Creating PWA service worker..." "INFO"
    $serviceWorkerContent = @"
// L3ARN-Labs PWA Service Worker v2.0
const CACHE_NAME = 'l3arn-cache-v2.0';
const urlsToCache = [
  '/',
  '/courses',
  '/lessons',
  '/dashboard',
  '/profile',
  '/quiz',
  '/static/js/bundle.js',
  '/static/css/main.css',
  '/manifest.json',
  '/favicon.ico'
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        console.log('Opened cache');
        return cache.addAll(urlsToCache);
      })
  );
});

self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request)
      .then(response => {
        if (response) {
          return response;
        }
        return fetch(event.request);
      }
    )
  );
});

self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => {
          if (cacheName !== CACHE_NAME) {
            console.log('Deleting old cache:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
});
"@
    
    $serviceWorkerContent | Out-File -FilePath "public/sw.js" -Encoding UTF8
    Write-Log "Service worker created: public/sw.js" "INFO"
    
    # Create PWA manifest
    Write-Log "Creating PWA manifest..." "INFO"
    $manifestContent = @"
{
  "name": "L3ARN-Labs AI School Platform",
  "short_name": "L3ARN-Labs",
  "description": "Enhanced AI School Platform with multimodal learning and real-time collaboration",
  "start_url": "/",
  "display": "standalone",
  "background_color": "#ffffff",
  "theme_color": "#3b82f6",
  "icons": [
    {
      "src": "/favicon.ico",
      "sizes": "64x64",
      "type": "image/x-icon"
    },
    {
      "src": "/icon-192.png",
      "sizes": "192x192",
      "type": "image/png"
    },
    {
      "src": "/icon-512.png",
      "sizes": "512x512",
      "type": "image/png"
    }
  ],
  "categories": ["education", "productivity"],
  "lang": "en",
  "dir": "ltr"
}
"@
    
    $manifestContent | Out-File -FilePath "public/manifest.json" -Encoding UTF8
    Write-Log "PWA manifest created: public/manifest.json" "INFO"
    
    # Build frontend
    if (-not $SkipBuild) {
        Write-Log "Building frontend application..." "INFO"
        
        $buildCommand = switch ($BuildMode) {
            "development" { "npm run dev" }
            "production" { "npm run build" }
            default { "npm run build" }
        }
        
        Write-Log "Executing: $buildCommand" "INFO"
        Invoke-Expression $buildCommand
        
        if ($LASTEXITCODE -ne 0) {
            Write-Log "Frontend build failed" "ERROR"
            exit 1
        }
        Write-Log "Frontend build completed successfully" "INFO"
    }
    
    # Deploy based on environment
    switch ($Environment) {
        "development" {
            Write-Log "Starting development server..." "INFO"
            Start-Process -FilePath "npm" -ArgumentList "run", "dev" -NoNewWindow
            Write-Log "Development server started at http://localhost:3000" "INFO"
        }
        "staging" {
            Write-Log "Deploying to staging environment..." "INFO"
            # Staging deployment logic
            docker run -d --name l3arn-frontend-staging -p 3000:3000 -v "$(Get-Location)/out:/usr/share/nginx/html" nginx:alpine
        }
        "production" {
            Write-Log "Deploying to production environment..." "INFO"
            
            # Azure Static Web Apps deployment
            $staticWebAppName = "l3arn-frontend-prod"
            
            # Check if resource group exists
            $rgExists = az group exists --name $ResourceGroup
            if ($rgExists -eq "false") {
                Write-Log "Creating resource group: $ResourceGroup" "INFO"
                az group create --name $ResourceGroup --location $Region
            }
            
            # Deploy to Azure Static Web Apps
            az staticwebapp create `
                --name $staticWebAppName `
                --resource-group $ResourceGroup `
                --source . `
                --location $Region `
                --branch main `
                --app-location "/" `
                --output-location "out"
            
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
        "development" { "http://localhost:3000" }
        "staging" { "http://localhost:3000" }
        "production" { "https://$staticWebAppName.$Region.azurestaticapps.net" }
    }
    
    try {
        $response = Invoke-WebRequest -Uri $healthUrl -Method GET -TimeoutSec 30
        if ($response.StatusCode -eq 200) {
            Write-Log "Health check passed" "INFO"
        } else {
            Write-Log "Health check failed: Status $($response.StatusCode)" "ERROR"
            exit 1
        }
    } catch {
        Write-Log "Health check failed: $($_.Exception.Message)" "ERROR"
        exit 1
    }
    
    # Performance test
    Write-Log "Running performance test..." "INFO"
    $stopwatch = [System.Diagnostics.Stopwatch]::StartNew()
    $response = Invoke-WebRequest -Uri $healthUrl -Method GET
    $stopwatch.Stop()
    
    Write-Log "Response time: $($stopwatch.ElapsedMilliseconds)ms" "INFO"
    
    if ($stopwatch.ElapsedMilliseconds -gt 3000) {
        Write-Log "Warning: Response time is slow" "WARN"
    }
    
    # PWA validation
    Write-Log "Validating PWA features..." "INFO"
    
    # Check if service worker is accessible
    $swUrl = switch ($Environment) {
        "development" { "http://localhost:3000/sw.js" }
        "staging" { "http://localhost:3000/sw.js" }
        "production" { "https://$staticWebAppName.$Region.azurestaticapps.net/sw.js" }
    }
    
    try {
        $swResponse = Invoke-WebRequest -Uri $swUrl -Method GET -TimeoutSec 10
        if ($swResponse.StatusCode -eq 200) {
            Write-Log "Service worker is accessible" "INFO"
        } else {
            Write-Log "Service worker not accessible" "WARN"
        }
    } catch {
        Write-Log "Service worker validation failed: $($_.Exception.Message)" "WARN"
    }
    
    # Check if manifest is accessible
    $manifestUrl = switch ($Environment) {
        "development" { "http://localhost:3000/manifest.json" }
        "staging" { "http://localhost:3000/manifest.json" }
        "production" { "https://$staticWebAppName.$Region.azurestaticapps.net/manifest.json" }
    }
    
    try {
        $manifestResponse = Invoke-WebRequest -Uri $manifestUrl -Method GET -TimeoutSec 10
        if ($manifestResponse.StatusCode -eq 200) {
            Write-Log "PWA manifest is accessible" "INFO"
        } else {
            Write-Log "PWA manifest not accessible" "WARN"
        }
    } catch {
        Write-Log "PWA manifest validation failed: $($_.Exception.Message)" "WARN"
    }
    
    Write-Log "Frontend deployment completed successfully!" "INFO"
    
    # Generate deployment report
    $report = @{
        timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        environment = $Environment
        region = $Region
        buildMode = $BuildMode
        responseTime = $stopwatch.ElapsedMilliseconds
        status = "success"
        pwaFeatures = @{
            serviceWorker = $swResponse.StatusCode -eq 200
            manifest = $manifestResponse.StatusCode -eq 200
        }
    }
    
    $reportPath = "deployment-report-frontend-$Environment-$(Get-Date -Format 'yyyyMMdd-HHmmss').json"
    $report | ConvertTo-Json -Depth 3 | Out-File -FilePath $reportPath
    Write-Log "Deployment report saved: $reportPath" "INFO"
    
} catch {
    Write-Log "Deployment failed: $($_.Exception.Message)" "ERROR"
    Write-Log "Stack trace: $($_.ScriptStackTrace)" "ERROR"
    exit 1
} finally {
    Write-Log "Frontend deployment script completed" "INFO"
} 