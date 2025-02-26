# Define SQLite database path
$databasePath = "C:\Users\Analy\datamules\UserActivityTracker\data\user_activity.db"

# Ensure the PSSQLite module is installed
if (-not (Get-Module -ListAvailable -Name PSSQLite)) {
    Install-Module -Name PSSQLite -Force -Scope CurrentUser
}
Import-Module PSSQLite

# Create SQLite table if it doesn't exist
$query = @"
CREATE TABLE IF NOT EXISTS user_activity (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    WindowTitle TEXT,
    ApplicationProcess TEXT,
    StartTime TEXT,
    EndTime TEXT,
    DurationSec REAL,
    ActivityStatus TEXT,
    ActivityCategory TEXT,
    KeystrokeCount INTEGER,
    MouseClickCount INTEGER
);
"@
Invoke-SqliteQuery -DataSource $databasePath -Query $query

# Load process categorization mapping from external JSON file
$CategoryMapPath = "C:\Users\Analy\datamules\UserActivityTracker\data\ProcessCategories.json"
if (Test-Path $CategoryMapPath) {
    $CategoryMap = Get-Content $CategoryMapPath | ConvertFrom-Json
} else {
    Write-Host "Category mapping file not found: $CategoryMapPath"
    $CategoryMap = @{}
}

# Import Windows API functions for detecting key presses, mouse clicks, and last input time
Add-Type @"
using System;
using System.Runtime.InteropServices;
public class Win32 {
    [DllImport("user32.dll", SetLastError=true)]
    public static extern int GetWindowThreadProcessId(IntPtr hWnd, out int lpdwProcessId);

    [DllImport("user32.dll")]
    public static extern short GetAsyncKeyState(int vKey);

    [DllImport("user32.dll")]
    public static extern int GetWindowText(IntPtr hWnd, System.Text.StringBuilder lpString, int nMaxCount);

    [DllImport("user32.dll")]
    public static extern IntPtr GetForegroundWindow();

    [DllImport("user32.dll")]
    public static extern bool GetLastInputInfo(ref LASTINPUTINFO plii);
}

[StructLayout(LayoutKind.Sequential)]
public struct LASTINPUTINFO {
    public uint cbSize;
    public uint dwTime;
}
"@

# Function to get system idle time in seconds using GetLastInputInfo
function Get-SystemIdleTime {
    $lastInputInfo = New-Object LASTINPUTINFO
    $lastInputInfo.cbSize = [System.Runtime.InteropServices.Marshal]::SizeOf($lastInputInfo)
    [Win32]::GetLastInputInfo([ref] $lastInputInfo) | Out-Null
    $idleTimeMilliseconds = [Environment]::TickCount - $lastInputInfo.dwTime
    return $idleTimeMilliseconds / 1000.0
}

function Get-ActiveWindowInfo {
    $hWnd = [Win32]::GetForegroundWindow()
    $builder = New-Object System.Text.StringBuilder 256
    [Win32]::GetWindowText($hWnd, $builder, $builder.Capacity) | Out-Null
    $windowTitle = $builder.ToString()

    # Get process ID using our own local variable (avoid $PID)
    $procId = 0
    [Win32]::GetWindowThreadProcessId($hWnd, [ref] $procId) | Out-Null

    $proc = Get-Process -Id $procId -ErrorAction SilentlyContinue | Select-Object -First 1

    # If window title is blank, try process.MainWindowTitle as fallback
    if ([string]::IsNullOrWhiteSpace($windowTitle) -and $proc) {
        if (-not [string]::IsNullOrWhiteSpace($proc.MainWindowTitle)) {
            $windowTitle = $proc.MainWindowTitle
        }
    }

    # Determine process name from process object or fallback to last known
    $processName = ""
    if ($proc) {
        $processName = $proc.ProcessName
    } elseif ($script:LastProcessName) {
        $processName = $script:LastProcessName
    }

    # If one is blank, fill it with the other
    if ([string]::IsNullOrWhiteSpace($windowTitle) -and -not [string]::IsNullOrWhiteSpace($processName)) {
        $windowTitle = $processName
    } elseif (-not [string]::IsNullOrWhiteSpace($windowTitle) -and [string]::IsNullOrWhiteSpace($processName)) {
        $processName = $windowTitle
    }

    if (-not [string]::IsNullOrWhiteSpace($processName)) {
        $script:LastProcessName = $processName
    }

    return @{
        Title       = $windowTitle
        ProcessName = $processName
    }
}

