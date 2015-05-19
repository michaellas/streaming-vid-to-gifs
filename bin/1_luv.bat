@echo off
setlocal
call "%~dp0env.bat"

%PYTHON_EXEC% src\colorspace_to_luv_service\service.py
endlocal
