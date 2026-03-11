import sqlite3
import json
import os
import shutil
from pathlib import Path

GLOBAL_DB = Path(os.path.expandvars(r"%APPDATA%\Antigravity\User\globalStorage\state.vscdb"))
TEMP_GLOBAL = Path(r"c:\Users\takut\dev\Ego-Mirror\tmp_global_state.vscdb")

def analyze_global_storage():
    if not GLOBAL_DB.exists(): return []
    shutil.copy2(GLOBAL_DB, TEMP_GLOBAL)
    conn = sqlite3.connect(TEMP_GLOBAL)
    cursor = conn.cursor()
    cursor.execute("SELECT key, value FROM ItemTable WHERE key LIKE '%chat%' OR key LIKE '%ai%'")
    rows = cursor.fetchall()
    conn.close()
    return rows

if __name__ == "__main__":
    rows = analyze_global_storage()
    print(f"Found {len(rows)} keys in global storage.")
    for key, value in rows:
        print(f"  [KEY] {key}")
        try:
             parsed = json.loads(value)
             print(f"    Sample: {str(parsed)[:200]}")
        except:
             print(f"    Raw: {str(value)[:100]}")
