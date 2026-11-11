@echo off
chcp 65001 >nul
setlocal
set "HIER=%~dp0"
set "PYTHONPATH=%HIER%src"

for /f "usebackq delims=" %%I in (`powershell -NoProfile -Command "Add-Type -AssemblyName System.Windows.Forms; $d = New-Object System.Windows.Forms.FolderBrowserDialog; $d.Description = 'Projektordner fuer den Sicherheitscheck waehlen'; if ($d.ShowDialog() -eq 'OK') { $d.SelectedPath }"`) do set "PROJEKT=%%I"

if not defined PROJEKT (
  echo Kein Ordner gewaehlt.
  pause
  exit /b 1
)

set "BERICHT=%TEMP%\sicherheitscheck-bericht"
echo Pruefe: %PROJEKT%
echo.

where py >nul 2>nul && (set "PY=py -3") || (set "PY=python")
%PY% -m sicherheitscheck "%PROJEKT%" --bericht-ordner "%BERICHT%"
set "CODE=%ERRORLEVEL%"

echo.
if exist "%BERICHT%\bericht.md" start "" "%BERICHT%\bericht.md"
echo Rueckgabecode: %CODE%  (0 = alles geprueft, keine Funde; 1 = Funde; 3 = Stufen liefen nicht)
pause
exit /b %CODE%
