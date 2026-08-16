param(
    [string]$ManagedRoot = (Join-Path $PSScriptRoot '..\.red-tag-demo'),
    [int]$ThresholdMb = 32,
    [int]$SeedMb = 64
)

$ErrorActionPreference = 'Stop'
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$python = Join-Path $repoRoot '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $python)) {
    throw "Python environment not found: $python"
}

& $python (Join-Path $PSScriptRoot 'local_windows_proof.py') `
    --root $ManagedRoot `
    --threshold-mb $ThresholdMb `
    --seed-mb $SeedMb `
    --output (Join-Path $repoRoot 'artifacts\local-executor-proof.json')
