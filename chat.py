#!/usr/bin/env python3.11
# chat.py — Haruka terminal chat with persistent memory

import os, sys, json, time, requests, pathlib, datetime, glob
from typing import TypedDict, List, Optional

API = os.environ.get("HARUKA_API", "http://127.0.0.1:8000")
ART_ROOT = pathlib.Path(os.environ.get("HARUKA_ART", str(pathlib.Path.home() / "haruka/data/artifacts")))
MEM_ROOT = pathlib.Path(os.environ.get("HARUKA_MEM", str(pathlib.Path.home() / "haruka/data/memory")))

HISTORY_TURNS = 12          # how many recent exchanges to send each turn
ART_WAIT_SEC = 120          # how long to wait for an artifact
SESSION_NAME = datetime.datetime.now().strftime("session_%Y-%m-%d_%H%M%S")

class Turn(TypedDict):
    user: str
    assistant: str

class Memory(TypedDict):
    session: str
    created_at: str
    summary: str
    turns: List[Turn]

def mem_path(name: str) -> pathlib.Path:
    return MEM_ROOT / f"{name}.json"

def load_mem(name: str) -> Memory:
    p = mem_path(name)
    if p.exists():
        return json.loads(p.read_text())
    return {"session": name, "created_at": datetime.datetime.now().isoformat(), "summary": "", "turns": []}

def save_mem(name: str, mem: Memory) -> None:
    MEM_ROOT.mkdir(parents=True, exist_ok=True)
    mem_path(name).write_text(json.dumps(mem, ensure_ascii=False, indent=2))

def newest_artifact_since(ts: float) -> Optional[pathlib.Path]:
    today_dir = ART_ROOT / datetime.date.today().isoformat()
    if not today_dir.exists():
        return None
    files = [p for p in today_dir.glob("*.md") if p.stat().st_mtime >= ts]
    return max(files, key=lambda p: p.stat().st_mtime) if files else None

def queue(intent: str, instruction: str, context: dict):
    payload = {"intent": intent, "instruction": instruction, "context": context}
    r = requests.post(f"{API}/task", headers={"content-type":"application/json"}, data=json.dumps(payload), timeout=30)
    r.raise_for_status()
    return r.json()

def wait_for_artifact(ts: float, timeout_s: int = ART_WAIT_SEC) -> Optional[pathlib.Path]:
    t0 = time.time()
    while time.time() - t0 < timeout_s:
        p = newest_artifact_since(ts)
        if p:
            return p
        time.sleep(0.3)
    return None

def show_help():
    print("""
commands:
  /new                 start a new session
  /save [name]         save current session under a custom name
  /load <name>         load a saved session (see /list)
  /list                list saved sessions
  /summarize           ask haruka to summarize this session into memory
  /forget              clear summary + turns (keep empty session)
  /export              write a .md transcript to artifacts
  /help                show this help
  /exit                quit
""".strip())

def export_md(mem: Memory) -> pathlib.Path:
    outdir = ART_ROOT / datetime.date.today().isoformat()
    outdir.mkdir(parents=True, exist_ok=True)
    path = outdir / f"{mem['session']}_transcript.md"
    lines = ["# haruka chat transcript", f"_session: {mem['session']}  |  created: {mem['created_at']}_", ""]
    if mem["summary"]:
        lines += ["## summary", mem["summary"], ""]
    lines += ["## turns"]
    for i, t in enumerate(mem["turns"], 1):
        lines += [f"### turn {i}", f"**you:** {t['user']}", f"**haruka:** {t['assistant']}", ""]
    path.write_text("\n".join(lines))
    return path

def main():
    global SESSION_NAME
    MEM_ROOT.mkdir(parents=True, exist_ok=True)
    mem = load_mem(SESSION_NAME)

    print(f"haruka chat — session: {SESSION_NAME} (type /help)")
    while True:
        try:
            msg = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nbye."); return

        if not msg:
            continue

        # commands
        if msg.startswith("/"):
            parts = msg.split()
            cmd = parts[0].lower()
            if cmd in {"/exit", "/quit", "/q"}:
                print("bye."); return
            if cmd == "/help":
                show_help(); continue
            if cmd == "/new":
                SESSION_NAME = datetime.datetime.now().strftime("session_%Y-%m-%d_%H%M%S")
                mem = load_mem(SESSION_NAME)
                print(f"new session: {SESSION_NAME}")
                continue
            if cmd == "/save":
                name = parts[1] if len(parts) > 1 else SESSION_NAME
                save_mem(name, mem)
                print(f"saved: {name}")
                continue
            if cmd == "/list":
                files = sorted(MEM_ROOT.glob("*.json"))
                for p in files:
                    print(p.stem)
                continue
            if cmd == "/load":
                if len(parts) < 2:
                    print("usage: /load <name>"); continue
                name = parts[1]
                if not mem_path(name).exists():
                    print(f"not found: {name}"); continue
                SESSION_NAME = name
                mem = load_mem(SESSION_NAME)
                print(f"loaded: {SESSION_NAME}")
                continue
            if cmd == "/forget":
                mem = {"session": SESSION_NAME, "created_at": datetime.datetime.now().isoformat(), "summary": "", "turns": []}
                save_mem(SESSION_NAME, mem)
                print("memory cleared."); continue
            if cmd == "/export":
                path = export_md(mem)
                print(f"exported: {path}"); continue
            if cmd == "/summarize":
                # ask haruka to write a concise summary of this session
                since = time.time()
                context = {
                    "history": mem["turns"][-HISTORY_TURNS:],
                    "summary": mem.get("summary", "")
                }
                queue("chat", "summarize this session in 8–12 lines: key goals, decisions, open threads, next actions. lowercase.", context)
                art = wait_for_artifact(since)
                if not art:
                    print("(no artifact yet; check worker logs)"); continue
                text = art.read_text().strip()
                mem["summary"] = text
                save_mem(SESSION_NAME, mem)
                print("\n" + text + "\n")
                continue

            print("unknown command. type /help")
            continue

        # regular chat message
        context = {
            "history": mem["turns"][-HISTORY_TURNS:],
            "summary": mem.get("summary", "")
        }
        since = time.time()
        # use "chat" intent (routes to your strategist model if configured)
        queue("chat", f"respond to the user in my lowercase voice. user said: {msg}", context)
        art = wait_for_artifact(since)
        if not art:
            print("(no artifact yet; check worker logs)"); continue
        text = art.read_text().strip()
        print("\n" + text + "\n")
        mem["turns"].append({"user": msg, "assistant": text[:10000]})
        save_mem(SESSION_NAME, mem)

if __name__ == "__main__":
    main()

