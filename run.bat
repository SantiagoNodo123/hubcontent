@echo off
title Content Hub Server
echo ==============================================
echo   Iniciando Content Hub (@s_thiago7 & @nodo_tg)
echo ==============================================
echo.
echo Abriendo navegador en http://localhost:8000...
timeout /t 2 /nobreak >nul
start http://localhost:8000
python app.py
pause
