# NAKAI Matcha Chatbot — System Documentation

## Overview

NAKAI Matcha Concierge は、バリスタと一般消費者向けの AI チャットボットシステム。
RAG (Retrieval-Augmented Generation) を使い、NAKAI の商品・レシピ・抹茶知識に基づいた回答を生成する。

---

## Architecture

```
Browser (PWA / Widget / Shopify)
  ├── session_id (localStorage)
  └── POST /api/chat
         │
         ▼
  FastAPI (Render.com)
  ├── RAG Engine
  │   ├── ChromaDB (Vector Search)
  │   └── NVIDIA NIM (LLM: Llama 3.3 70B)
  ├── Async Logging → Supabase
  ├── /api/admin/* → Knowledge CRUD + Analytics
  └── /admin → Admin Dashboard
         │
         ▼
  Supabase (PostgreSQL)
  ├── conversations
  ├── messages
  └── knowledge_articles
```

---

## URLs

| URL | Description |
|-----|-------------|
| https://nakai-matcha-chat.onrender.com/app | PWA アプリ |
| https://nakai-matcha-chat.onrender.com/admin | 管理画面 |
| https://nakai-matcha-chat.onrender.com/widget.js | Shopify Widget |
| https://nakai-matcha-chat.onrender.com/api/health | ヘルスチェック |
| https://nakaimatcha.com | Shopify ストア |
| https://supabase.com/dashboard | Supabase ダッシュボード |
| https://dashboard.render.com | Render ダッシュボード |
| https://build.nvidia.com | NVIDIA NIM API |
| https://github.com/takahiranakai-ops/nakai-matcha-chatbot | GitHub リポジトリ |

---

## Environment Variables

Render ダッシュボード > nakai-matcha-chat > Environment で管理。

| Variable | Description | Required |
|----------|-------------|----------|
| `NGC_API_KEY` | NVIDIA API キー (build.nvidia.com で取得) | Yes |
| `SHOPIFY_STORE_URL` | Shopify ドメイン (`nakaimatcha.com`) | Yes |
| `SHOPIFY_STOREFRONT_TOKEN` | Shopify Storefront API トークン | Yes |
| `SHOPIFY_ADMIN_TOKEN` | Shopify Admin API トークン | Yes |
| `REFRESH_SECRET` | データ再取込み用シークレット | Yes |
| `ALLOWED_ORIGINS` | CORS 許可オリジン (カンマ区切り) | Yes |
| `SUPABASE_URL` | Supabase プロジェクト URL | Yes |
| `SUPABASE_SERVICE_KEY` | Supabase service_role キー | Yes |
| `ADMIN_PASSWORD` | 管理画面ログインパスワード | Yes |
| `NVIDIA_CHAT_MODEL` | LLM モデル ID (default: `meta/llama-3.3-70b-instruct`) | No |
| `NVIDIA_EMBED_MODEL` | 埋め込みモデル ID (default: `nvidia/nv-embedqa-e5-v5`) | No |
| `MAX_CONTEXT_CHUNKS` | RAG 最大チャンク数 (default: `5`) | No |

---

## File Structure

