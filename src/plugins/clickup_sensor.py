import os
import json

def collect_clickup_activity(api_key, team_id):
    """
    Mock ClickUp sensor. 
    Focus on: Task completion rate, update transparency, and planning.
    """
    if not api_key:
        return {"status": "skipped", "reason": "No API key"}

    # Mock data representing 'Reliability'
    mock_clickup_data = {
        "tasks_completed": 4,
        "due_date_hits": "100%",
        "descriptions_added": True,
        "time_estimated_vs_actual": "Gaps minimal",
        "summary": "タスクの粒度が適切で、期限遵守意識が非常に高い。不確実性の早期報告が確認された。"
    }
    
    return mock_clickup_data

if __name__ == "__main__":
    print(collect_clickup_activity(None, None))
