@echo off
setlocal
call "%~dp0env.bat"

%PYTHON_EXEC% src\universal_stub.py %*
endlocal
