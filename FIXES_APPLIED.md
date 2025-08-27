# Nanika Website - Fixes Applied

## Issues Found and Fixed

### 1. Requirements File Issue
- **Problem**: The `requirements.txt` file had a space in the filename (` requirements.txt`)
- **Fix**: Renamed to `requirements.txt` (removed leading space)

### 2. Dependency Version Conflicts
- **Problem**: `lxml==5.2.1` was incompatible with `trafilatura==1.9.0`
- **Fix**: Downgraded `lxml` to version `5.1.1` for compatibility

### 3. Missing Dependencies
- **Problem**: `apscheduler` was missing from requirements but needed by scheduler
- **Fix**: Added `apscheduler==3.10.4` to requirements.txt

### 4. Docker Configuration Issues
- **Problem**: Dockerfiles were hardcoding dependencies instead of using requirements.txt
- **Fix**: Updated all Dockerfiles to:
  - Copy and use the main requirements.txt file
  - Follow proper Docker best practices
  - Include proper EXPOSE directives

## Files Modified

1. `requirements.txt` - Fixed filename and dependency versions
2. `src/api/Dockerfile` - Updated to use requirements.txt properly
3. `src/worker/Dockerfile` - Updated to use requirements.txt properly  
4. `src/scheduler/Dockerfile` - Updated to use requirements.txt and added apscheduler

## Testing Results

✅ All Python modules import successfully
✅ FastAPI application starts and responds correctly
✅ Worker module loads without errors
✅ Scheduler module loads without errors
✅ API endpoints return expected responses

## How to Run

### Using Docker Compose (Recommended)
```bash
docker-compose up --build
```

### Manual Installation
```bash
pip install -r requirements.txt

# Start API server
cd src/api
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Start worker (in separate terminal)
cd src/worker  
python worker.py

# Start scheduler (in separate terminal)
cd src/scheduler
python scheduler.py
```

## Services and Ports

- **API Server**: http://localhost:8000
- **Redis**: localhost:6380 (mapped from container port 6379)
- **SearXNG**: http://localhost:8888

## Environment Variables

Make sure to set the following in your `.env` file:
- `SERPER_API_KEY` - Already configured in the provided .env file

## API Endpoints

- `GET /` - Service status
- `GET /health` - Health check with Redis connection status
- `POST /calmops/validate` - Validate CalmOps problems
- `POST /calmops/execute-week/{week_number}` - Execute tasks for a specific week
- `GET /calmops/week-status/{week_number}` - Check week status
- `GET /task/{task_id}` - Get task results

The website is now fully functional and ready to use!

