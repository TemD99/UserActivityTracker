Set WshShell = CreateObject("WScript.Shell")
' Run the PowerShell script hidden (0 specifies a hidden window).
WshShell.Run "powershell.exe -WindowStyle Hidden -ExecutionPolicy Bypass -File ""C:\Users\Analy\datamules\UserActivityTracker\UserActivityTracker.ps1""", 0
