# get_data_flow.ps1 - chạy cả quy trình: ghi dữ liệu -> xuất txt + video theo lesson.

# Ví dụ:
#   .\get_data_flow.ps1                              # dùng toàn bộ cấu hình trong .env
#   .\get_data_flow.ps1 --course I2                  # đổi khóa cho lần chạy này
#   .\get_data_flow.ps1 --course I3 --targets "U02-L01..L03"
#   .\get_data_flow.ps1 --manual                     # ép chế độ thủ công (tự gõ nhãn)
#   .\get_data_flow.ps1 -NoExport                    # chỉ ghi, chưa xuất txt/video

# .env KHÔNG còn được nạp ở đây: ed_config.py (Python) tự đọc, nên chạy trực tiếp
# `python ed_recorder_autologin.py ...` cũng cho kết quả giống hệt. Chỉ có MỘT bộ đọc .env duy nhất.


param([switch]$NoExport)

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

if (-not (Test-Path ".env")) { throw "Không thấy file .env - sao chép .env.example thành .env rồi điền thông tin." }

# Ưu tiên môi trường ảo .venv nếu có
$py = if (Test-Path ".\.venv\Scripts\python.exe") { ".\.venv\Scripts\python.exe" } else { "python" }
if (-not (Get-Command $py -ErrorAction SilentlyContinue)) { throw "Không tìm thấy Python ($py)." }

New-Item -ItemType Directory -Force -Path "logs" | Out-Null
$log = "logs\run_{0:yyyyMMdd_HHmmss}.log" -f (Get-Date)
Start-Transcript -Path $log | Out-Null   # nhật ký mỗi lần chạy (không chứa mật khẩu: Python không in nó)

try {
    & $py ed_recorder_autologin_v3.py @args
    if ($LASTEXITCODE -ne 0) { throw "ed_recorder_autologin_v3.py kết thúc với mã lỗi $LASTEXITCODE" }

    if (-not $NoExport -and (Test-Path "out/record")) {
        Write-Host "`n== Xuất txt + video theo lesson =="
        & $py ed_lessons.py out/record
        if ($LASTEXITCODE -ne 0) { throw "ed_lessons.py kết thúc với mã lỗi $LASTEXITCODE" }
    }
    Write-Host "`nXong. Nhật ký: $log"
}
finally {
    Stop-Transcript | Out-Null
}
