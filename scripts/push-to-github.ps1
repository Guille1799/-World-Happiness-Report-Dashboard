# Run AFTER creating an empty GitHub repo (no README from the template).
# Example:
#   .\scripts\push-to-github.ps1 -RepoUrl "https://github.com/you/world-happiness-report-dashboard.git"

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

Write-Host "Pushing branch main..." -ForegroundColor Cyan
git push -u origin main
Write-Host "Done. If prompted for a password, use a GitHub Personal Access Token." -ForegroundColor Green
