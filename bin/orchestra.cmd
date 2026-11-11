@echo off
python -m orchestra_core.cli %*
exit /b %ERRORLEVEL%
