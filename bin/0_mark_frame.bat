@echo off
setlocal
call "%~dp0env.bat"

%PYTHON_EXEC% src\mark_frame_service\service.py
endlocal
