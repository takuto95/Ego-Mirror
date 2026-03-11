import shutil
import os
from pathlib import Path

# Paths
EGO_REPORTS_DIR = Path(r"c:\Users\takut\dev\Ego-Mirror\logs\reports")
CANON_CENTRAL_DIR = Path(r"c:\Users\takut\dev\Canon\logs\ego_mirror\reports")

def sync_pows():
    """
    Sync all generated POV reports from Ego-Mirror to Canon central hub.
    This simulates the real-time reporting of productivity and value.
    """
    print("📡 Ego-Mirror: Syncing Reports to Canon Central...")
    
    if not EGO_REPORTS_DIR.exists():
        print("❌ No reports found to sync.")
        return False
    
    CANON_CENTRAL_DIR.mkdir(parents=True, exist_ok=True)
    
    synced_count = 0
    for report in EGO_REPORTS_DIR.glob("*.md"):
        target_path = CANON_CENTRAL_DIR / report.name
        
        # In a real environment, this might be an encrypted transfer
        try:
            shutil.copy2(report, target_path)
            synced_count += 1
            print(f"  Synced: {report.name} -> Canon Core")
        except Exception as e:
            print(f"  FAILED: {report.name} - {e}")
            
    print(f"✅ Sync complete. {synced_count} reports are now at the Mission Radar for central review.")
    return True

if __name__ == "__main__":
    sync_pows()
