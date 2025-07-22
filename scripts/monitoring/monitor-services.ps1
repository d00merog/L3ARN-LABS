# L3ARN-Labs Service Monitoring Script v2.0
# Enhanced monitoring with comprehensive health checks and reporting

param(
    [string]$Environment = "development",
    [int]$IntervalSeconds = 60,
    [int]$DurationMinutes = 60,
    [switch]$Continuous = $false,
    [switch]$GenerateReport = $true,
    [string]$ReportFormat = "json"  # json, html, both
)

# Error handling setup
$ErrorActionPreference = "Continue"
$ProgressPreference = "SilentlyContinue"

# Logging function
function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Write-Host "[$timestamp] [$Level] $Message"
}

# Service configuration
$services = @{
    "backend" = @{
        "url" = switch ($Environment) {
            "development" { "http://localhost:8000/health" }
            "staging" { "http://localhost:8000/health" }
            "production" { "https://l3arn-backend-prod.eastus.azurecontainerapps.io/health" }
        }
        "port" = 8000
        "container" = "l3arn-backend"
    }
    "frontend" = @{
        "url" = switch ($Environment) {
            "development" { "http://localhost:3000" }
            "staging" { "http://localhost:3000" }
            "production" { "https://l3arn-frontend-prod.eastus.azurestaticapps.net" }
        }
        "port" = 3000
        "container" = "l3arn-frontend"
    }
    "database" = @{
        "url" = "http://localhost:5432"
        "port" = 5432
        "container" = "l3arn-database"
    }
    "redis" = @{
        "url" = "http://localhost:6379"
        "port" = 6379
        "container" = "l3arn-redis"
    }
}

# Monitoring data structure
$monitoringData = @{
    timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    environment = $Environment
    services = @{}
    system = @{}
    alerts = @()
}

function Test-ServiceHealth {
    param([string]$ServiceName, [hashtable]$ServiceConfig)
    
    $healthStatus = @{
        name = $ServiceName
        timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        status = "unknown"
        responseTime = 0
        error = $null
    }
    
    try {
        # Test HTTP endpoint if available
        if ($ServiceConfig.url -and $ServiceConfig.url -notlike "*localhost*") {
            $stopwatch = [System.Diagnostics.Stopwatch]::StartNew()
            $response = Invoke-WebRequest -Uri $ServiceConfig.url -Method GET -TimeoutSec 10
            $stopwatch.Stop()
            
            $healthStatus.responseTime = $stopwatch.ElapsedMilliseconds
            $healthStatus.status = if ($response.StatusCode -eq 200) { "healthy" } else { "unhealthy" }
        }
        
        # Test port connectivity
        $tcpClient = New-Object System.Net.Sockets.TcpClient
        $connection = $tcpClient.BeginConnect("localhost", $ServiceConfig.port, $null, $null)
        $wait = $connection.AsyncWaitHandle.WaitOne(5000, $false)
        
        if ($wait) {
            $tcpClient.EndConnect($connection)
            $healthStatus.status = "healthy"
        } else {
            $healthStatus.status = "unhealthy"
        }
        $tcpClient.Close()
        
        # Check Docker container if applicable
        if ($ServiceConfig.container) {
            try {
                $containerStatus = docker ps --filter "name=$($ServiceConfig.container)" --format "table {{.Status}}"
                if ($containerStatus -and $containerStatus -notlike "*Up*") {
                    $healthStatus.status = "unhealthy"
                    $healthStatus.error = "Container not running"
                }
            } catch {
                $healthStatus.error = "Docker check failed: $($_.Exception.Message)"
            }
        }
        
    } catch {
        $healthStatus.status = "unhealthy"
        $healthStatus.error = $_.Exception.Message
    }
    
    return $healthStatus
}

function Get-SystemResources {
    $systemInfo = @{
        cpu = @{
            usage = (Get-Counter "\Processor(_Total)\% Processor Time").CounterSamples[0].CookedValue
            cores = (Get-WmiObject -Class Win32_Processor).NumberOfCores
        }
        memory = @{
            total = [math]::Round((Get-WmiObject -Class Win32_ComputerSystem).TotalPhysicalMemory / 1GB, 2)
            available = [math]::Round((Get-WmiObject -Class Win32_OperatingSystem).FreePhysicalMemory / 1MB, 2)
            usage = [math]::Round(((Get-WmiObject -Class Win32_ComputerSystem).TotalPhysicalMemory - (Get-WmiObject -Class Win32_OperatingSystem).FreePhysicalMemory) / (Get-WmiObject -Class Win32_ComputerSystem).TotalPhysicalMemory * 100, 2)
        }
        disk = @{
            total = [math]::Round((Get-WmiObject -Class Win32_LogicalDisk -Filter "DeviceID='C:'").Size / 1GB, 2)
            free = [math]::Round((Get-WmiObject -Class Win32_LogicalDisk -Filter "DeviceID='C:'").FreeSpace / 1GB, 2)
            usage = [math]::Round(((Get-WmiObject -Class Win32_LogicalDisk -Filter "DeviceID='C:'").Size - (Get-WmiObject -Class Win32_LogicalDisk -Filter "DeviceID='C:'").FreeSpace) / (Get-WmiObject -Class Win32_LogicalDisk -Filter "DeviceID='C:'").Size * 100, 2)
        }
        network = @{
            connections = (Get-NetTCPConnection -State Listen).Count
            activeConnections = (Get-NetTCPConnection -State Established).Count
        }
    }
    
    return $systemInfo
}

