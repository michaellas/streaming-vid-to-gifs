@echo off
setlocal
call "%~dp0env.bat"

%PYTHON_EXEC% src\gif_convert_service\GifConverter.py --ffmpeg %FFMPEG_EXEC% --out "out" %*
endlocal
