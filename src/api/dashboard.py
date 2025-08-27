@app.get("/dashboard")
def dashboard():
    """Show today's generated work ready for execution"""
    
    today = datetime.date.today().isoformat()
    artifacts_dir = ART_DIR / today
    
    if not artifacts_dir.exists():
        return {"message": "No artifacts yet today"}
    
    artifacts = []
    for f in sorted(artifacts_dir.glob("*.md")):
        artifacts.append({
            "name": f.stem,
            "created": datetime.datetime.fromtimestamp(f.stat().st_mtime).isoformat(),
            "preview": f.read_text()[:200] + "..."
        })
    
    return {
        "date": today,
        "artifacts_count": len(artifacts),
        "artifacts": artifacts,
        "next_scheduled": "Check scheduler logs"
    }
