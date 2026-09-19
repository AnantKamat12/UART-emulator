@echo off

set "PROJECT_ROOT=%~dp0.."

for /d /r "%PROJECT_ROOT%" %%D in (__pycache__) do (
    if exist "%%D" rd /s /q "%%D"
)

del /s /q "%PROJECT_ROOT%\*.log" 2>nul

echo Removed all __pycache__ folders and .log files.
pause