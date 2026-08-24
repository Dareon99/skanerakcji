[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)][ValidatePattern('^[A-Z0-9][A-Z0-9-]{4,80}$')][string]$PackageId,
    [Parameter(Mandatory=$true)][ValidatePattern('^[A-Z0-9-]{2,40}$')][string]$Area
)

$ErrorActionPreference = 'Stop'
$DocsRoot = Split-Path $PSScriptRoot -Parent
$ActiveRoot = Join-Path $DocsRoot '03-AKTYWNE-PACZKI'
$Templates = Join-Path $DocsRoot '07-SZABLONY'
$Target = Join-Path $ActiveRoot $PackageId

$active = Get-ChildItem -LiteralPath $ActiveRoot -Directory -ErrorAction SilentlyContinue
if ($active) {
    throw "Istnieje juz katalog aktywnej paczki: $($active.Name -join ', '). Najpierw zamknij lub jawnie zatwierdz prace rownolegla."
}
if (Test-Path -LiteralPath $Target) { throw "Paczka juz istnieje: $Target" }

New-Item -ItemType Directory -Path $Target | Out-Null
$mapping = [ordered]@{
    '10-PACKAGE-README.md' = 'README.md'
    '01-SPEC.md' = '01-SPEC.md'
    '02-AUDIT.md' = '02-AUDIT.md'
    '03-CONFLICT-REPORT.md' = '03-CONFLICT-REPORT.md'
    '04-USER-DECISIONS.md' = '04-USER-DECISIONS.md'
    '05-IMPLEMENTATION-CONTRACT.md' = '05-IMPLEMENTATION-CONTRACT.md'
    '06-TEST-EVIDENCE.md' = '06-TEST-EVIDENCE.md'
    '07-ACCEPTANCE.md' = '07-ACCEPTANCE.md'
    '08-FINAL-AS-BUILT.md' = '08-FINAL-AS-BUILT.md'
    '09-SESSION-HANDOFF.md' = '09-SESSION-HANDOFF.md'
}
foreach ($sourceName in $mapping.Keys) {
    $content = Get-Content -LiteralPath (Join-Path $Templates $sourceName) -Raw
    $content = $content.Replace('<PACKAGE-ID>', $PackageId).Replace('<PACKAGE-ID / MODULE>', $PackageId)
    $content = $content -replace '(?m)^AREA:\s*$', "AREA: $Area"
    Set-Content -LiteralPath (Join-Path $Target $mapping[$sourceName]) -Value $content -Encoding UTF8
}
New-Item -ItemType Directory -Path (Join-Path $Target 'EVIDENCE') | Out-Null
New-Item -ItemType Directory -Path (Join-Path $Target 'BACKUP') | Out-Null
Write-Host "Utworzono paczke: $Target" -ForegroundColor Green
Write-Host 'Gate: SPEC ONLY — NO IMPLEMENTATION AUTHORIZED' -ForegroundColor Yellow
