@echo off
REM Railway Setup Script for Windows
REM Run this after deploying to Railway

echo ==================================
echo Railway Post-Deployment Setup
echo ==================================

REM Check if Railway CLI is installed
where railway >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo X Railway CLI not found
    echo Install it with: npm i -g @railway/cli
    exit /b 1
)

echo √ Railway CLI found

REM Login to Railway
echo.
echo Step 1: Login to Railway
railway login

REM Link to project
echo.
echo Step 2: Link to your project
railway link

REM Run migrations
echo.
echo Step 3: Running migrations...
railway run python manage.py migrate

REM Create superuser prompt
echo.
echo Step 4: Do you want to create a superuser? (Y/N)
set /p CREATE_SUPER=
if /i "%CREATE_SUPER%"=="Y" (
    railway run python manage.py createsuperuser
)

echo.
echo ==================================
echo √ Setup Complete!
echo ==================================
echo.
echo Your backend is ready!
echo Run 'railway open' to view your deployment
pause
