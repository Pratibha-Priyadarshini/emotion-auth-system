@echo off
echo ========================================
echo Emotion Auth System - Heroku Deployment
echo ========================================
echo.

echo Checking Heroku CLI...
heroku --version
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Heroku CLI not installed!
    echo Please install from: https://devcenter.heroku.com/articles/heroku-cli
    pause
    exit /b 1
)

echo.
echo Step 1: Login to Heroku...
heroku login

echo.
echo Step 2: Create Heroku app...
set /p APP_NAME="Enter your app name (e.g., my-emotion-auth): "
heroku create %APP_NAME%

if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Failed to create app. It might already exist.
    echo Continuing with existing app...
)

echo.
echo Step 3: Adding Python buildpack...
heroku buildpacks:set heroku/python -a %APP_NAME%

echo.
echo Step 4: Deploying to Heroku...
git add .
git commit -m "Deploy to Heroku"
git push heroku main

if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Deployment failed!
    pause
    exit /b 1
)

echo.
echo ========================================
echo Deployment Successful!
echo ========================================
echo.
echo Opening application...
heroku open -a %APP_NAME%

echo.
echo To view logs: heroku logs --tail -a %APP_NAME%
echo To restart: heroku restart -a %APP_NAME%
echo.
pause
