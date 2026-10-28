@echo off
set "BPD_APP=%~dp0..\BPD App\BPD.exe"
if exist "%BPD_APP%" (
    start "" "%BPD_APP%"
    exit /b 0
)
if exist "%LOCALAPPDATA%\Programs\BPD\BPD.exe" (
    start "" "%LOCALAPPDATA%\Programs\BPD\BPD.exe"
    exit /b 0
)
echo BPD executable was not found. Install BPD or restore the BPD App folder.
pause
exit /b 1
