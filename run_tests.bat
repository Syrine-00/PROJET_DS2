@echo off
REM Test runner script for Windows

echo Running unit tests...
py -m pytest tests/ -v --tb=short

echo.
echo Test coverage summary:
py -m pytest tests/ --co -q

pause
