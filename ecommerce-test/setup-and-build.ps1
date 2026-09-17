$ErrorActionPreference = 'Stop'
$Root = $PSScriptRoot

function Resolve-Executable([string]$Name) {
    $command = Get-Command $Name -ErrorAction SilentlyContinue
    if (-not $command) {
        throw "Required command '$Name' was not found in PATH. Install it or configure the Jenkins tool PATH."
    }
    return $command.Source
}

$JavaExe = Resolve-Executable 'java'
$MavenExe = Resolve-Executable 'mvn'
$NodeExe = Resolve-Executable 'node'
$NpmExe = Resolve-Executable 'npm'

$javaHome = Split-Path (Split-Path $JavaExe -Parent) -Parent
if (Test-Path -LiteralPath $javaHome) { $env:JAVA_HOME = $javaHome }
$env:Path = "$(Split-Path $NodeExe -Parent);$(Split-Path $NpmExe -Parent);$env:Path"

Write-Host '=== Building mall-backend ===' -ForegroundColor Cyan
Push-Location (Join-Path $Root 'source\mall-backend')
try {
    & $MavenExe '-DskipTests=true' '-Ddocker.skip=true' package
    if ($LASTEXITCODE -ne 0) { throw 'Backend build failed.' }
} finally { Pop-Location }

Write-Host '=== Installing and building mall-admin-web ===' -ForegroundColor Cyan
Push-Location (Join-Path $Root 'source\mall-admin-web')
try {
    & $NpmExe ci
    if ($LASTEXITCODE -ne 0) { throw 'mall-admin-web npm ci failed.' }
    & $NpmExe run build
    if ($LASTEXITCODE -ne 0) { throw 'mall-admin-web build failed.' }
} finally { Pop-Location }

Write-Host '=== Installing and building mall-app-web ===' -ForegroundColor Cyan
Push-Location (Join-Path $Root 'source\mall-app-web')
try {
    & $NpmExe ci
    if ($LASTEXITCODE -ne 0) { throw 'mall-app-web npm ci failed.' }
    & $NpmExe run build:h5
    if ($LASTEXITCODE -ne 0) { throw 'mall-app-web build failed.' }
} finally { Pop-Location }

Write-Host 'All modules built successfully. Run start-all.ps1 next.' -ForegroundColor Green
