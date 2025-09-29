@echo off
echo Setting up virtual environment in temp location...

cd /d "D:\Psnal\SIDE GIGS\projects\taqneeq\backend"

echo Creating virtual environment in temp directory...
python -m venv C:\temp\ewallet_venv

echo Activating virtual environment...
call C:\temp\ewallet_venv\Scripts\activate

echo Installing dependencies...
pip install -r requirements.txt
pip install pytest pytest-asyncio httpx requests

echo.
echo Virtual environment setup complete!
echo Location: C:\temp\ewallet_venv
echo.
echo Running tests...
python -m pytest tests/ -v

pause