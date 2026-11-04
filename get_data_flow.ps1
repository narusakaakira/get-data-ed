# get_data_flow.ps1 - chay ca quy trinh: ghi du lieu -> xuat txt + video theo lesson.

# Vi du:
#   .\get_data_flow.ps1                              # dung toan bo cau hinh trong .env
#   .\get_data_flow.ps1 --course I2                  # doi khoa cho lan chay nay
#   .\get_data_flow.ps1 --course I3 --targets "U02-L01..L03"
#   .\get_data_flow.ps1 --course I3 --targets "U01-L01" --redo
#   .\get_data_flow.ps1 --manual                     # ep che do thu cong (tu go nhan)
#   .\get_data_flow.ps1 -NoExport                    # chi ghi, chua xuat txt/video
#   .\get_data_flow.ps1 -Force                       # lam lai ca cac bai da co trong lessons

param([switch]$NoExport, [switch]$Force)

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

if (-not (Test-Path ".env")) { throw "Khong thay file .env - hay sao chep .env.example thanh .env roi dien thong tin." }

# Uu tien moi truong ao .venv neu co
$py = if (Test-Path ".\.venv\Scripts\python.exe") { ".\.venv\Scripts\python.exe" } else { "python" }
if (-not (Get-Command $py -ErrorAction SilentlyContinue)) { throw "Khong tim thay Python ($py)." }

New-Item -ItemType Directory -Force -Path "logs" | Out-Null
$log = "logs\run_{0:yyyyMMdd_HHmmss}.log" -f (Get-Date)
Start-Transcript -Path $log | Out-Null

try {
    & $py ed_recorder_autologin_v3.py @args
    if ($LASTEXITCODE -ne 0) { throw "ed_recorder_autologin_v3.py ket thuc voi ma loi $LASTEXITCODE" }

    if (-not $NoExport -and (Test-Path "out/record")) {
        Write-Host "`n== Xuat txt + video theo lesson =="
        $lessonArgs = @("out/record")
        if ($Force -or ($args -contains "--redo") -or ($args -contains "-redo")) {
            $lessonArgs += "--force"
        }
        & $py ed_lessons.py @lessonArgs
        if ($LASTEXITCODE -ne 0) { throw "ed_lessons.py ket thuc voi ma loi $LASTEXITCODE" }
    }
    Write-Host "`nXong. Nhat ky: $log"
}
finally {
    Stop-Transcript | Out-Null
}
