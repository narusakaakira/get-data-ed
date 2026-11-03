$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

$envFile = Join-Path $PSScriptRoot ".env"
if (-not (Test-Path $envFile)) { throw "Không thấy file .env" }

Write-Host "ED_USERNAME = $env:ED_USERNAME"
Write-Host "ED_PASS length = $($env:ED_PASS.Length)" ..


# Đọc từng dòng KEY=VALUE, bỏ qua dòng trống và dòng comment (#)
Get-Content $envFile -Encoding UTF8 | ForEach-Object {
    $line = $_.Trim()
    if ($line -eq "" -or $line.StartsWith("#")) { return }
    $k, $v = $line -split "=", 2
    $v = $v.Trim().Trim('"').Trim("'")
    [Environment]::SetEnvironmentVariable($k.Trim(), $v, "Process")
}

python ed_recorder_autologin.py @args

