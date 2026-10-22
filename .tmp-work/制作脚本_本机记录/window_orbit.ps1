param([int]$Pixels=450,[int]$Repeats=2)
Add-Type -TypeDefinition @'
using System;using System.Runtime.InteropServices;
public static class EdaOrbit { [DllImport("user32.dll")]public static extern bool SetProcessDPIAware();[DllImport("user32.dll")]public static extern bool SetForegroundWindow(IntPtr h);[DllImport("user32.dll")]public static extern bool SetCursorPos(int x,int y);[DllImport("user32.dll")]public static extern void mouse_event(uint f,uint x,uint y,uint d,UIntPtr extra); }
'@
[EdaOrbit]::SetProcessDPIAware()|Out-Null
$edaWin=Get-Process | Where-Object { $_.ProcessName -match 'lceda' -and $_.MainWindowTitle -match 'ChatGPT-PCB-Art' } | Select-Object -First 1
if(-not $edaWin){throw 'No matching EDA window'}
$edaFocusShell=New-Object -ComObject WScript.Shell
$edaFocusShell.SendKeys('%');Start-Sleep -Milliseconds 100
$edaFocusShell.AppActivate($edaWin.Id)|Out-Null
[EdaOrbit]::SetForegroundWindow($edaWin.MainWindowHandle)|Out-Null
for($j=0;$j -lt $Repeats;$j++){
 [EdaOrbit]::SetCursorPos(1050,750)|Out-Null;Start-Sleep -Milliseconds 100
 [EdaOrbit]::mouse_event(2,0,0,0,[UIntPtr]::Zero)
 for($i=1;$i -le 30;$i++){[EdaOrbit]::SetCursorPos((1050+[int]($i*$Pixels/30)),750)|Out-Null;Start-Sleep -Milliseconds 15}
 [EdaOrbit]::mouse_event(4,0,0,0,[UIntPtr]::Zero);Start-Sleep -Milliseconds 300
}
