# Ejecutar DESPUÉS de crear en github.com un repo vacío (sin README).
# Ejemplo:
#   .\scripts\push-to-github.ps1 -RepoUrl "https://github.com/tu-usuario/world-happiness-intelligence.git"

param(
    [Parameter(Mandatory = $true)]
    [string] $RepoUrl
)

$ErrorActionPreference = "Stop"
Set-Location (Split-Path -Parent $PSScriptRoot)

if (git remote get-url origin 2>$null) {
    git remote set-url origin $RepoUrl
} else {
    git remote add origin $RepoUrl
}

Write-Host "Subiendo rama main..." -ForegroundColor Cyan
git push -u origin main
Write-Host "Listo. Si pide credenciales, usa un Personal Access Token de GitHub como contraseña." -ForegroundColor Green
