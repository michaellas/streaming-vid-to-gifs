@echo off
setlocal
call "%~dp0env.bat"

%PYTHON_EXEC% src\loop_detect_service\FrameAnalyzer.py %*
endlocal
