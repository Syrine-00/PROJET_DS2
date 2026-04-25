@echo off
echo ========================================
echo Pushing PROJET_DS2 to GitHub
echo ========================================
echo.

REM Check if git is installed
git --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Git is not installed!
    echo Please install Git from: https://git-scm.com/download/win
    pause
    exit /b 1
)

echo Git is installed. Proceeding...
echo.

REM Initialize git if not already done
if not exist .git (
    echo Initializing git repository...
    git init
    git branch -M main
)

REM Add remote if not already added
git remote get-url origin >nul 2>&1
if errorlevel 1 (
    echo Adding remote repository...
    git remote add origin https://github.com/Syrine-00/PROJET_DS2.git
)

REM Add all files
echo Adding files...
git add .

REM Commit
echo Committing changes...
git commit -m "Week 2 complete: Multi-agent orchestration with backtracking planner, schema validation, security layer, tests, and GUI"

REM Push
echo Pushing to GitHub...
git push -u origin main

echo.
echo ========================================
echo Done! Check https://github.com/Syrine-00/PROJET_DS2
echo ========================================
pause