function Test-DockerContainers {
    $containerStatus = @{}
    
    try {
        $containers = docker ps -a --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
        $containerLines = $containers -split "`n" | Select-Object -Skip 1
        
        foreach ($line in $containerLines) {
            if ($line.Trim()) {
                $parts = $line -split "`t"
                if ($parts.Length -ge 2) {
                    $containerName = $parts[0].Trim()
                    $status = $parts[1].Trim()
                    
                    $containerStatus[$containerName] = @{
                        name = $containerName
                        status = if ($status -like "*Up*") { "running" } else { "stopped" }
                        details = $status
                        timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
                    }
                }
            }
        }
    } catch {
        Write-Log "Docker container check failed: $($_.Exception.Message)" "ERROR"
    }
    
    return $containerStatus
}

function Test-DatabaseConnections {
    $dbStatus = @{}
    
    # Test PostgreSQL connection
    try {
        $pgConnection = New-Object System.Net.Sockets.TcpClient
        $pgConnection.BeginConnect("localhost", 5432, $null, $null).AsyncWaitHandle.WaitOne(5000, $false)
        $dbStatus["postgresql"] = @{
            status = "connected"
            port = 5432
            timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        }
        $pgConnection.Close()
    } catch {
        $dbStatus["postgresql"] = @{
            status = "disconnected"
            port = 5432
            error = $_.Exception.Message
            timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        }
    }
    
    # Test Redis connection
    try {
        $redisConnection = New-Object System.Net.Sockets.TcpClient
        $redisConnection.BeginConnect("localhost", 6379, $null, $null).AsyncWaitHandle.WaitOne(5000, $false)
        $dbStatus["redis"] = @{
            status = "connected"
            port = 6379
            timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        }
        $redisConnection.Close()
    } catch {
        $dbStatus["redis"] = @{
            status = "disconnected"
            port = 6379
            error = $_.Exception.Message
            timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        }
    }
    
    return $dbStatus
}

function Generate-Alerts {
    param([hashtable]$MonitoringData)
    
    $alerts = @()
    
    # Service health alerts
    foreach ($service in $MonitoringData.services.Values) {
        if ($service.status -eq "unhealthy") {
            $alerts += @{
                type = "service_unhealthy"
                service = $service.name
                message = "Service $($service.name) is unhealthy"
                severity = "high"
                timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
            }
        }
        
        if ($service.responseTime -gt 5000) {
            $alerts += @{
                type = "service_slow"
                service = $service.name
                message = "Service $($service.name) is responding slowly: $($service.responseTime)ms"
                severity = "medium"
                timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
            }
        }
    }
    
    # System resource alerts
    $system = $MonitoringData.system
    if ($system.cpu.usage -gt 80) {
        $alerts += @{
            type = "high_cpu"
            message = "CPU usage is high: $($system.cpu.usage)%"
            severity = "medium"
            timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        }
    }
    
    if ($system.memory.usage -gt 85) {
        $alerts += @{
            type = "high_memory"
            message = "Memory usage is high: $($system.memory.usage)%"
            severity = "medium"
            timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        }
    }
    
    if ($system.disk.usage -gt 90) {
        $alerts += @{
            type = "high_disk"
            message = "Disk usage is high: $($system.disk.usage)%"
            severity = "high"
            timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        }
    }
    
    return $alerts
}

