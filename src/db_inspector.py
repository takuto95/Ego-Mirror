import sqlite3
import os
import shutil
from pathlib import Path

DB_PATH = Path(r"C:\Users\takut\AppData\Roaming\Antigravity\User\workspaceStorage\383507c3baa088b64b29cd1462d3aa41\state.vscdb")
TEMP_DB = Path(r"c:\Users\takut\dev\Ego-Mirror\tmp_inspect.vscdb")

def inspect_db():
    shutil.copy2(DB_PATH, TEMP_DB)
    conn = sqlite3.connect(TEMP_DB)
    cursor = conn.cursor()
    
    # 1. List all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [r[0] for r in cursor.fetchall()]
    print(f"Tables: {tables}")
    
    for table in tables:
        print(f"\n--- Table: {table} ---")
        try:
            cursor.execute(f"SELECT * FROM {table} LIMIT 5")
            cols = [description[0] for description in cursor.description]
            print(f"Columns: {cols}")
            rows = cursor.fetchall()
            for r in rows:
                print(f"  {str(r)[:200]}")
        except Exception as e:
            print(f"  Error: {e}")
            
    conn.close()

if __name__ == "__main__":
    inspect_db()
