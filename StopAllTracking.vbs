Set WshShell = CreateObject("WScript.Shell")
' Run the PowerShell stop script hidden (0 means hidden).
WshShell.Run "powershell.exe -WindowStyle Hidden -ExecutionPolicy Bypass -File ""C:\Scripts\StopAllTracking.ps1""", 0