```
nakai-matcha-chatbot/
├── render.yaml                      # Render デプロイ設定
├── .env.example                     # 環境変数テンプレート
├── SYSTEM_DOCS.md                   # このドキュメント
│
├── backend/
│   ├── main.py                      # FastAPI アプリ + ルーター登録
│   ├── config.py                    # 設定 (環境変数読み込み)
│   ├── requirements.txt             # Python 依存パッケージ
│   │
│   ├── api/
│   │   ├── routes.py                # /api/chat, /api/health, /api/refresh
│   │   ├── admin_routes.py          # /api/admin/* (Knowledge CRUD, Analytics)
│   │   ├── admin_page.py            # /admin (管理画面 HTML)
│   │   ├── pwa.py                   # /app (PWA アプリ HTML/CSS/JS)
│   │   ├── widget.py                # /widget.js (Shopify 埋め込みウィジェット)
│   │   ├── models.py                # Pydantic リクエスト/レスポンスモデル
│   │   └── middleware.py            # レート制限設定
│   │
│   ├── services/
│   │   ├── rag_engine.py            # RAG パイプライン (検索 → 回答生成)
│   │   ├── vector_store.py          # ChromaDB ラッパー
│   │   ├── nvidia_client.py         # NVIDIA NIM API (Embedding + LLM)
│   │   ├── supabase_client.py       # Supabase REST API ラッパー
│   │   ├── shopify_client.py        # Shopify データ取得
│   │   ├── data_processor.py        # ドキュメント処理 (チャンク分割)
│   │   └── prompt_templates.py      # システムプロンプト
│   │
│   ├── scripts/
│   │   ├── ingest.py                # データ取込みスクリプト
│   │   ├── migrate_knowledge.py     # .txt → Supabase 移行スクリプト
│   │   └── supabase_schema.sql      # DB スキーマ (初回のみ実行)
│   │
│   ├── knowledge/                   # ナレッジベースファイル (16 files)
│   │   ├── nakai_products.txt / _ja.txt
│   │   ├── barista_guide.txt / _ja.txt
│   │   ├── revi_recipes.txt / _ja.txt
│   │   ├── matcha_faq.txt / _ja.txt
│   │   ├── matcha_advanced_faq.txt
│   │   ├── matcha_basics_ja.txt
│   │   ├── matcha_powder_guide.txt
│   │   ├── matcha_science.txt
│   │   ├── matcha_vs_coffee.txt
│   │   ├── water_science.txt
│   │   └── shipping_and_returns.txt / _ja.txt
│   │
│   └── data/chroma_db/              # ベクトル DB 永続化ディレクトリ
│
├── shopify-theme/                   # Shopify テーマ用ファイル
│   ├── snippets/nakai-chat-widget.liquid
│   └── sections/nakai-chat-page.liquid
│
└── *.png                            # ロゴ画像アセット
```

---

## API Endpoints

### Public

| Method | Path | Description | Rate Limit |
|--------|------|-------------|------------|
| POST | `/api/chat` | チャットメッセージ送受信 | 20/分 |
| GET | `/api/health` | ヘルスチェック | - |
| POST | `/api/refresh` | データ再取込み (`X-Refresh-Secret` 必須) | 5/時 |
| GET | `/app` | PWA アプリケーション | - |
| GET | `/widget.js` | Shopify ウィジェット | - |

### Admin (全て `X-Admin-Password` ヘッダー必須)

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/admin/login` | ログイン認証 |
| GET | `/api/admin/articles` | ナレッジ記事一覧 |
| POST | `/api/admin/articles` | 記事作成 |
| PATCH | `/api/admin/articles/{id}` | 記事更新 |
| DELETE | `/api/admin/articles/{id}` | 記事削除 |
| POST | `/api/admin/reingest` | ベクトル DB 再取込み |
| GET | `/api/admin/conversations` | 会話一覧 |
| GET | `/api/admin/conversations/{id}/messages` | メッセージ詳細 |
| GET | `/api/admin/analytics` | 分析データ |

---

## RAG Pipeline (回答生成の流れ)

```
1. ユーザーメッセージ受信
      ↓
2. 挨拶チェック (hello, ありがとう 等)
   → 挨拶なら RAG スキップ → 直接 LLM 回答
      ↓
3. 検索クエリ構築 (会話履歴 2 往復分を付加)
      ↓
4. NVIDIA Embedding API で質問をベクトル化
      ↓
5. ChromaDB でコサイン類似度検索 (上位 10 件取得)
      ↓
6. 関連度フィルタ (距離 < 0.75 のもの → 上位 5 件)
      ↓
7. RAG コンテキスト構築 (チャンク + 質問 + システムプロンプト)
      ↓
8. NVIDIA LLM (Llama 3.3 70B) で回答生成
      ↓
9. レスポンス返却 (回答テキスト + ソース URL)
      ↓
