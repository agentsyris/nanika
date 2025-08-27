import os
import json
import time
import httpx
import redis
import pathlib
import datetime
from urllib.parse import quote

REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
OLLAMA = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
ART_DIR = pathlib.Path("/app/artifacts")

r = redis.Redis.from_url(REDIS_URL)

def search_web(query: str) -> str:
    """Search using DuckDuckGo HTML version (no API key needed)"""
    print(f"[web search] {query}")
    try:
        with httpx.Client(follow_redirects=True) as client:
            # Use DuckDuckGo HTML version
            response = client.get(
                f"https://html.duckduckgo.com/html/?q={quote(query)}",
                headers={"User-Agent": "Mozilla/5.0"}
            )
            
            if response.status_code == 200:
                # Basic extraction - you'd want to parse this better
                text = response.text
                # Extract result snippets (quick and dirty)
                results = []
                lines = text.split('\n')
                for i, line in enumerate(lines):
                    if 'result__snippet' in line and i+1 < len(lines):
                        snippet = lines[i+1].strip().replace('<b>', '').replace('</b>', '')
                        if snippet and len(snippet) > 20:
                            results.append(snippet)
                
                if results:
                    return f"Search results for '{query}':\n" + "\n".join(results[:5])
            
        return f"No results found for: {query}"
    except Exception as e:
        return f"Search failed: {e}"

def scrape_url(url: str) -> str:
    """Scrape content from a URL"""
    print(f"[scraping] {url}")
    try:
        with httpx.Client(follow_redirects=True, timeout=10) as client:
            response = client.get(url, headers={"User-Agent": "Mozilla/5.0"})
            if response.status_code == 200:
                # Extract text (basic - you'd want BeautifulSoup for better extraction)
                text = response.text
                # Remove HTML tags (very basic)
                import re
                clean = re.sub('<.*?>', '', text)
                return clean[:2000]  # First 2000 chars
    except Exception as e:
        return f"Could not fetch {url}: {e}"
    return "Failed to fetch URL"

def call_ollama(model: str, prompt: str) -> str:
    body = {"model": model, "prompt": prompt, "stream": False}
    try:
        with httpx.Client(timeout=120) as client:
            resp = client.post(f"{OLLAMA}/api/generate", json=body)
        resp.raise_for_status()
        return resp.json().get("response", "").strip()
    except Exception as e:
        return f"error: {e}"

def save_artifact(text: str, name: str) -> str:
    day = datetime.date.today().isoformat()
    outdir = ART_DIR / day
    outdir.mkdir(parents=True, exist_ok=True)
    ts = datetime.datetime.now().strftime("%H%M%S")
    path = outdir / f"{name}_{ts}.md"
    path.write_text(text)
    return str(path)

print("[nanika] あい - ready with web access")

while True:
    try:
        item = r.brpop("nanika:tasks", timeout=5)
        if not item:
            continue
            
        _, raw = item
        task = json.loads(raw)
        instruction = task.get('instruction', '')
        
        print(f"[task] {instruction[:50]}...")
        
        # Check if this needs web search
        needs_search = any(word in instruction.lower() for word in [
            'real', 'actual', 'find', 'search', 'companies', 'website', 
            'research', 'identify', 'current', 'latest'
        ])
        
        web_context = ""
        if needs_search:
            # Extract what to search for
            if 'companies' in instruction.lower():
                search_query = "creative agencies 50-200 employees creative director"
                web_context = search_web(search_query)
                
                # Try another search for more specific results
                search_query2 = "mid-size creative agencies workflow problems"
                web_context += "\n\n" + search_web(search_query2)
        
        prompt = f"""you are nanika. you have web access. never hallucinate.

web search results:
{web_context if web_context else "no web search performed"}

task: {instruction}

if the task asks for real companies or real data, ONLY use information from the web search results above.
if you cannot find real information, say "cannot find real data for this request."
never make up company names or data.
be minimal and direct. lowercase."""

        answer = call_ollama("llama3.1:70b-instruct-q4_K_M", prompt)
        
        path = save_artifact(answer, task.get('intent', 'task'))
        print(f"[saved] {path}")
        
        if task.get('request_id'):
            r.setex(f"nanika:response:{task['request_id']}", 300, json.dumps({"text": answer}))
            
    except Exception as e:
        print(f"[error] {e}")
    
    time.sleep(0.5)
