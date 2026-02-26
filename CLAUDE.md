# NAKAI Matcha Chatbot

## Project Overview
NAKAI Matcha Concierge - バリスタと一般消費者向けの AI チャットボットシステム。
RAG (Retrieval-Augmented Generation) を使い、NAKAI の商品・レシピ・抹茶知識に基づいた回答を生成する。

## Tech Stack
- **Backend**: Python 3.11 / FastAPI / Uvicorn
- **AI/LLM**: NVIDIA NIM (Llama 3.3 70B) + ChromaDB (Vector Search)
- **Database**: Supabase (PostgreSQL)
- **Frontend**: PWA (単一 Python ファイルから HTML/CSS/JS を生成) + Shopify Widget
- **Hosting**: Render.com (自動デプロイ: git push → main)
- **Store**: Shopify (nakaimatcha.com)

## Key URLs
- PWA: https://nakai-matcha-chat.onrender.com/app
- Admin: https://nakai-matcha-chat.onrender.com/admin
- Health: https://nakai-matcha-chat.onrender.com/api/health
- GitHub: https://github.com/takahiranakai-ops/nakai-matcha-chatbot

## File Structure
```
backend/
  main.py              # FastAPI アプリ + ルーター登録
  config.py            # 設定 (環境変数)
  requirements.txt     # Python 依存パッケージ
  api/
    routes.py          # /api/chat, /api/health, /api/refresh
    admin_routes.py    # /api/admin/* (Knowledge CRUD, Analytics)
    admin_page.py      # /admin (管理画面 HTML)
    pwa.py             # /app (PWA アプリ HTML/CSS/JS) ← メインの UI
    widget.py          # /widget.js (Shopify ウィジェット)
    models.py          # Pydantic モデル
    middleware.py       # レート制限
  services/
    rag_engine.py      # RAG パイプライン
    vector_store.py    # ChromaDB ラッパー
    nvidia_client.py   # NVIDIA NIM API
    supabase_client.py # Supabase REST API
    shopify_client.py  # Shopify データ取得
    data_processor.py  # ドキュメント処理 (チャンク分割)
    prompt_templates.py # システムプロンプト
  knowledge/           # ナレッジベース .txt ファイル
```

## Design System
- Primary: #406546 (抹茶グリーン)
- Secondary: #F9F0E2 (クリーム)
- Tertiary: #FFFFFF (ホワイト)
- Font: Work Sans (Latin) / Shippori Mincho (Japanese)

## Common Commands
```bash
# ローカル開発
cd /Users/nakai/nakai-matcha-chatbot
pip install -r backend/requirements.txt
uvicorn backend.main:app --reload --port 8000

# デプロイ (自動)
git add <files> && git commit -m "message" && git push origin main

# ヘルスチェック
curl https://nakai-matcha-chat.onrender.com/api/health
```

## Development Notes
- PWA の UI は `backend/api/pwa.py` に HTML/CSS/JS が全て含まれる
- git push → main で Render が自動デプロイ (約3分)
- 環境変数は Render ダッシュボードで管理 (.env.example 参照)
- ナレッジ追加後は Admin の「Re-ingest Knowledge」が必要

## Recent Work
- プライベート抹茶ルーム + フレンド招待システム
- Apple風 UI: セグメントコントロール、カプセルチップ
- 商品カード v2 (140px ビジュアルエリア + グラデーション)