10. 非同期で Supabase にログ保存
```

### Key Parameters

| Parameter | Value | Description |
|-----------|-------|-------------|
| LLM Model | `meta/llama-3.3-70b-instruct` | 70B パラメータ |
| Embedding Model | `nvidia/nv-embedqa-e5-v5` | 1024次元ベクトル |
| Temperature | 0.3 (QA) / 0.5 (挨拶) | 低いほど正確 |
| Max Tokens | 512 (QA) / 256 (挨拶) | 回答の最大長 |
| Chunk Size | 500 words | ドキュメント分割サイズ |
| Chunk Overlap | 50 words | チャンク間のオーバーラップ |
| Relevance Threshold | 0.75 | コサイン距離の閾値 |

---

## Database Schema (Supabase)

### conversations

| Column | Type | Description |
|--------|------|-------------|
| id | UUID PK | 自動生成 |
| session_id | TEXT | ブラウザ匿名 ID |
| source | TEXT | 'pwa' / 'widget' |
| language | TEXT | 'en' / 'ja' |
| user_agent | TEXT | ブラウザ情報 |
| referrer | TEXT | 参照元 URL |
| started_at | TIMESTAMPTZ | 開始時刻 |
| last_message_at | TIMESTAMPTZ | 最終メッセージ (トリガー自動更新) |
| message_count | INTEGER | メッセージ数 (トリガー自動更新) |

### messages

| Column | Type | Description |
|--------|------|-------------|
| id | UUID PK | 自動生成 |
| conversation_id | UUID FK | conversations.id |
| role | TEXT | 'user' / 'assistant' |
| content | TEXT | メッセージ本文 |
| language | TEXT | 言語 |
| sources | TEXT[] | RAG ソース URL |
| context_chunks | INTEGER | 使用チャンク数 |
| response_time_ms | INTEGER | 応答時間 (ms) |
| created_at | TIMESTAMPTZ | 送信時刻 |

### knowledge_articles

| Column | Type | Description |
|--------|------|-------------|
| id | UUID PK | 自動生成 |
| title | TEXT | タイトル |
| slug | TEXT UNIQUE | スラッグ |
| content | TEXT | 記事本文 |
| language | TEXT | 'en' / 'ja' |
| category | TEXT | カテゴリ |
| is_active | BOOLEAN | 有効/無効 |
| sort_order | INTEGER | 並び順 |
| updated_at | TIMESTAMPTZ | 更新日時 (トリガー自動更新) |

---

## Admin Dashboard (/admin)

### ログイン
- URL: https://nakai-matcha-chat.onrender.com/admin
- パスワード: Render の `ADMIN_PASSWORD` 環境変数

### Knowledge Base タブ
- 記事の作成・編集・削除・有効/無効切替
- 言語・カテゴリフィルター
- **「Re-ingest Knowledge」ボタン** → 記事追加/編集後に押すとチャットに反映

### Chat History タブ
- 会話一覧 (セッション ID、ソース、メッセージ数、最終活動)
- 会話クリック → メッセージ詳細表示

### Analytics タブ
- 総会話数 / 総メッセージ数 / 平均メッセージ数
- 過去 7 日間の日別チャート
- ソース別・言語別内訳

---

## Data Ingestion (データ取込み)

### 自動取込み
- サーバー起動時、ベクトル DB が空なら自動実行
- 取込み中も API は使用可能

### 手動取込み
1. **管理画面**: /admin → Knowledge Base → 「Re-ingest Knowledge」ボタン
2. **API**: `POST /api/refresh` + `X-Refresh-Secret` ヘッダー
3. **管理 API**: `POST /api/admin/reingest` + `X-Admin-Password` ヘッダー

### データソース (取込み順序)
1. Shopify 商品 (Storefront API)
2. Shopify コレクション (Storefront API)
3. Shopify ページ (Admin API)
4. Shopify ブログ記事 (Admin API)
5. Shopify ポリシー (Admin API)
6. ローカル .txt ナレッジファイル (`backend/knowledge/`)
7. Supabase ナレッジ記事 (管理画面で追加したもの)

---

## Knowledge Management (ナレッジ管理)

### 2 つの方法でナレッジを追加できる

**方法 1: 管理画面 (推奨)**
1. /admin → Knowledge Base タブ
2. 「New Article」をクリック
3. タイトル・内容・言語・カテゴリを入力
4. 保存
5. 「Re-ingest Knowledge」をクリック
6. チャットで確認

**方法 2: .txt ファイル (開発者向け)**
1. `backend/knowledge/` に .txt ファイルを追加
2. Git push → Render 自動デプロイ
3. データ再取込みを実行

### カテゴリ一覧
- `product` — 商品情報
- `brewing` — 準備・淹れ方
- `recipe` — レシピ
- `faq` — よくある質問
- `science` — 抹茶の科学
- `shipping` — 配送・返品
- `general` — その他

---

## Frontend (フロントエンド)

### PWA (/app)
- デスクトップ: 左サイドバー (ブランドパネル) + メインチャット
- モバイル: フルスクリーン
- ホーム画面: 検索入力 + アクションチップ + 商品カード + レシピカード
- チャット画面: メッセージバブル + タイピングインジケーター + ソースリンク
- 言語切替: EN / JA トグル
- セッション: localStorage に永続化

### Widget (/widget.js)
- Shopify に `<script src="...widget.js" defer></script>` で埋め込み
- フローティングボタン → チャットパネル
- sessionStorage にセッション保持
- ダークモード対応

### デザインシステム
- Primary: `#406546` (抹茶グリーン)
- Secondary: `#F9F0E2` (クリーム)
- Tertiary: `#FFFFFF` (ホワイト)
- Font: Work Sans (Latin) / Shippori Mincho (Japanese)

