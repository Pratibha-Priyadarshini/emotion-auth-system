@echo off
echo ========================================
echo Emotion Auth System - Docker Deployment
echo ========================================
echo.

echo Step 1: Building Docker image...
docker build -t emotion-auth-system .

if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Docker build failed!
    pause
    exit /b 1
)

echo.
echo Step 2: Stopping existing container...
docker stop emotion-auth 2>nul
docker rm emotion-auth 2>nul

echo.
echo Step 3: Starting new container...
docker run -d -p 8000:8000 --name emotion-auth emotion-auth-system

if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Failed to start container!
    pause
    exit /b 1
)

echo.
echo ========================================
echo Deployment Successful!
echo ========================================
echo.
echo Application is running at:
echo   - Authentication: http://localhost:8000/web/index.html
echo   - Admin Dashboard: http://localhost:8000/web/admin.html
echo   - API Docs: http://localhost:8000/docs
echo.
echo To view logs: docker logs -f emotion-auth
echo To stop: docker stop emotion-auth
echo.
pause
