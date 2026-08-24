[CmdletBinding()]
param(
    [string]$ProjectRoot
)

$ErrorActionPreference = 'Stop'
if (-not $ProjectRoot) {
    $ProjectRoot = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
}
$ProjectRoot = [System.IO.Path]::GetFullPath($ProjectRoot)
$DocsRoot = Join-Path $ProjectRoot 'DOKUMENTACJA'
$failures = [System.Collections.Generic.List[string]]::new()
$warnings = [System.Collections.Generic.List[string]]::new()

function Pass([string]$Message) { Write-Host "[PASS] $Message" -ForegroundColor Green }
function Warn([string]$Message) { Write-Host "[WARN] $Message" -ForegroundColor Yellow; $warnings.Add($Message) }
function Fail([string]$Message) { Write-Host "[FAIL] $Message" -ForegroundColor Red; $failures.Add($Message) }

Write-Host "SKANER WYKRESOW — KONTROLA SYSTEMU" -ForegroundColor Cyan
Write-Host "Project: $ProjectRoot"

$required = @(
    'AGENTS.md',
    'CLAUDE.md',
    '.gitignore',
    '.gitattributes',
    'DOKUMENTACJA\MASTER-PROJEKT.md',
    'DOKUMENTACJA\STAN-AKTUALNY.md',
    'DOKUMENTACJA\00-STEROWANIE\SYSTEM-PRACY.md',
    'DOKUMENTACJA\00-STEROWANIE\ZASADY-PROJEKTU.md',
    'DOKUMENTACJA\00-STEROWANIE\PROTOKOL-SESJI-AI.md',
    'DOKUMENTACJA\00-STEROWANIE\WERSJONOWANIE-I-GIT.md',
    'DOKUMENTACJA\00-STEROWANIE\DOSTEPY-I-BEZPIECZENSTWO.md',
    'DOKUMENTACJA\04-DECYZJE\DECYZJE-PROJEKTOWE.md',
    'DOKUMENTACJA\05-REJESTRY\REJESTR-SPRINTOW.md',
    'DOKUMENTACJA\05-REJESTRY\REJESTR-ARTEFAKTOW.md'
)
foreach ($relative in $required) {
    $path = Join-Path $ProjectRoot $relative
    if (Test-Path -LiteralPath $path -PathType Leaf) { Pass "required: $relative" }
    else { Fail "missing required file: $relative" }
}

$config = Join-Path $ProjectRoot 'backend\config.py'
$productVersion = $null
if (Test-Path -LiteralPath $config -PathType Leaf) {
    $configText = Get-Content -LiteralPath $config -Raw
    $versionPattern = '(?m)^\s*VERSION\s*=\s*[\x22\x27]([^\x22\x27]+)[\x22\x27]'
    $versionMatch = [regex]::Match($configText, $versionPattern)
    if ($versionMatch.Success) {
        $productVersion = $versionMatch.Groups[1].Value
        Pass "config VERSION=$productVersion"
    } else { Fail 'VERSION not found in backend/config.py' }

    foreach ($flag in @('massive_traffic_manager_enabled','massive_traffic_measurement_enabled')) {
        $m = [regex]::Match($configText, "(?m)^\s*$flag\s*=\s*([^#\r\n]+)")
        if ($m.Success) { Write-Host "[INFO] $flag=$($m.Groups[1].Value.Trim())" }
        else { Warn "flag not found: $flag" }
    }

    $secretPattern = '(?m)^\s*(POLYGON_KEY|MASSIVE_KEY|API_KEY)\s*=\s*[\x22\x27]([^\x22\x27]+)[\x22\x27]'
    $hardcoded = [regex]::Match($configText, $secretPattern)
    if ($hardcoded.Success) { Fail "non-empty hardcoded secret candidate in config variable $($hardcoded.Groups[1].Value)" }
    else { Pass 'no non-empty hardcoded key detected in current config.py' }
} else { Fail 'backend/config.py not found' }

if ($productVersion) {
    foreach ($doc in @('MASTER-PROJEKT.md','STAN-AKTUALNY.md')) {
        $path = Join-Path $DocsRoot $doc
        if (Test-Path -LiteralPath $path) {
            $text = Get-Content -LiteralPath $path -Raw
            if ($text.Contains($productVersion)) { Pass "$doc references current VERSION" }
            else { Fail "$doc does not reference current VERSION $productVersion" }
        }
    }
}

$manifestFiles = Get-ChildItem -LiteralPath (Join-Path $DocsRoot 'ARCHIWUM') -Filter 'HASHES-SHA256.txt' -Recurse -File -ErrorAction SilentlyContinue
if (-not $manifestFiles) { Warn 'no SHA-256 manifests found in ARCHIWUM' }
foreach ($manifest in $manifestFiles) {
    $manifestRoot = Split-Path $manifest.FullName -Parent
    $errors = 0
    foreach ($line in Get-Content -LiteralPath $manifest.FullName) {
        if (-not $line -or $line.StartsWith('#')) { continue }
        if ($line -notmatch '^([0-9a-fA-F]{64})  (.+)$') { $errors++; continue }
        $expected = $matches[1].ToLowerInvariant()
        $relative = $matches[2].Replace('/', [System.IO.Path]::DirectorySeparatorChar)
        $target = Join-Path $manifestRoot $relative
        if (-not (Test-Path -LiteralPath $target -PathType Leaf)) { $errors++; continue }
        $actual = (Get-FileHash -LiteralPath $target -Algorithm SHA256).Hash.ToLowerInvariant()
        if ($actual -ne $expected) { $errors++ }
    }
    $label = $manifest.FullName.Substring($ProjectRoot.Length + 1)
    if ($errors -eq 0) { Pass "hash manifest: $label" }
    else { Fail "hash manifest errors=${errors}: $label" }
}

$port = Get-NetTCPConnection -LocalPort 8000 -State Listen -ErrorAction SilentlyContinue
if ($port) { Write-Host '[INFO] runtime port 8000: LISTENING' }
else { Write-Host '[INFO] runtime port 8000: OFF' }

$previousPreference = $ErrorActionPreference
$ErrorActionPreference = 'SilentlyContinue'
$safeDirectory = "safe.directory=$ProjectRoot"
$gitProbe = & git -c $safeDirectory -C $ProjectRoot rev-parse --is-inside-work-tree 2>$null
$gitProbeCode = $LASTEXITCODE
$ErrorActionPreference = $previousPreference
if ($gitProbeCode -eq 0) {
    Pass 'Git repository initialized'
    $branch = git -c $safeDirectory -C $ProjectRoot branch --show-current
    Write-Host "[INFO] Git branch: $branch"
    $status = git -c $safeDirectory -C $ProjectRoot status --short
    if ($status) { Warn 'Git worktree has uncommitted changes' }
    else { Pass 'Git worktree clean' }
    if (git -c $safeDirectory -C $ProjectRoot remote) { Pass 'Git remote configured' }
    else { Warn 'Git remote not configured' }
} else { Warn 'Git repository not initialized' }

Write-Host ''
Write-Host "SUMMARY: FAIL=$($failures.Count) WARN=$($warnings.Count)" -ForegroundColor Cyan
if ($failures.Count -gt 0) { exit 2 }
if ($warnings.Count -gt 0) { exit 1 }
exit 0