---

## Deployment (デプロイ)

### 自動デプロイ
- GitHub `main` ブランチに push → Render が自動デプロイ
- ビルド: `pip install -r requirements.txt`
- 起動: `uvicorn main:app --host 0.0.0.0 --port $PORT`

### 手動デプロイが必要な場面
- 環境変数の変更 → Render ダッシュボード > Environment
- DB スキーマ変更 → Supabase SQL Editor で実行

### Python バージョン
- `3.11.11` (render.yaml で指定)

---

## Security (セキュリティ)

| Layer | Method |
|-------|--------|
| Admin API | `X-Admin-Password` ヘッダー |
| Data Refresh | `X-Refresh-Secret` ヘッダー |
| Chat Rate Limit | 20 req/min per IP |
| Refresh Rate Limit | 5 req/hour per IP |
| Supabase | Row Level Security (service_role only) |
| CORS | 全オリジン許可 (`*`) |

---

## Troubleshooting

### チャットが回答しない
1. `/api/health` を確認 → `documents` が 0 なら再取込み実行
2. NVIDIA API キーが有効か確認 (build.nvidia.com)
3. Render ログを確認

### 管理画面にアクセスできない
1. Render の `ADMIN_PASSWORD` が設定されているか確認
2. ブラウザの sessionStorage をクリアして再ログイン

### ナレッジが反映されない
1. 管理画面で記事が「Active」になっているか確認
2. 「Re-ingest Knowledge」を実行
3. `/api/health` で `documents` 数が増えたか確認

### Supabase にデータが入らない
1. Render の `SUPABASE_URL` と `SUPABASE_SERVICE_KEY` が正しいか確認
2. Supabase ダッシュボードで SQL スキーマが実行済みか確認
3. RLS ポリシーが作成されているか確認

### デプロイが失敗する
1. Render ダッシュボード > Deploys でエラーログを確認
2. `requirements.txt` の依存関係に問題がないか確認
3. Python 3.11 で互換性があるか確認

---

## Dependencies

```
fastapi==0.115.0           # Web フレームワーク
uvicorn[standard]==0.30.0  # ASGI サーバー
httpx==0.27.0              # 非同期 HTTP クライアント
chromadb==0.5.0            # ベクトル DB
numpy<2.0                  # 数値計算
pydantic==2.9.0            # データバリデーション
pydantic-settings==2.5.0   # 設定管理
python-dotenv==1.0.1       # 環境変数読み込み
slowapi==0.1.9             # レート制限
```

---

## Quick Reference (よく使う操作)

| やりたいこと | 操作 |
|-------------|------|
| ナレッジ追加 | /admin → Knowledge Base → New Article → 保存 → Re-ingest |
| 会話履歴確認 | /admin → Chat History |
| 分析確認 | /admin → Analytics |
| データ再取込み | /admin → Knowledge Base → Re-ingest Knowledge |
| 環境変数変更 | Render Dashboard → Environment |
| コードデプロイ | `git push origin main` (自動) |
| DB スキーマ変更 | Supabase Dashboard → SQL Editor |
| ヘルスチェック | `curl https://nakai-matcha-chat.onrender.com/api/health` |
