param(
    [switch]$KeepInfrastructure
)

$ErrorActionPreference = 'Continue'
$Root = $PSScriptRoot
$PidDir = Join-Path $Root 'runtime\pids'

function Get-DescendantProcessIds([int]$ParentId) {
    $children = @(Get-CimInstance Win32_Process -Filter "ParentProcessId=$ParentId" -ErrorAction SilentlyContinue)
    $ids = @()
    foreach ($child in $children) {
        $ids += Get-DescendantProcessIds -ParentId $child.ProcessId
        $ids += [int]$child.ProcessId
    }
    return $ids
}

function Stop-ManagedProcess([string]$Name) {
    $pidFile = Join-Path $PidDir "$Name.pid"
    if (-not (Test-Path -LiteralPath $pidFile)) {
        Write-Host "[SKIP] No PID file for $Name" -ForegroundColor Yellow
        return
    }

    $pidText = (Get-Content -Raw -LiteralPath $pidFile).Trim()
    if ($pidText -match '^\d+$') {
        $processId = [int]$pidText
        $descendants = @(Get-DescendantProcessIds -ParentId $processId)
        foreach ($childId in ($descendants | Sort-Object -Descending)) {
            Stop-Process -Id $childId -Force -ErrorAction SilentlyContinue
        }
        Stop-Process -Id $processId -Force -ErrorAction SilentlyContinue
        Write-Host "[STOP] $Name PID=$processId" -ForegroundColor Cyan
    }
    Remove-Item -LiteralPath $pidFile -Force -ErrorAction SilentlyContinue
}

foreach ($name in @('mall-app-web', 'mall-admin-web', 'mall-portal', 'mall-admin')) {
    Stop-ManagedProcess -Name $name
}

if (-not $KeepInfrastructure) {
    foreach ($container in @('mall-rabbitmq', 'mall-mongo', 'mall-redis', 'mall-mysql')) {
        $running = docker ps --filter "name=^/$container$" --format '{{.Names}}' 2>$null
        if ($running -eq $container) {
            docker stop $container | Out-Null
            Write-Host "[STOP] Docker container $container" -ForegroundColor Cyan
        }
    }
} else {
    Write-Host '[KEEP] Project 2 infrastructure containers remain running.' -ForegroundColor Yellow
}


