import sqlite3
import json
import os
import shutil
from pathlib import Path
from datetime import datetime

# ターゲットとなるIDEのストレージパス候補
IDE_PATHS = [
    Path(os.path.expandvars(r"%APPDATA%\Antigravity\User")),
    Path(os.path.expandvars(r"%APPDATA%\Cursor\User")),
    Path(os.path.expandvars(r"%APPDATA%\Code\User")),
]

TEMP_DIR = Path(r"c:\Users\takut\dev\Ego-Mirror\tmp_analysis")

def get_db_connection(db_path):
    temp_db = TEMP_DIR / f"tmp_{datetime.now().timestamp()}.vscdb"
    shutil.copy2(db_path, temp_db)
    return sqlite3.connect(temp_db)

def analyze_chat_patterns(messages):
    """
    メッセージ群からAI活用の詳細なメタデータを抽出
    """
    stats = {
        "total_turns": len(messages),
        "code_request": 0,
        "error_troubleshoot": 0,
        "refactor_request": 0,
        "explanation_request": 0,
        "avg_user_length": 0
    }
    
    user_msgs = [m for m in messages if m.get('role') == 'user' or m.get('type') == 'user']
    if not user_msgs: return stats
    
    total_len = 0
    for m in user_msgs:
        text = str(m.get('text', '') or m.get('bubble', {}).get('text', '')).lower()
        total_len += len(text)
        
        if any(kw in text for kw in ["error", "fail", "修正", "なおして", "バグ"]): stats["error_troubleshoot"] += 1
        if any(kw in text for kw in ["refactor", "リファクタ", "整理", "綺麗"]): stats["refactor_request"] += 1
        if any(kw in text for kw in ["how", "why", "どうして", "説明"]): stats["explanation_request"] += 1
        if "```" in text or "code" in text: stats["code_request"] += 1
        
    stats["avg_user_length"] = total_len / len(user_msgs)
    return stats

def run_ide_ego_mirror():
    TEMP_DIR.mkdir(parents=True, exist_ok=True)
    report = {
        "timestamp": datetime.now().isoformat(),
        "workspaces": []
    }
    
    for ide_base in IDE_PATHS:
        if not ide_base.exists(): continue
        
        # 1. Global Storage (共通設定)
        global_db = ide_base / "globalStorage" / "state.vscdb"
        
        # 2. Workspace Storage (各プロジェクト)
        ws_root = ide_base / "workspaceStorage"
        if ws_root.exists():
            for ws_dir in ws_root.glob("*"):
                db_path = ws_dir / "state.vscdb"
                if not db_path.exists(): continue
                
                try:
                    conn = get_db_connection(db_path)
                    cursor = conn.cursor()
                    
                    # 履歴を保持していそうなキーを探す (Antigravity/Cursor/VSCode/Copilot)
                    query = "SELECT key, value FROM ItemTable WHERE key LIKE 'chat.%' OR key LIKE 'composer.%' OR key LIKE 'interactive.history%'"
                    cursor.execute(query)
                    rows = cursor.fetchall()
                    
                    for key, value in rows:
                        try:
                            data = json.loads(value)
                            messages = []
                            # 1. Cursor Composer
                            if isinstance(data, dict) and "allComposers" in data:
                                for comp in data["allComposers"]:
                                    messages.extend(comp.get("conversation", []))
                            # 2. VS Code Standard Chat / Copilot
                            elif isinstance(data, dict) and "history" in data:
                                messages = data["history"]
                            # 3. Direct list (Simplified history)
                            elif isinstance(data, list):
                                messages = data
                                
                            if messages:
                                ws_stats = analyze_chat_patterns(messages)
                                report["workspaces"].append({
                                    "ide": ide_base.name,
                                    "ws_id": ws_dir.name,
                                    "key": key,
                                    "stats": ws_stats
                                })
                        except: pass
                    conn.close()
                except Exception as e:
                    print(f"Error analyzing {ws_dir.name}: {e}")

    # 結果を保存
    output_file = Path(r"c:\Users\takut\dev\Ego-Mirror\logs\ide_analysis_report.json")
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    return report

if __name__ == "__main__":
    print("🚀 Ego-Mirror: IDE Activity Analysis starting...")
    report = run_ide_ego_mirror()
    print(f"✅ Analysis complete. Scanned {len(report['workspaces'])} active workspaces.")
    if report["workspaces"]:
         print("\n--- Insights ---")
         for ws in report["workspaces"]:
             print(f"IDE: {ws['ide']} | WS: {ws['ws_id'][:8]}...")
             print(f"  AI Turns: {ws['stats']['total_turns']}")
             print(f"  Troubleshooting: {ws['stats']['error_troubleshoot']}")
             print(f"  Avg Prompt: {ws['stats']['avg_user_length']:.1f} chars")
