$ErrorActionPreference = 'Continue'
$Root = $PSScriptRoot

function Get-HttpStatus([string]$Name, [string]$Url) {
    try {
        $response = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 15
        [pscustomobject]@{ Service = $Name; Status = $response.StatusCode; Url = $Url }
    } catch {
        $status = 'DOWN'
        if ($_.Exception.Response) { $status = [int]$_.Exception.Response.StatusCode }
        [pscustomobject]@{ Service = $Name; Status = $status; Url = $Url }
    }
}

Write-Host '=== Project 2 Docker containers ===' -ForegroundColor Cyan
docker ps -a --filter 'name=mall-' --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'

Write-Host ''
Write-Host '=== Ports ===' -ForegroundColor Cyan
$ports = 3307, 6380, 27017, 5672, 15672, 8082, 8085, 8090, 8060
$portResults = foreach ($port in $ports) {
    $listener = Get-NetTCPConnection -State Listen -LocalPort $port -ErrorAction SilentlyContinue | Select-Object -First 1
    [pscustomobject]@{
        Port = $port
        Status = if ($listener) { 'LISTENING' } else { 'DOWN' }
        PID = if ($listener) { $listener.OwningProcess } else { $null }
    }
}
$portResults | Format-Table -AutoSize

Write-Host '=== HTTP ===' -ForegroundColor Cyan
@(
    Get-HttpStatus 'Admin frontend' 'http://127.0.0.1:8090/'
    Get-HttpStatus 'Mall frontend' 'http://127.0.0.1:8060/'
    Get-HttpStatus 'Admin backend health' 'http://127.0.0.1:8082/actuator/health'
    Get-HttpStatus 'Portal backend health' 'http://127.0.0.1:8085/actuator/health'
    Get-HttpStatus 'Mall home API' 'http://127.0.0.1:8085/home/content'
) | Format-Table -AutoSize

Write-Host '=== Admin login smoke test ===' -ForegroundColor Cyan
try {
    $body = @{ username = 'admin'; password = 'macro123' } | ConvertTo-Json
    $login = Invoke-RestMethod -Uri 'http://127.0.0.1:8082/admin/login' -Method Post `
        -ContentType 'application/json;charset=UTF-8' -Body $body -TimeoutSec 20
    [pscustomobject]@{
        Code = $login.code
        TokenReceived = [bool]$login.data.token
        Account = 'admin'
    } | Format-List
} catch {
    Write-Host "Login smoke test failed: $($_.Exception.Message)" -ForegroundColor Red
}



