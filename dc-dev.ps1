# Script para facilitar el uso de docker compose en desarrollo (PowerShell)
$composeFile = "docker-compose.dev.yaml"

if (Get-Command docker -ErrorAction SilentlyContinue) {
    try {
        docker compose version | Out-Null
        $dcCmd = "docker compose"
    } catch {
        $dcCmd = "docker-compose"
    }
} else {
    Write-Host "Docker no está instalado."
    exit 1
}

$cmd = "$dcCmd -f $composeFile $args"
Invoke-Expression $cmd
