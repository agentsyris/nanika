from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import os
import redis
import json
import pathlib
import datetime

app = FastAPI(title="nanika.api")
r = redis.Redis.from_url(os.environ.get("REDIS_URL", "redis://localhost:6379/0"))

# Paths
ART_DIR = pathlib.Path("/app/artifacts")
UI_DIR = pathlib.Path("/app/ui")

class Task(BaseModel):
    intent: str
    instruction: str
    context: dict = {}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/task")
def task(t: Task):
    payload = t.model_dump()
    r.lpush("nanika:tasks", json.dumps(payload))
    return {"queued": True}

@app.get("/latest")
def latest():
    """Get the most recent artifact"""
    today = ART_DIR / datetime.date.today().isoformat()
    if not today.exists():
        return {"path": "", "text": "", "created_at": ""}
    
    files = sorted(today.glob("*.md"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not files:
        return {"path": "", "text": "", "created_at": ""}
    
    p = files[0]
    return {
        "path": str(p),
        "text": p.read_text(),
        "created_at": datetime.datetime.fromtimestamp(p.stat().st_mtime).isoformat()
    }

# Serve the UI
if UI_DIR.exists():
    app.mount("/app.js", StaticFiles(directory=UI_DIR), name="ui-js")
    
    @app.get("/")
    async def read_index():
        return FileResponse(UI_DIR / "index.html")
