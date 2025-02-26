# Define arrays of keywords to match in the command lines.
$psKeywords = @("SystemPerformanceTracker.ps1", "ProcessTracker.ps1", "UserActivityTracker.ps1")
$vbKeywords = @("LaunchSystemPerformanceTracker.vbs", "LaunchProcessTracker.vbs")

# Stop any PowerShell processes running one of our tracking scripts.
Get-CimInstance Win32_Process -Filter "Name = 'powershell.exe'" | ForEach-Object {
    $cmdLine = $_.CommandLine
    if ($cmdLine) {
        foreach ($kw in $psKeywords) {
            if ($cmdLine.ToLower().Contains($kw.ToLower())) {
                Write-Host "Stopping PowerShell process ID $($_.ProcessId) containing '$kw'"
                Stop-Process -Id $_.ProcessId -Force
                break
            }
        }
    }
}

# Stop any VBScript wrapper processes running our self-healing launchers.
Get-CimInstance Win32_Process -Filter "Name = 'wscript.exe'" | ForEach-Object {
    $cmdLine = $_.CommandLine
    if ($cmdLine) {
        foreach ($kw in $vbKeywords) {
            if ($cmdLine.ToLower().Contains($kw.ToLower())) {
                Write-Host "Stopping VBScript process ID $($_.ProcessId) containing '$kw'"
                Stop-Process -Id $_.ProcessId -Force
                break
            }
        }
    }
}

# Optionally, if you have any network capture processes (e.g. tshark), include:
Get-Process -Name tshark -ErrorAction SilentlyContinue | ForEach-Object {
    Write-Host "Stopping tshark process ID $($_.Id)"
    Stop-Process -Id $_.Id -Force
}
