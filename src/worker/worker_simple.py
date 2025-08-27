import os
import json
import time
import yaml
import httpx
import redis
import pathlib
import datetime

REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
OLLAMA = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
ART_DIR = pathlib.Path("/app/artifacts")

ART_DIR.mkdir(parents=True, exist_ok=True)
r = redis.Redis.from_url(REDIS_URL)

def call_ollama(model: str, prompt: str, timeout_s: int = 120) -> str:
    body = {"model": model, "prompt": prompt, "stream": False}
    with httpx.Client(timeout=timeout_s) as client:
        resp = client.post(f"{OLLAMA}/api/generate", json=body)
    resp.raise_for_status()
    return (resp.json().get("response") or "").strip()

def save_artifact(text: str, name: str) -> str:
    day = datetime.date.today().isoformat()
    outdir = ART_DIR / day
    outdir.mkdir(parents=True, exist_ok=True)
    path = outdir / f"{name}.md"
    path.write_text(text)
    return str(path)

# Simple worker loop
while True:
    try:
        item = r.brpop("nanika:tasks", timeout=5)
        if not item:
            continue

        _, raw = item
        task = json.loads(raw)

        intent = task.get("intent", "")
        instruction = task.get("instruction", "")
        request_id = task.get("request_id", "")
        
        # Simple prompt
        prompt = f"""you are nanika. minimal, lowercase, direct.

task: {instruction}

be specific and actionable. no fluff."""

        answer = call_ollama("llama3.1:70b-instruct-q4_K_M", prompt)
        
        # Save
        timestamp = datetime.datetime.now().strftime("%H%M%S")
        artifact_path = save_artifact(answer, f"{intent}_{timestamp}")
        
        print(f"[saved] {artifact_path}")
        print(f"[response preview] {answer[:200]}...")
        
        # Save for UI
        if request_id:
            response_key = f"nanika:response:{request_id}"
            r.setex(response_key, 300, json.dumps({"text": answer}))

    except Exception as e:
        print(f"[error] {e}")
    
    time.sleep(0.2)
