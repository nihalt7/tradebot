@echo off
title TradePulse AI - Indian Stock Market Quant Platform
echo ========================================================
echo Starting TradePulse AI Trading Chat Website
echo ========================================================
echo.

start "TradePulse AI Backend (FastAPI)" cmd /k "python run_backend.py"
timeout /t 3 /nobreak >nul
start "TradePulse AI Frontend (React TS)" cmd /k "cd frontend && npm run dev"

echo.
echo Both servers have been launched!
echo Access the application at: http://127.0.0.1:5173
echo Backend API Docs at: http://127.0.0.1:8000/docs
echo.
pause
