#!/usr/bin/env python3
# feedback.py - feed results back to Nanika

import json
import pathlib
import datetime
import sys

FEEDBACK_DIR = pathlib.Path.home() / "nanika/data/feedback"
FEEDBACK_DIR.mkdir(exist_ok=True)

def log_feedback(category: str, content: dict):
    """Log feedback for Nanika to learn from"""
    
    feedback = {
        "timestamp": datetime.datetime.now().isoformat(),
        "category": category,
        "content": content
    }
    
    filename = FEEDBACK_DIR / f"{category}_{datetime.date.today().isoformat()}.json"
    
    existing = []
    if filename.exists():
        existing = json.loads(filename.read_text())
    
    existing.append(feedback)
    filename.write_text(json.dumps(existing, indent=2))
    
    print(f"Logged {category} feedback")

if __name__ == "__main__":
    # Example usage:
    # python feedback.py outreach "replied interested, wants to discuss next week"
    
    if len(sys.argv) < 3:
        print("Usage: python feedback.py <category> <message>")
        sys.exit(1)
    
    category = sys.argv[1]
    message = " ".join(sys.argv[2:])
    
    log_feedback(category, {"message": message})
