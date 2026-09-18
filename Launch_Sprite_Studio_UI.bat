@echo off
title 2D Sprite Studio UI Launcher
color 0A

echo ================================================================
echo       Launching 2D Sprite & Animation Studio (52 Moves)
echo ================================================================
echo.
echo Starting Studio Server on http://127.0.0.1:8190 ...

start /B "" "C:\Users\USER\AppData\Local\Comfy-Desktop\ComfyUI-Installs\ComfyUI\ComfyUI\.venv\Scripts\python.exe" "C:\Users\USER\AppData\Local\Comfy-Desktop\ComfyUI-Shared\sprite_studio_app.py"

timeout /t 2 /nobreak >nul

echo Opening browser...
start http://127.0.0.1:8190

echo.
echo ================================================================
echo Server is running! Keep this window open while using the Studio.
echo Press Ctrl+C or close this window to stop the UI.
echo ================================================================
echo.

pause
