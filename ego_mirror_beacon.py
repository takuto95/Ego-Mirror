#!/usr/bin/env python3
import os
import sys
import json
import subprocess
from datetime import datetime
from pathlib import Path

# Base configuration
USER_ID = os.getenv("USER_ID", "takuto_unknown") # Set this in .env or environment variable
TARGET_REPO = Path("c:/Users/takut/dev/Canon") 
OUTPUT_DIR = Path("c:/Users/takut/dev/Ego-Mirror/logs/evaluation")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def get_git_diff():
    """Get summarized git diff from the target repo."""
    try:
        # Get diff of staged and unstaged changes
        cmd = ["git", "-C", str(TARGET_REPO), "diff", "HEAD"]
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace')
        diff = result.stdout
        if not diff:
            return "No changes detected."
        # Limit size for LLM efficiency
        if len(diff) > 5000:
            return diff[:5000] + "\n... (truncated)"
        return diff
    except Exception as e:
        return f"Git error: {str(e)}"

def get_ps_history():
    """Get recent PowerShell history."""
    try:
        if sys.platform != "win32":
            return "Not on Windows"
        
        # PowerShell command to get history file path and read last 20 lines
        ps_cmd = "(Get-PSReadlineOption).HistorySavePath"
        hist_path_res = subprocess.run(["powershell", "-Command", ps_cmd], capture_output=True, text=True)
        hist_path = hist_path_res.stdout.strip()
        
        if os.path.exists(hist_path):
            with open(hist_path, "r", encoding="utf-8", errors="replace") as f:
                lines = f.readlines()
                return "".join(lines[-20:])
        return "History file not found."
    except Exception as e:
        return f"PS History error: {str(e)}"

def collect_activity():
    """Collect all metadata for evaluation."""
    print(f"📡 Ego-Mirror Beacon: Collecting activity from {TARGET_REPO}...")
    
    activity = {
        "user_id": USER_ID,
        "timestamp": datetime.now().isoformat(),
        "target_repo": str(TARGET_REPO),
        "git_diff": get_git_diff(),
        "cli_history": get_ps_history(),
        "recent_files": [str(p) for p in TARGET_REPO.glob("**/*") if p.is_file() and (datetime.now().timestamp() - p.stat().st_mtime < 3600)][:10]
    }
    
    # Save raw log mit USER_ID for easy sorting
    filename = f"activity_{USER_ID}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(OUTPUT_DIR / filename, "w", encoding="utf-8") as f:
        json.dump(activity, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Activity logged to {OUTPUT_DIR / filename}")
    return activity

def main():
    # 1. Activities collection (JSON)
    collect_activity()
    
    # 2. PoV Report Generation (Markdown + IDE Analysis)
    try:
        # Import dynamically to avoid path issues
        sys.path.append(str(Path(__file__).parent / "src"))
        from generate_pov_report import generate_pov
        generate_pov()
    except Exception as e:
        print(f"⚠️ PoV Generation failed: {e}")

    # 3. Sync to Canon Central
    try:
        from sync_to_canon import sync_pows
        sync_pows()
    except Exception as e:
        print(f"⚠️ Sync failed: {e}")

if __name__ == "__main__":
    main()