function Export-MonitoringReport {
    param([hashtable]$Data, [string]$Format)
    
    $timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
    
    if ($Format -eq "json" -or $Format -eq "both") {
        $jsonPath = "monitoring-report-$timestamp.json"
        $Data | ConvertTo-Json -Depth 5 | Out-File -FilePath $jsonPath
        Write-Log "JSON report saved: $jsonPath" "INFO"
    }
    
    if ($Format -eq "html" -or $Format -eq "both") {
        $htmlContent = @"
<!DOCTYPE html>
<html>
<head>
    <title>L3ARN-Labs Monitoring Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .header { background-color: #3b82f6; color: white; padding: 20px; border-radius: 5px; }
        .section { margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }
        .service { margin: 10px 0; padding: 10px; border-left: 4px solid #3b82f6; }
        .healthy { border-left-color: #10b981; }
        .unhealthy { border-left-color: #ef4444; }
        .alert { background-color: #fef3c7; border: 1px solid #f59e0b; padding: 10px; margin: 10px 0; border-radius: 5px; }
        .high { border-left-color: #ef4444; }
        .medium { border-left-color: #f59e0b; }
        .low { border-left-color: #3b82f6; }
    </style>
</head>
<body>
    <div class="header">
        <h1>L3ARN-Labs Monitoring Report</h1>
        <p>Environment: $($Data.environment) | Generated: $($Data.timestamp)</p>
    </div>
    
    <div class="section">
        <h2>Service Health</h2>
        $(foreach ($service in $Data.services.Values) {
            $statusClass = if ($service.status -eq "healthy") { "healthy" } else { "unhealthy" }
            "<div class='service $statusClass'>
                <h3>$($service.name)</h3>
                <p>Status: $($service.status)</p>
                <p>Response Time: $($service.responseTime)ms</p>
                $(if ($service.error) { "<p>Error: $($service.error)</p>" })
            </div>"
        })
    </div>
    
    <div class="section">
        <h2>System Resources</h2>
        <p>CPU Usage: $($Data.system.cpu.usage)%</p>
        <p>Memory Usage: $($Data.system.memory.usage)%</p>
        <p>Disk Usage: $($Data.system.disk.usage)%</p>
        <p>Active Network Connections: $($Data.system.network.activeConnections)</p>
    </div>
    
    <div class="section">
        <h2>Alerts</h2>
        $(foreach ($alert in $Data.alerts) {
            $severityClass = $alert.severity
            "<div class='alert $severityClass'>
                <strong>$($alert.type.ToUpper())</strong>
                <p>$($alert.message)</p>
                <small>Time: $($alert.timestamp)</small>
            </div>"
        })
    </div>
</body>
</html>
"@
        
        $htmlPath = "monitoring-report-$timestamp.html"
        $htmlContent | Out-File -FilePath $htmlPath
        Write-Log "HTML report saved: $htmlPath" "INFO"
    }
}

# Main monitoring loop
Write-Log "Starting L3ARN-Labs Service Monitoring v2.0" "INFO"
Write-Log "Environment: $Environment" "INFO"
Write-Log "Monitoring interval: $IntervalSeconds seconds" "INFO"

$startTime = Get-Date
$endTime = if ($Continuous) { $null } else { $startTime.AddMinutes($DurationMinutes) }

do {
    $currentTime = Get-Date
    Write-Log "Running health checks at $($currentTime.ToString('HH:mm:ss'))" "INFO"
    
    # Update monitoring data timestamp
    $monitoringData.timestamp = $currentTime.ToString("yyyy-MM-dd HH:mm:ss")
    
    # Test service health
    foreach ($serviceName in $services.Keys) {
        $serviceConfig = $services[$serviceName]
        $healthStatus = Test-ServiceHealth -ServiceName $serviceName -ServiceConfig $serviceConfig
        $monitoringData.services[$serviceName] = $healthStatus
        
        $statusColor = if ($healthStatus.status -eq "healthy") { "Green" } else { "Red" }
        Write-Host "$($serviceName): $($healthStatus.status)" -ForegroundColor $statusColor
    }
    
    # Get system resources
    $monitoringData.system = Get-SystemResources
    
    # Test Docker containers
    $monitoringData.containers = Test-DockerContainers
    
    # Test database connections
    $monitoringData.databases = Test-DatabaseConnections
    
    # Generate alerts
    $monitoringData.alerts = Generate-Alerts -MonitoringData $monitoringData
    
    # Display summary
    $healthyServices = ($monitoringData.services.Values | Where-Object { $_.status -eq "healthy" }).Count
    $totalServices = $monitoringData.services.Count
    $alertCount = $monitoringData.alerts.Count
    
    Write-Log "Health Summary: $healthyServices/$totalServices services healthy, $alertCount alerts" "INFO"
    
    # Generate report if requested
    if ($GenerateReport) {
        Export-MonitoringReport -Data $monitoringData -Format $ReportFormat
    }
    
    # Wait for next interval
    if (-not $Continuous -and $currentTime -ge $endTime) {
        Write-Log "Monitoring duration completed" "INFO"
        break
    }
    
    if ($Continuous -or $currentTime -lt $endTime) {
        Write-Log "Waiting $IntervalSeconds seconds until next check..." "INFO"
        Start-Sleep -Seconds $IntervalSeconds
    }
    
} while ($Continuous -or $currentTime -lt $endTime)

Write-Log "Monitoring completed" "INFO"

# Final report
if ($GenerateReport) {
    Export-MonitoringReport -Data $monitoringData -Format $ReportFormat
} 
} 