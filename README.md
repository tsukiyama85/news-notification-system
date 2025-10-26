# ニュース収集・要約・LINE通知システム

キーワードに基づいてGoogle News RSSから関連性の高い当日のニュースを収集し、LLMで要約してLINE Messaging APIで通知するシステムです。

## システム構成

```
news-notification-system/
├── config/              # 設定ファイル
│   ├── settings.py      # 環境変数管理
│   └── keywords.yaml    # キーワード設定
├── src/
│   ├── business/        # ビジネスロジック層
│   ├── infrastructure/  # インフラ層
│   ├── models/          # データモデル
│   └── utils/           # ユーティリティ
├── data/
│   ├── cache/           # 通知済みニュース管理
│   └── logs/            # ログファイル
└── tests/               # テストコード
```

## 必要要件

- Python 3.12以上
- uv（Python環境管理ツール）
- LINE Messaging API アクセストークン
- Gemini API キー（Gemini使用時）または Ollama（ローカルLLM使用時）

## セットアップ

### 1. リポジトリのクローン

```bash
git clone <repository-url>
cd news-notification-system
```

### 2. uv環境のセットアップ

```bash
# uvのインストール（まだの場合）
curl -LsSf https://astral.sh/uv/install.sh | sh

# 依存関係のインストール
uv sync
```

### 3. 環境変数の設定

`.env.example`をコピーして`.env`を作成し、必要な情報を入力します。

```bash
cp .env.example .env
```

`.env`ファイルを編集：

```env
# LINE Messaging API
LINE_CHANNEL_ACCESS_TOKEN=your_line_channel_access_token_here

# Google Gemini API（Gemini使用時）
GEMINI_API_KEY=your_gemini_api_key_here

# Ollama API（Ollama使用時）
OLLAMA_API_URL=http://localhost:11434

# LLM設定（gemini または ollama）
DEFAULT_LLM_PROVIDER=gemini
```

### 4. キーワード設定

`config/keywords.yaml`を編集して、通知先とキーワードを設定します。

```yaml
notification_targets:
  - name: "main_channel"
    line_user_id: "YOUR_LINE_USER_ID"
    keywords:
      - "AI"
      - "機械学習"
      - "Python"
    llm_provider: "gemini"  # gemini または ollama
```

### 5. LINE Messaging APIの設定

1. [LINE Developers](https://developers.line.biz/)でMessaging APIチャンネルを作成
2. チャンネルアクセストークンを取得
3. `.env`の`LINE_CHANNEL_ACCESS_TOKEN`に設定
4. LINEアプリで自分のUser IDを確認（LINE公式の[@LINE ID確認bot](https://line.me/R/ti/p/@lineid)を使用）
5. `config/keywords.yaml`の`line_user_id`に設定

### 6. LLM APIの設定

#### Gemini APIを使用する場合

1. [Google AI Studio](https://makersuite.google.com/app/apikey)でAPIキーを取得
2. `.env`の`GEMINI_API_KEY`に設定

#### Ollama を使用する場合

1. [Ollama](https://ollama.ai/)をインストール
2. モデルをダウンロード（例: `ollama pull llama2`）
3. Ollamaサーバーを起動（`ollama serve`）

## 使用方法

### 手動実行

```bash
uv run python src/main.py
```

### テストの実行

```bash
uv run pytest --cov=. --cov-report=xml --cov-report=term-missing
```

## ログ

ログは以下に出力されます：

- コンソール: 標準出力
- ファイル: `data/logs/news_notification.log`

ログレベルは`.env`の`LOG_LEVEL`で設定可能です（DEBUG, INFO, WARNING, ERROR, CRITICAL）。

## トラブルシューティング

### 1. ニュースが取得できない

- インターネット接続を確認
- Google News RSSへのアクセスを確認

### 2. LINE通知が届かない

- `LINE_CHANNEL_ACCESS_TOKEN`が正しいか確認
- `line_user_id`が正しいか確認
- LINE Developersコンソールでチャンネルの状態を確認

### 3. LLM要約が生成されない

- Gemini使用時: `GEMINI_API_KEY`が正しいか確認
- Ollama使用時: Ollamaサーバーが起動しているか確認（`ollama serve`）

## ライセンス

MIT License
