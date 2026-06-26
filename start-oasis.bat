@echo off
title Oasis on the Go Spa - Management System
echo ============================================================
echo   Oasis on the Go Spa Management System is starting...
echo   Keep this window OPEN while staff are using the system.
echo   To stop, close this window (or press Ctrl+C).
echo ============================================================
echo.
echo   On THIS computer, open:        http://localhost:8010
echo   On other phones/PCs use:       http://THIS-PC-IP:8010
echo   Customer booking page:         http://THIS-PC-IP:8010/book/
echo.
echo   (Port 8010 is used so this can run alongside the 24K system on 8000.)
echo.
"%~dp0.venv\Scripts\python.exe" "%~dp0manage.py" runserver 0.0.0.0:8010
pause
