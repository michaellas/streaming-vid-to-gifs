@echo off
setlocal
call "%~dp0env.bat"

%PYTHON_EXEC% src\demux\service.py demux2.json
endlocal
