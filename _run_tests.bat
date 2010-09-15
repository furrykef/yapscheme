@echo off
echo Testing MyStream...
echo.
python -m yapscheme.tests.test_MyStream
if errorlevel 1 goto done
echo.
echo Running main tests...
echo.
python -m yapscheme.tests.tests
if errorlevel 1 goto done
:done
pause
