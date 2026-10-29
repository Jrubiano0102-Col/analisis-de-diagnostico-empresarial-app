@echo off
setlocal
title DIAGNOSTICO EMPRESARIAL

:: Intentar con python en PATH
where python >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    python main.py
    goto end
)

:: Intentar con ruta directa de Python 3.12 en AppData
if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" (
    "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" main.py
    goto end
)

:: Intentar con py launcher
where py >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    py -3 main.py
    goto end
)

echo [ERROR] No se encontro el ejecutable de Python.
echo Asegurese de reiniciar su terminal o instalar Python en el sistema.
pause

:end
endlocal
