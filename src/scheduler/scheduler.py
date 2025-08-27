#!/usr/bin/env python3
# minimal nanika scheduler (UTC cron). safe: only queues tasks.

import os, json, time, pathlib, yaml, requests
from apscheduler.schedulers.background import BackgroundScheduler

API = os.environ.get("NANIKA_API", "http://api:8000")
RULES_PATH = pathlib.Path("/app/rules.yaml")

def queue(intent, instruction, context=None):
    payload = {"intent": intent, "instruction": instruction, "context": context or {}}
    r = requests.post(f"{API}/task",
                      headers={"content-type": "application/json"},
                      data=json.dumps(payload), timeout=20)
    r.raise_for_status()
    print(f"[queued] {intent} :: {instruction[:60]}...")

def load_rules():
    if RULES_PATH.exists():
        return yaml.safe_load(RULES_PATH.read_text()) or {"jobs": []}
    return {"jobs": []}

def make_job(job):
    def _job():
        try:
            queue(job["intent"], job["instruction"], job.get("context", {}))
        except Exception as e:
            print(f"[scheduler-error] {e}")
    return _job

def main():
    rules = load_rules()
    sched = BackgroundScheduler(timezone="UTC")
    for job in rules.get("jobs", []):
        trig = job.get("trigger", {})
        t = trig.get("type")
        if t == "cron":
            # pass through cron kwargs (minute, hour, day_of_week, etc.)
            kwargs = {k: v for k, v in trig.items() if k != "type"}
            sched.add_job(make_job(job), "cron", **kwargs, id=job.get("name"))
        elif t == "interval":
            kwargs = {k: v for k, v in trig.items() if k != "type"}
            sched.add_job(make_job(job), "interval", **kwargs, id=job.get("name"))
        else:
            print(f"[skip] unknown trigger type for {job.get('name')}")
    sched.start()
    print("[scheduler] started (UTC).")
    try:
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        sched.shutdown()

if __name__ == "__main__":
    main()

