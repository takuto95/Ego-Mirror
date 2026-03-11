import os
from pathlib import Path

ROOT = Path(os.path.expandvars(r"%APPDATA%\Antigravity"))

def search_text(root, target):
    found = []
    for p in root.rglob("*"):
        if p.is_file() and p.suffix in [".json", ".vscdb", ".txt", ".log"]:
            try:
                content = p.read_bytes()
                if target.encode() in content:
                    found.append(str(p))
            except: pass
    return found

if __name__ == "__main__":
    print(f"Searching for 'composer' in {ROOT}...")
    matches = search_text(ROOT, "composer")
    for m in matches:
        print(f"  MATCH: {m}")
    
    print(f"Searching for 'conversation' in {ROOT}...")
    matches = search_text(ROOT, "conversation")
    for m in matches:
        print(f"  MATCH: {m}")
