@echo off
setlocal
call "%~dp0env.bat"

%PYTHON_EXEC% src\gif_convert_service\stub_input.py %FFMPEG_EXEC% %*
endlocal