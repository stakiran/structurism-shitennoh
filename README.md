# structurism-shitennoh
構造主義の四天王を決めよ。一人を落とせ。

## run_battles.py の使い方

### 前提
- Python 3.10 以上
- インターネット接続
- OpenAI API キー

### 環境変数
- `OPENAI_API_KEY` (必須): OpenAI API キー
- `OPENAI_MODEL` (任意): 既定は `gpt-5.2`
- `OPENAI_TIMEOUT_SEC` (任意): 既定は `120`

### 実行
PowerShell:

```powershell
$env:OPENAI_API_KEY="YOUR_API_KEY"
python .\scripts\run_battles.py
```

### 動作仕様
- 5人を `1-人物 = 1-agent` として扱う
- 1回の実行で 1on1 をランダムに 1 回だけ実行する
- 何回目かは `battles/` 内の `battle-*.md` を見て自動判定する（次の番号を採用）
- 1ターンの発話ごとに Responses API を 1 回呼ぶ
- 見物者 3 人の敗者判定も、それぞれ API を 1 回呼ぶ
- `battle-30.md` が存在する状態で実行した場合、新規バトルは作らず既存結果から `final.md` のみ更新する

### 出力ファイル
- `battles/battle-1.md` 〜 `battles/battle-30.md`
- `final.md`

### 注意
- API 呼び出し回数が多いため、実行時間とコストが増える
- `OPENAI_API_KEY` 未設定時は実行時にエラーになる