function Check-InputCounts {
    $keystrokeCount = 0
    $mouseClickCount = 0
    $mouseKeys = @(0x01, 0x02, 0x04)  # Left, Right, Middle mouse buttons
    foreach ($key in $mouseKeys) {
        if (([Win32]::GetAsyncKeyState($key) -band 0x0001) -ne 0) {
            $mouseClickCount++
        }
    }
    foreach ($key in (0x08..0xFE)) {
        if (([Win32]::GetAsyncKeyState($key) -band 0x0001) -ne 0) {
            $keystrokeCount++
        }
    }
    return @{ Keystrokes = $keystrokeCount; MouseClicks = $mouseClickCount }
}

# Detailed categorizer using the external JSON mapping
function Get-ActivityCategory {
    param([string] $procName)
    $procNameLower = $procName.ToLower()
    foreach ($key in $CategoryMap.PSObject.Properties.Name) {
        if ($procNameLower -like "*$key*") {
            return $CategoryMap.$key
        }
    }
    return "Uncategorized"
}

# Initialize tracking variables
$info = Get-ActiveWindowInfo
$script:LastProcessName = $info.ProcessName
$previousTitle = $info.Title
$previousProcName = $info.ProcessName
$activityCategory = Get-ActivityCategory $previousProcName
$startTime = Get-Date
$previousStatus = "Active"
$idleThreshold = 60  # seconds

$keystrokeCountSession = 0
$mouseClickCountSession = 0

while ($true) {
    Start-Sleep -Milliseconds 100
    $currentTime = Get-Date

    # Accumulate keystroke and mouse click counts for this interval
    $inputCounts = Check-InputCounts
    $keystrokesNow = $inputCounts.Keystrokes
    $mouseClicksNow = $inputCounts.MouseClicks
    $keystrokeCountSession += $keystrokesNow
    $mouseClickCountSession += $mouseClicksNow

    # Get current active window info
    $currentInfo = Get-ActiveWindowInfo
    $currentTitle = $currentInfo.Title
    $currentProcName = $currentInfo.ProcessName
    $currentCategory = Get-ActivityCategory $currentProcName

    # Determine current activity status using the system idle time
    $idleTime = Get-SystemIdleTime
    $currentStatus = if ($idleTime -ge $idleThreshold) { "Idle" } else { "Active" }

    # Log session if there's a change in window title, process, or activity status
    if (($currentTitle -ne $previousTitle) -or ($currentStatus -ne $previousStatus) -or ($currentProcName -ne $previousProcName)) {
        $endTime = $currentTime
        $duration = [math]::Round(($endTime - $startTime).TotalSeconds, 2)
        $insertQuery = @"
INSERT INTO user_activity 
(WindowTitle, ApplicationProcess, StartTime, EndTime, DurationSec, ActivityStatus, ActivityCategory, KeystrokeCount, MouseClickCount)
VALUES 
('$previousTitle', '$previousProcName', '$($startTime.ToString("yyyy-MM-dd HH:mm:ss"))', '$($endTime.ToString("yyyy-MM-dd HH:mm:ss"))', $duration, '$previousStatus', '$activityCategory', $keystrokeCountSession, $mouseClickCountSession);
"@
        try {
            Invoke-SqliteQuery -DataSource $databasePath -Query $insertQuery
        } catch {
            # Handle errors if necessary
        }

        # Reset session tracking variables
        $startTime = $currentTime
        $keystrokeCountSession = 0
        $mouseClickCountSession = 0
        $previousTitle = $currentTitle
        $previousProcName = $currentProcName
        $activityCategory = $currentCategory
        $previousStatus = $currentStatus
    }
}
