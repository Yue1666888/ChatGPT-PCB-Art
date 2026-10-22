param([string]$OutputPath='C:\Users\zhangyue\Documents\Codex\2026-10-13\d-project-deepseek-pcb\chatgpt-work\live-eda.png')
Add-Type -AssemblyName System.Drawing
Add-Type -TypeDefinition @'
using System;using System.Text;using System.Runtime.InteropServices;using System.Collections.Generic;
public static class LiveEdaWindow {
 public delegate bool CB(IntPtr h,IntPtr p);
 [StructLayout(LayoutKind.Sequential)]public struct RECT {public int L,T,R,B;}
 [DllImport("user32.dll")]public static extern bool EnumWindows(CB cb,IntPtr p);
 [DllImport("user32.dll")]public static extern bool IsWindowVisible(IntPtr h);
 [DllImport("user32.dll")]public static extern bool IsIconic(IntPtr h);
 [DllImport("user32.dll",CharSet=CharSet.Unicode)]public static extern int GetWindowText(IntPtr h,StringBuilder b,int n);
 [DllImport("user32.dll")]public static extern uint GetWindowThreadProcessId(IntPtr h,out uint p);
 [DllImport("user32.dll")]public static extern bool GetWindowRect(IntPtr h,out RECT r);
 [DllImport("user32.dll")]public static extern bool PrintWindow(IntPtr h,IntPtr dc,uint f);
 [DllImport("user32.dll")]public static extern bool SetForegroundWindow(IntPtr h);
 [DllImport("user32.dll")]public static extern bool ShowWindow(IntPtr h,int c);
 [DllImport("user32.dll")]public static extern bool SetProcessDPIAware();
 public static string[] List(){var a=new List<string>();EnumWindows((h,p)=>{var b=new StringBuilder(512);GetWindowText(h,b,512);uint id;GetWindowThreadProcessId(h,out id);RECT r;GetWindowRect(h,out r);if(IsWindowVisible(h)&&b.Length>0)a.Add(h+"|"+id+"|"+r.L+"|"+r.T+"|"+r.R+"|"+r.B+"|"+IsIconic(h)+"|"+b);return true;},IntPtr.Zero);return a.ToArray();}
}
'@
[LiveEdaWindow]::SetProcessDPIAware() | Out-Null
$windows=[LiveEdaWindow]::List() | ForEach-Object { $f=$_ -split '\|',8;[pscustomobject]@{Handle=[long]$f[0];PID=[int]$f[1];L=[int]$f[2];T=[int]$f[3];R=[int]$f[4];B=[int]$f[5];Minimized=$f[6];Title=$f[7]} } | Where-Object Title -Match 'ChatGPT-PCB-Art.*嘉立创EDA'
$win=$windows | Sort-Object @{Expression={($_.R-$_.L)*($_.B-$_.T)};Descending=$true} | Select-Object -First 1
if(-not $win){$windows | Format-List;throw 'No matching EDA window'}
if($win.Minimized -eq 'True'){[LiveEdaWindow]::ShowWindow([IntPtr]$win.Handle,9)|Out-Null;Start-Sleep -Milliseconds 400}
$rect=New-Object LiveEdaWindow+RECT
[LiveEdaWindow]::GetWindowRect([IntPtr]$win.Handle,[ref]$rect)|Out-Null
$bmp=[Drawing.Bitmap]::new($rect.R-$rect.L,$rect.B-$rect.T)
$g=[Drawing.Graphics]::FromImage($bmp);$dc=$g.GetHdc();$ok=[LiveEdaWindow]::PrintWindow([IntPtr]$win.Handle,$dc,2);$g.ReleaseHdc($dc)
$bmp.Save($OutputPath);$g.Dispose();$bmp.Dispose()
[pscustomobject]@{Handle=$win.Handle;Title=$win.Title;Left=$rect.L;Top=$rect.T;Width=$rect.R-$rect.L;Height=$rect.B-$rect.T;Captured=$ok;Output=$OutputPath} | ConvertTo-Json -Compress
