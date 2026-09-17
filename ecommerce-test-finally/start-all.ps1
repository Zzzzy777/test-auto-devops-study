param(
    [switch]$SkipInfrastructure
)

$ErrorActionPreference = 'Stop'
$Root = $PSScriptRoot
$LogDir = Join-Path $Root 'runtime\logs'
$PidDir = Join-Path $Root 'runtime\pids'

function Resolve-Executable([string]$Name) {
    $command = Get-Command $Name -ErrorAction SilentlyContinue
    if (-not $command) { throw "Required command '$Name' was not found in PATH." }
    return $command.Source
}

$JavaExe = Resolve-Executable 'java'
$NodeExe = Resolve-Executable 'node'
$AdminJar = Join-Path $Root 'source\mall-backend\mall-admin\target\mall-admin-1.0-SNAPSHOT.jar'
$PortalJar = Join-Path $Root 'source\mall-backend\mall-portal\target\mall-portal-1.0-SNAPSHOT.jar'
$AdminVite = Join-Path $Root 'source\mall-admin-web\node_modules\vite\bin\vite.js'
$AppUni = Join-Path $Root 'source\mall-app-web\node_modules\@dcloudio\vite-plugin-uni\bin\uni.js'

New-Item -ItemType Directory -Force -Path $LogDir, $PidDir | Out-Null

function Test-Port([int]$Port) {
    return [bool](Get-NetTCPConnection -State Listen -LocalPort $Port -ErrorAction SilentlyContinue)
}

function Wait-Port([string]$Name, [int]$Port, [int]$TimeoutSeconds = 60) {
    $end = (Get-Date).AddSeconds($TimeoutSeconds)
    while ((Get-Date) -lt $end) {
        if (Test-Port $Port) {
            Write-Host "[OK] $Name is listening on port $Port" -ForegroundColor Green
            return
        }
        Start-Sleep -Seconds 1
    }
    throw "$Name failed to listen on port $Port. Check logs in $LogDir"
}

function Start-ManagedProcess(
    [string]$Name,
    [string]$FilePath,
    [string[]]$Arguments,
    [string]$WorkingDirectory,
    [int]$Port,
    [int]$TimeoutSeconds = 60
) {
    if (Test-Port $Port) {
        Write-Host "[SKIP] $Name is already running on port $Port" -ForegroundColor Yellow
        return
    }

    $pidFile = Join-Path $PidDir "$Name.pid"
    if (Test-Path -LiteralPath $pidFile) {
        $oldPidText = (Get-Content -Raw -LiteralPath $pidFile).Trim()
        if ($oldPidText -match '^\d+$') {
            Stop-Process -Id ([int]$oldPidText) -Force -ErrorAction SilentlyContinue
        }
    }

    $stdout = Join-Path $LogDir "$Name.out.log"
    $stderr = Join-Path $LogDir "$Name.err.log"
    if (Test-Path -LiteralPath $stdout) { Clear-Content -LiteralPath $stdout -ErrorAction SilentlyContinue }
    if (Test-Path -LiteralPath $stderr) { Clear-Content -LiteralPath $stderr -ErrorAction SilentlyContinue }

    $process = Start-Process -FilePath $FilePath `
        -ArgumentList $Arguments `
        -WorkingDirectory $WorkingDirectory `
        -WindowStyle Hidden `
        -RedirectStandardOutput $stdout `
        -RedirectStandardError $stderr `
        -PassThru

    Set-Content -LiteralPath $pidFile -Value $process.Id
    Write-Host "[START] $Name PID=$($process.Id)" -ForegroundColor Cyan
    Wait-Port -Name $Name -Port $Port -TimeoutSeconds $TimeoutSeconds
}

if (-not $SkipInfrastructure) {
    if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
        throw 'Docker command was not found. Start Docker Desktop first.'
    }

    $requiredContainers = @('mall-mysql', 'mall-redis', 'mall-mongo', 'mall-rabbitmq')
    foreach ($container in $requiredContainers) {
        $exists = docker ps -a --filter "name=^/$container$" --format '{{.Names}}'
        if ($exists -ne $container) {
            throw "Required container '$container' does not exist. Run setup-and-build.ps1 first."
        }
        $running = docker ps --filter "name=^/$container$" --format '{{.Names}}'
        if ($running -ne $container) {
            docker start $container | Out-Null
            Write-Host "[START] Docker container $container" -ForegroundColor Cyan
        } else {
            Write-Host "[OK] Docker container $container is already running" -ForegroundColor Green
        }
    }

    Wait-Port -Name 'mall-mysql' -Port 3307 -TimeoutSeconds 60
    Wait-Port -Name 'mall-redis' -Port 6380 -TimeoutSeconds 60
    Wait-Port -Name 'mall-mongo' -Port 27017 -TimeoutSeconds 60
    Wait-Port -Name 'mall-rabbitmq' -Port 5672 -TimeoutSeconds 60
}

foreach ($requiredFile in @($JavaExe, $NodeExe, $AdminJar, $PortalJar, $AdminVite, $AppUni)) {
    if (-not (Test-Path -LiteralPath $requiredFile)) {
        throw "Required file is missing: $requiredFile. Run setup-and-build.ps1 first."
    }
}

Start-ManagedProcess -Name 'mall-admin' -FilePath $JavaExe `
    -Arguments @('-Dspring.profiles.active=dev', '-jar', $AdminJar) `
    -WorkingDirectory (Split-Path $AdminJar) -Port 8082 -TimeoutSeconds 90

Start-ManagedProcess -Name 'mall-portal' -FilePath $JavaExe `
    -Arguments @('-Dspring.profiles.active=dev', '-jar', $PortalJar) `
    -WorkingDirectory (Split-Path $PortalJar) -Port 8085 -TimeoutSeconds 90

Start-ManagedProcess -Name 'mall-admin-web' -FilePath $NodeExe `
    -Arguments @($AdminVite, '--host', '0.0.0.0', '--port', '8090') `
    -WorkingDirectory (Join-Path $Root 'source\mall-admin-web') -Port 8090 -TimeoutSeconds 60

Start-ManagedProcess -Name 'mall-app-web' -FilePath $NodeExe `
    -Arguments @($AppUni, '--host', '0.0.0.0', '--port', '8060') `
    -WorkingDirectory (Join-Path $Root 'source\mall-app-web') -Port 8060 -TimeoutSeconds 90

Write-Host ''
Write-Host 'Project 2 is running:' -ForegroundColor Green
Write-Host '  Admin frontend : http://localhost:8090  (admin / macro123)'
Write-Host '  Mall frontend  : http://localhost:8060'
Write-Host '  Admin backend  : http://localhost:8082'
Write-Host '  Portal backend : http://localhost:8085'
Write-Host '  RabbitMQ UI    : http://localhost:15672  (mall / mall)'
Write-Host "  Logs           : $LogDir"

