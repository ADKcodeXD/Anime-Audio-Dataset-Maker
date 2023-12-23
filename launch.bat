@echo off
echo Installing dependencies from requirements.txt...
pip install -r requirements.txt

echo Starting FastAPI application...
python fastApi.py

pause