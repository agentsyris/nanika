from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict
import redis
import json
import uuid
import os
from datetime import datetime

# Create the FastAPI app FIRST
app = FastAPI(title="Nanika - CalmOps Assistant")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Redis connection
redis_client = redis.Redis(
    host=os.getenv('REDIS_HOST', 'redis'),
    port=6379,
    decode_responses=True
)

# Request models
class CalmOpsValidationRequest(BaseModel):
    market: str = "all"
    week: int = 1

# Root endpoint
@app.get("/")
async def root():
    return {
        "service": "Nanika - CalmOps Assistant",
        "status": "operational"
    }

@app.get("/health")
async def health():
    try:
        redis_client.ping()
        return {"status": "healthy", "redis": "connected"}
    except:
        return {"status": "unhealthy", "redis": "disconnected"}

@app.post("/calmops/validate")
async def validate_problem(request: CalmOpsValidationRequest):
    task = {
        'id': str(uuid.uuid4()),
        'type': 'validate_problem',
        'market': request.market,
        'week': request.week,
        'timestamp': datetime.now().isoformat()
    }
    
    redis_client.lpush('nanika_queue', json.dumps(task))
    
    return {
        'task_id': task['id'],
        'message': f'Searching for validation prospects in {request.market}',
        'status': 'queued'
    }

@app.post("/calmops/execute-week/{week_number}")
async def execute_week_tasks(week_number: int):
    """Execute all tasks for a given week"""
    
    week_tasks = {
        1: ['validate_problem', 'create_framework'],
        2: ['generate_landing', 'find_pilots'],
        3: ['setup_operations'],
        4: ['create_case_study', 'launch_content'],
        5: ['develop_referrals', 'scale_outreach'],
        6: ['scale_outreach'],
        7: ['close_full_price']
    }
    
    tasks = week_tasks.get(week_number, [])
    if not tasks:
        return {"error": f"No tasks defined for week {week_number}"}
    
    task_ids = []
    for task_type in tasks:
        task = {
            'id': str(uuid.uuid4()),
            'type': task_type,
            'week': week_number,
            'market': 'new_york',
            'timestamp': datetime.now().isoformat()
        }
        redis_client.lpush('nanika_queue', json.dumps(task))
        task_ids.append({'task_type': task_type, 'task_id': task['id']})
    
    return {
        'week': week_number,
        'tasks_queued': tasks,
        'task_ids': task_ids,
        'message': f'Week {week_number} tasks queued for processing'
    }

@app.get("/calmops/week-status/{week_number}")
async def get_week_status(week_number: int):
    """Check status of all tasks for a week"""
    
    week_tasks = {
        1: ['validate_problem', 'create_framework'],
        2: ['generate_landing', 'find_pilots'],
        3: ['setup_operations'],
        4: ['create_case_study', 'launch_content'],
        5: ['develop_referrals', 'scale_outreach'],
        6: ['scale_outreach'],
        7: ['close_full_price']
    }
    
    expected_tasks = week_tasks.get(week_number, [])
    completed = []
    pending = expected_tasks.copy()
    
    progress = (len(completed) / len(expected_tasks) * 100) if expected_tasks else 0
    
    return {
        'week': week_number,
        'tasks_completed': completed,
        'tasks_pending': pending,
        'overall_progress': f'{progress:.0f}%',
        'total_tasks': len(expected_tasks)
    }

@app.get("/task/{task_id}")
async def get_task_result(task_id: str):
    """Get results of a queued task"""
    result = redis_client.get(f'result:{task_id}')
    
    if result:
        return json.loads(result)
    else:
        queue_length = redis_client.llen('nanika_queue')
        return {
            'task_id': task_id,
            'status': 'pending',
            'queue_position': queue_length,
            'message': 'Task is still processing or not found'
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)