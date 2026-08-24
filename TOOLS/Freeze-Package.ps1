[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)][ValidatePattern('^[A-Z0-9][A-Z0-9-]{4,80}$')][string]$PackageId
)

$ErrorActionPreference = 'Stop'
$DocsRoot = Split-Path $PSScriptRoot -Parent
$ActiveRoot = [System.IO.Path]::GetFullPath((Join-Path $DocsRoot '03-AKTYWNE-PACZKI'))
$PackageRoot = [System.IO.Path]::GetFullPath((Join-Path $ActiveRoot $PackageId))
if (-not $PackageRoot.StartsWith($ActiveRoot + [System.IO.Path]::DirectorySeparatorChar, [System.StringComparison]::OrdinalIgnoreCase)) {
    throw 'Nieprawidlowa sciezka paczki.'
}
if (-not (Test-Path -LiteralPath $PackageRoot -PathType Container)) { throw "Brak paczki: $PackageRoot" }

$acceptance = Join-Path $PackageRoot '07-ACCEPTANCE.md'
$tests = Join-Path $PackageRoot '06-TEST-EVIDENCE.md'
$asBuilt = Join-Path $PackageRoot '08-FINAL-AS-BUILT.md'
foreach ($required in @($acceptance,$tests,$asBuilt)) {
    if (-not (Test-Path -LiteralPath $required -PathType Leaf)) { throw "Brak wymaganego pliku: $required" }
}
$acceptanceText = Get-Content -LiteralPath $acceptance -Raw
if ($acceptanceText -notmatch '(?m)^STATUS:\s*ACCEPTED\s*$') {
    throw 'Acceptance nie ma dokładnego STATUS: ACCEPTED. FREEZE niedozwolony.'
}
$testText = Get-Content -LiteralPath $tests -Raw
if ($testText -notmatch '(?m)^QUALITY GATE:\s*PASS\s*$') {
    throw 'Test evidence nie ma dokładnego QUALITY GATE: PASS. FREEZE niedozwolony.'
}

$manifest = Join-Path $PackageRoot 'HASHES-SHA256.txt'
$freeze = Join-Path $PackageRoot 'FREEZE.md'
if (Test-Path -LiteralPath $freeze) { throw 'FREEZE.md już istnieje. Frozen paczki nie wolno nadpisywać.' }

$lines = @(
    '# SHA-256 manifest',
    "# Package: $PackageId",
    '# HASHES-SHA256.txt and FREEZE.md are excluded to avoid circular hashing.'
)
$files = Get-ChildItem -LiteralPath $PackageRoot -Recurse -File | Where-Object { $_.FullName -notin @($manifest,$freeze) } | Sort-Object FullName
foreach ($file in $files) {
    $relative = $file.FullName.Substring($PackageRoot.Length + 1).Replace('\','/')
    $hash = (Get-FileHash -LiteralPath $file.FullName -Algorithm SHA256).Hash.ToLowerInvariant()
    $lines += "$hash  $relative"
}
Set-Content -LiteralPath $manifest -Value $lines -Encoding UTF8

$timestamp = (Get-Date).ToString('yyyy-MM-ddTHH:mm:ssK')
$freezeText = @"
# FREEZE — $PackageId

STATUS: FROZEN
TIMESTAMP: $timestamp
FILES HASHED: $($files.Count)
ACCEPTANCE: ACCEPTED
QUALITY GATE: PASS

Frozen package is immutable. Any correction requires a new package with SUPERSEDES.
"@
Set-Content -LiteralPath $freeze -Value $freezeText -Encoding UTF8
Write-Host "FROZEN: $PackageRoot" -ForegroundColor Green
Write-Host "Files hashed: $($files.Count)" -ForegroundColor Green
