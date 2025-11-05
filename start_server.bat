@echo off
echo ============================================================
echo Starting Emotion-Aware Authentication Server
echo ============================================================
echo.
echo Server will be available at:
echo   - Main UI: http://localhost:8000/web/index.html
echo   - Admin Dashboard: http://localhost:8000/web/admin.html
echo   - API Docs: http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop the server
echo.
echo ============================================================
echo.

python -m uvicorn backend.main:app --reload
