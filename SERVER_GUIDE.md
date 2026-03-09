# 🏁 Ego-Mirror: 社内サーバ運用ガイド (PROTOTYPE)

社内の共通サーバ（Windows/Linux）で `Ego-Mirror` を稼働させ、各メンバーの活動を集約・評価するための設定手順です。

## 🏛️ サーバー構成

1.  **データの集約先 (DATA_DIR)**: 
    - `c:/Users/takut/dev/Ego-Mirror/logs/evaluation`
    - 各メンバーの端末から生成された `activity_USERID_TIMESTAMP.json` をこのディレクトリに集約します。
    - 方法：共有フォルダとして公開するか、Git Push / API でこの場所にファイルを置くように設定します。

2.  **推論エンジン (Evaluator)**:
    - サーバー上で `python src/evaluator.py` を定期実行（タスクスケジューラ / cron）します。
    - DeepSeek API キーが必要です。

## 🚀 運用手順

### 1. メンバー側の設定 (Agent-In-The-Box)
各メンバーの `.env` または環境変数に以下を設定します。
```bash
USER_ID="member_name_01"
```
その後、`python ego_mirror_beacon.py` を実行すると、そのメンバー専用の活動ログが生成されます。

### 2. サーバー側の起動
サーバー上で以下のコマンドを実行し、未処理のログを一括で解析します。
```bash
python src/evaluator.py
```
解析が完了したログは `logs/processed/` へ移動され、評価レポートは `logs/reports/USER_ID/daily_evaluation.md` に生成されます。

### 3. タクトの Canon への集約
サーバーで生成された `logs/reports/` 以下の Markdown ファイルを、タクトさんの端末（Canon）が読み取れる場所に同期します。
これで、Canon の **MISSION RADAR** に全メンバーの「最新の評価」が表示されるようになります。

## 🛡️ 注意事項
- **プライバシー**: `Ego-Mirror` は詳細なログを解析しますが、サーバーへ送る前に「機密情報の除外」を Beacon 側で行う設定を推奨します。
- **リソース**: 大人数の場合、LLM のトークン消費量と API コストに注意してください。
