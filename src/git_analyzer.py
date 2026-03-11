import subprocess
from datetime import datetime
from pathlib import Path

def get_git_activity(repo_path, days=1):
    """
    リポジトリ内の直近n日の変更統計を取得
    """
    try:
        # コミット数と内容のサマリーを取得
        since = datetime.fromtimestamp(datetime.now().timestamp() - days*86400).isoformat()
        cmd = ["git", "-C", str(repo_path), "log", f"--since={since}", "--pretty=format:%h %ad %s", "--date=iso"]
        res = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
        commits = res.stdout.strip().split('\n') if res.stdout.strip() else []
        
        # 変更行数の統計
        cmd_stats = ["git", "-C", str(repo_path), "diff", "--shortstat", f"HEAD@{{{days} day ago}}", "HEAD"]
        res_stats = subprocess.run(cmd_stats, capture_output=True, text=True)
        stats = res_stats.stdout.strip()
        
        return {
            "commit_count": len(commits),
            "commits": commits[:10], # Latest 10
            "stats": stats
        }
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    repo = Path(r"c:\Users\takut\dev\Canon")
    print(get_git_activity(repo))
