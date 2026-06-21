@echo off

echo Starting Redis...
start cmd /k "docker start redis-server"

timeout /t 3

echo Starting Celery...
start cmd /k "cd /d D:\Fastapi && venv\Scripts\activate && celery -A app.celery_app worker --loglevel=info --pool=solo"

echo Starting FastAPI...
start cmd /k "cd /d D:\Fastapi && venv\Scripts\activate && uvicorn app.main:app --reload"

echo Starting Frontend...
start cmd /k "cd /d D:\Fastapi\frontend && venv\Scripts\activate && npm run dev"

echo All services started.
pause