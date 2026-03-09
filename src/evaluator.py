#!/usr/bin/env python3
import os
import json
import requests
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Load environment
load_dotenv(Path("c:/Users/takut/dev/Canon/.env"))
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

DATA_DIR = Path("c:/Users/takut/dev/Ego-Mirror/logs/evaluation")
PROCESSED_DIR = Path("c:/Users/takut/dev/Ego-Mirror/logs/processed")
REPORTS_DIR = Path("c:/Users/takut/dev/Ego-Mirror/logs/reports")

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

SYSTEM_PROMPT = """
あなたは自律人事評価システム「Ego-Mirror（エゴ・ミラー）」の評価・推論エンジンです。
収集された活動ログを分析し、ユーザーの貢献と成長を客観的にスコアリングしてください。

【評価軸：Global Core (共通)】
1. Speed (実装・解決の速度)
2. Quality (コードの質、テスト、ドキュメントの配慮)
3. AI-Utilization (AIエージェントをいかに使いこなしているか)
4. Problem-Solving (困難な課題への論理的アプローチ)
5. Growth/Resilience (同じミスを繰り返さない仕組み化、新しい挑戦)

【評価軸：Custom Local (独自設定)】
{custom_axes_prompt}

【注意点】
- バグの発生はマイナス評価ではなく「解決プロセス」の材料として扱う。
- カスタム軸についても可能な限りログから推論すること。
- ユーザーに対して「次の評価を上げるための具体的なアドバイス」を必ず含めること。
"""

def load_custom_axes():
    """Load local custom evaluation axes."""
    axes_content = ""
    config_dir = Path("c:/Users/takut/dev/Ego-Mirror/config/custom_axes")
    for p in config_dir.glob("*.json"):
        try:
            with open(p, "r", encoding="utf-8") as f:
                axes = json.load(f)
                for key, val in axes.items():
                    axes_content += f"- {val['desc']} ({val['points']}点): {', '.join(val['criteria'])}\n"
        except Exception as e:
            print(f"Warning: Failed to load custom axis {p.name}: {e}")
    return axes_content or "（カスタム軸設定なし）"

def evaluate_activity(activity_file: Path):
    """Evaluate a single activity file."""
    with open(activity_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    user_id = data.get("user_id", "unknown")
    user_report_path = REPORTS_DIR / user_id / "daily_evaluation.md"
    user_report_path.parent.mkdir(parents=True, exist_ok=True)

    custom_axes_prompt = load_custom_axes()
    current_system_prompt = SYSTEM_PROMPT.replace("{custom_axes_prompt}", custom_axes_prompt)

    print(f"🧠 Evaluating activity for user [{user_id}]: {activity_file.name}...")

    prompt = f"User: {user_id}\nActivity Log:\n{json.dumps(data, indent=2, ensure_ascii=False)}"

    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": current_system_prompt},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7
    }

    try:
        response = requests.post("https://api.deepseek.com/chat/completions", headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()["choices"][0]["message"]["content"]
        
        # Write report
        with open(user_report_path, "a", encoding="utf-8") as f:
            f.write(f"\n\n## Evaluation: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(result)
            f.write("\n\n---")
            
        print(f"📊 Evaluation report updated for [{user_id}] at: {user_report_path}")
        
        # Mark as processed
        activity_file.rename(PROCESSED_DIR / activity_file.name)
        
    except Exception as e:
        print(f"❌ Evaluation failed for {activity_file.name}: {e}")

def run_evaluation_loop():
    """Find all unprocessed activity logs and evaluate them."""
    files = list(DATA_DIR.glob("activity_*.json"))
    if not files:
        print("No new activity logs to process.")
        return

    print(f"🚀 Found {len(files)} new activity logs to evaluate.")
    for f in files:
        evaluate_activity(f)

if __name__ == "__main__":
    run_evaluation_loop()
