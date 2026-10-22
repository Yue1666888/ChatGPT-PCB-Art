param([int]$X,[int]$Y,[int]$Count=1)
Add-Type -TypeDefinition @'
using System;using System.Runtime.InteropServices;
public static class EdaClick { [DllImport("user32.dll")]public static extern bool SetProcessDPIAware();[DllImport("user32.dll")]public static extern bool SetForegroundWindow(IntPtr h);[DllImport("user32.dll")]public static extern IntPtr GetForegroundWindow();[DllImport("user32.dll")]public static extern bool SetCursorPos(int x,int y);[DllImport("user32.dll")]public static extern void mouse_event(uint f,uint x,uint y,uint d,UIntPtr extra); }
'@
[EdaClick]::SetProcessDPIAware()|Out-Null
$edaWin=Get-Process | Where-Object { $_.ProcessName -match 'lceda' -and $_.MainWindowTitle -match 'ChatGPT-PCB-Art' } | Select-Object -First 1
if(-not $edaWin){throw 'No matching EDA window'}
if([EdaClick]::GetForegroundWindow() -ne $edaWin.MainWindowHandle){
 $edaFocusShell=New-Object -ComObject WScript.Shell
 $edaFocusShell.SendKeys('%');Start-Sleep -Milliseconds 100
 $edaFocusShell.AppActivate($edaWin.Id)|Out-Null
}
[EdaClick]::SetForegroundWindow($edaWin.MainWindowHandle)|Out-Null
Start-Sleep -Milliseconds 200
if([EdaClick]::GetForegroundWindow() -ne $edaWin.MainWindowHandle){throw 'EDA window did not acquire focus'}
[EdaClick]::SetCursorPos($X,$Y)|Out-Null
Start-Sleep -Milliseconds 250
for($i=0;$i -lt $Count;$i++){[EdaClick]::mouse_event(2,0,0,0,[UIntPtr]::Zero);[EdaClick]::mouse_event(4,0,0,0,[UIntPtr]::Zero);Start-Sleep -Milliseconds 120}
'clicked'
