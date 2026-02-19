-- ============================================================
-- NAKAI Matcha Chatbot — Supabase Schema
-- Run this in Supabase SQL Editor (Dashboard > SQL Editor > New Query)
-- ============================================================

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. CONVERSATIONS
CREATE TABLE conversations (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id      TEXT NOT NULL,
    source          TEXT NOT NULL DEFAULT 'pwa',
    language        TEXT NOT NULL DEFAULT 'en',
    user_agent      TEXT,
    referrer        TEXT,
    started_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_message_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    message_count   INTEGER NOT NULL DEFAULT 0,
    metadata        JSONB DEFAULT '{}'::JSONB
);

CREATE INDEX idx_conversations_session  ON conversations (session_id);
CREATE INDEX idx_conversations_started  ON conversations (started_at DESC);
CREATE INDEX idx_conversations_source   ON conversations (source);
CREATE INDEX idx_conversations_language ON conversations (language);

-- 2. MESSAGES
CREATE TABLE messages (
    id                UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_id   UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    role              TEXT NOT NULL CHECK (role IN ('user', 'assistant')),
    content           TEXT NOT NULL,
    language          TEXT NOT NULL DEFAULT 'en',
    sources           TEXT[] DEFAULT '{}',
    context_chunks    INTEGER DEFAULT 0,
    response_time_ms  INTEGER,
    created_at        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    metadata          JSONB DEFAULT '{}'::JSONB
);

CREATE INDEX idx_messages_conversation ON messages (conversation_id, created_at);
CREATE INDEX idx_messages_created      ON messages (created_at DESC);

-- 3. KNOWLEDGE ARTICLES
CREATE TABLE knowledge_articles (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title       TEXT NOT NULL,
    slug        TEXT NOT NULL UNIQUE,
    content     TEXT NOT NULL,
    language    TEXT NOT NULL DEFAULT 'en',
    category    TEXT NOT NULL DEFAULT 'general',
    is_active   BOOLEAN NOT NULL DEFAULT TRUE,
    sort_order  INTEGER NOT NULL DEFAULT 0,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_knowledge_active   ON knowledge_articles (is_active, language);
CREATE INDEX idx_knowledge_category ON knowledge_articles (category);

-- 4. ROW LEVEL SECURITY
ALTER TABLE conversations     ENABLE ROW LEVEL SECURITY;
ALTER TABLE messages           ENABLE ROW LEVEL SECURITY;
ALTER TABLE knowledge_articles ENABLE ROW LEVEL SECURITY;

CREATE POLICY "service_role_conversations" ON conversations
    FOR ALL USING (auth.role() = 'service_role');
CREATE POLICY "service_role_messages" ON messages
    FOR ALL USING (auth.role() = 'service_role');
CREATE POLICY "service_role_knowledge" ON knowledge_articles
    FOR ALL USING (auth.role() = 'service_role');

-- 5. AUTO-UPDATE conversation stats on message insert
CREATE OR REPLACE FUNCTION update_conversation_stats()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE conversations
    SET last_message_at = NEW.created_at,
        message_count = message_count + 1
    WHERE id = NEW.conversation_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_update_conversation_stats
    AFTER INSERT ON messages
    FOR EACH ROW
    EXECUTE FUNCTION update_conversation_stats();

-- 6. AUTO-UPDATE updated_at on knowledge_articles
CREATE OR REPLACE FUNCTION update_modified_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_knowledge_updated
    BEFORE UPDATE ON knowledge_articles
    FOR EACH ROW
    EXECUTE FUNCTION update_modified_column();
