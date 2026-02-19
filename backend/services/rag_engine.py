import re
from typing import Optional, List, Dict

from services.nvidia_client import get_embeddings, chat_completion
from services.vector_store import VectorStore
from services.prompt_templates import build_system_prompt, build_rag_prompt
from config import settings

# Simple greetings and small talk — no RAG needed
_GREETING_RE = re.compile(
    r"^(h[ae]llo|hi|hey|yo|sup|good\s*(morning|afternoon|evening|night)"
    r"|こんにちは|こんばんは|おはよう|はじめまして|ハロー|ハイ|やあ"
    r"|ありがとう|thank|thanks|どうも|よろしく)[\s!?。！？]*$",
    re.IGNORECASE,
)

# Cosine distance threshold — higher distance = less relevant
_RELEVANCE_THRESHOLD = 0.75

# Retrieve extra candidates for better filtering
_RETRIEVAL_MULTIPLIER = 2


class RAGEngine:
    def __init__(self, vector_store: VectorStore):
        self.vector_store = vector_store

    def _build_search_query(
        self,
        user_message: str,
        conversation_history: Optional[List[Dict]] = None,
    ) -> str:
        """Enrich the search query with recent conversation context.

        For follow-up questions like "How about the other one?" or "もう一つは？",
        the raw message alone won't retrieve useful results. By prepending
        the last few exchanges, the embedding captures the real intent.
        """
        if not conversation_history:
            return user_message

        # Collect the last 2 exchanges (user + assistant) for context
        recent = conversation_history[-4:]
        context_parts = []
        for msg in recent:
            if msg.get("role") == "user":
                context_parts.append(msg.get("content", ""))
        # Append current question
        context_parts.append(user_message)
        return " ".join(context_parts)

    async def answer(
        self,
        user_message: str,
        conversation_history: Optional[List[Dict]] = None,
        language: str = "en",
    ) -> dict:
        system_prompt = build_system_prompt(language=language)
        msg_stripped = user_message.strip()

        # For greetings / small talk, skip RAG entirely (faster + more natural)
        if _GREETING_RE.match(msg_stripped):
            messages = [{"role": "system", "content": system_prompt}]
            if conversation_history:
                messages.extend(conversation_history[-6:])
            messages.append({"role": "user", "content": msg_stripped})
            response = await chat_completion(messages, temperature=0.5, max_tokens=256)
            return {"response": response, "sources": []}

        # 1. Build enriched search query using conversation context
        search_query = self._build_search_query(msg_stripped, conversation_history)

        # 2. Embed the search query
        query_embeddings = await get_embeddings([search_query], input_type="query")
        query_embedding = query_embeddings[0]

        # 3. Retrieve extra candidates for better filtering
        n_retrieve = min(
            settings.max_context_chunks * _RETRIEVAL_MULTIPLIER,
            self.vector_store.count(),
        )
        results = self.vector_store.query(
            query_embedding=query_embedding,
            n_results=max(n_retrieve, 1),
        )

        # 4. Filter by relevance and limit to max_context_chunks
        context_texts = []
        source_urls = set()
        for result in results:
            if result["distance"] > _RELEVANCE_THRESHOLD:
                continue
            if len(context_texts) >= settings.max_context_chunks:
                break
            context_texts.append(result["text"])
            url = result["metadata"].get("url")
            if url:
                source_urls.add(url)

        # 5. Build messages
        if context_texts:
            context = "\n---\n".join(context_texts)
            rag_context = build_rag_prompt(context=context, question=user_message)
        else:
            rag_context = user_message

        messages = [{"role": "system", "content": system_prompt}]
        if conversation_history:
            messages.extend(conversation_history[-6:])
        messages.append({"role": "user", "content": rag_context})

        # 6. Generate response
        response = await chat_completion(messages, temperature=0.3, max_tokens=512)

        return {
            "response": response,
            "sources": list(source_urls),
        }
