@echo off
set "VIRTUAL_ENV=C:\Users\Marcin\Desktop\pwr\tirt\env2"

if defined _OLD_VIRTUAL_PROMPT (
    set "PROMPT=%_OLD_VIRTUAL_PROMPT%"
) else (
    if not defined PROMPT (
        set "PROMPT=$P$G"
    )
	set "_OLD_VIRTUAL_PROMPT=%PROMPT%"	
)
set "PROMPT=(env2) %PROMPT%"

if not defined _OLD_VIRTUAL_PYTHONHOME (
    set "_OLD_VIRTUAL_PYTHONHOME=%PYTHONHOME%"
)
set PYTHONHOME=

if defined _OLD_VIRTUAL_PATH (
    set "PATH=%_OLD_VIRTUAL_PATH%"
) else (
    set "_OLD_VIRTUAL_PATH=%PATH%"
)
set "PATH=%VIRTUAL_ENV%\Scripts;%PATH%"



REM set "TCL_LIBRARY=%VIRTUAL_ENV%\Lib\site-packages\tcl\tcl8.5"
REM set "TCL_LIBRARY=C:\programs\portable\Python2.7\App\tcl\tcl8.5"
REM set "TK_LIBRARY=C:\programs\portable\Python2.7\App\tcl\tk8.5"

set "TCL_LIBRARY=tcl\tcl8.5"
set "TK_LIBRARY=tcl\tk8.5"


:END
