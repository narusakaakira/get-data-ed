# run_batch.ps1 - Chay hang loat treo may cho khoa I2 va I3 (tat ca cac Unit)
#
# Cach dung:
#   .\run_batch.ps1                     # Chay lan luot khoa I2 (ALL) roi khoa I3 (ALL)
#   .\run_batch.ps1 -Rounds 2           # Chay 2 luot (luot 1 cao het, luot 2 quet vet cac bai loi)
#   .\run_batch.ps1 -Force              # Ep lam lai ca nhung bai da co

param(
    [int]$Rounds = 1,
    [string[]]$Courses = @("I2", "I3"),
    [switch]$Force
)

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

# Ngan may tinh vao che do Sleep khi treo may
try {
    $sig = @'
    [DllImport("kernel32.dll", SetLastError = true)]
    public static extern uint SetThreadExecutionState(uint esFlags);
'@
    $sleepType = Add-Type -MemberDefinition $sig -Name "Win32Sleep" -Namespace "Win32Functions" -PassThru -ErrorAction SilentlyContinue
    if ($sleepType) {
        # 0x80000001 = ES_CONTINUOUS | ES_SYSTEM_REQUIRED
        $null = $sleepType::SetThreadExecutionState(0x80000001)
        Write-Host "[Anti-Sleep] Da bat che do giu may luon thuc trong suot qua trinh chay." -ForegroundColor Cyan
    }
} catch {
    # Bo qua neu khong add duoc type
}

$startTimeTotal = Get-Date

try {
    for ($round = 1; $round -le $Rounds; $round++) {
        if ($Rounds -gt 1) {
            Write-Host "`n========================================================" -ForegroundColor Magenta
            Write-Host ">>> BAT DAU LUOT QUET $round / $Rounds <<<" -ForegroundColor Magenta
            Write-Host "========================================================" -ForegroundColor Magenta
        }

        $courseIndex = 0
        foreach ($c in $Courses) {
            $courseIndex++
            $startCourse = Get-Date
            Write-Host "`n--------------------------------------------------------" -ForegroundColor Yellow
            Write-Host "[$courseIndex/$($Courses.Count)] Chay khoa: $c | Targets: ALL Unit | Luc: $($startCourse.ToString('HH:mm:ss'))" -ForegroundColor Yellow
            Write-Host "--------------------------------------------------------" -ForegroundColor Yellow

            $flowArgs = @("--course", $c, "--targets", "ALL")
            if ($Force) { $flowArgs += "-Force" }

            try {
                & .\get_data_flow.ps1 @flowArgs
            } catch {
                Write-Host "  [Canh bao] Khoa $c gap loi: $_" -ForegroundColor Red
            }

            $elapsed = (Get-Date) - $startCourse
            Write-Host "`n[OK] Hoan thanh khoa $c trong: $($elapsed.ToString('hh\:mm\:ss'))" -ForegroundColor Green

            # Nghi 5 giay giua 2 khoa hoc de giai phong hoan toan trinh duyet va mang
            if ($courseIndex -lt $Courses.Count) {
                Write-Host "Nghi 5 giay truoc khi chuyen sang khoa tiep theo..." -ForegroundColor Gray
                Start-Sleep -Seconds 5
            }
        }
    }

    $totalElapsed = (Get-Date) - $startTimeTotal
    Write-Host "`n========================================================" -ForegroundColor Cyan
    Write-Host "DA HOAN THANH TAT CA CAC KHOA ($($Courses -join ', '))!" -ForegroundColor Cyan
    Write-Host "Tong thoi gian chay: $($totalElapsed.ToString('hh\:mm\:ss'))" -ForegroundColor Cyan
    Write-Host "Tat ca du lieu da duoc xuat tai: out\lessons" -ForegroundColor Cyan
    Write-Host "========================================================`n" -ForegroundColor Cyan

    # Phat tieng beep bao hieu da xong
    try { [System.Console]::Beep(1000, 600) } catch {}
}
finally {
    # Khoi phuc lai che do Sleep mac dinh cua Windows
    try {
        if ($sleepType) {
            $null = $sleepType::SetThreadExecutionState(0x80000000)
            Write-Host "[Anti-Sleep] Da khoi phuc che do ngu mac dinh cua Windows." -ForegroundColor Gray
        }
    } catch {}
}

