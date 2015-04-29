@echo off
setlocal
call "%~dp0env.bat"

%PYTHON_EXEC% src\input.py %*
endlocal
