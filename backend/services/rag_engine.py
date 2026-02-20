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

# Extract [SUGGESTIONS]...[/SUGGESTIONS] from response
_SUGGESTIONS_RE = re.compile(
    r"\[SUGGESTIONS\]\s*\n(.*?)\n?\[/SUGGESTIONS\]",
    re.DOTALL,
)

# Cosine distance threshold — lower = stricter, higher = more permissive
_RELEVANCE_THRESHOLD = 0.80

# Retrieve extra candidates for better filtering
_RETRIEVAL_MULTIPLIER = 3


def _parse_suggestions(response: str) -> tuple[str, list[str]]:
    """Extract follow-up suggestions from the LLM response.
    Returns (clean_response, suggestions_list)."""
    match = _SUGGESTIONS_RE.search(response)
    if not match:
        return response.strip(), []

    suggestions_text = match.group(1).strip()
    suggestions = [
        line.strip().lstrip("0123456789.-) ")
        for line in suggestions_text.split("\n")
        if line.strip()
    ]
    clean = response[: match.start()].strip()
    return clean, suggestions[:3]


class RAGEngine:
    def __init__(self, vector_store: VectorStore):
        self.vector_store = vector_store

    def _build_search_query(
        self,
        user_message: str,
        conversation_history: Optional[List[Dict]] = None,
    ) -> str:
        """Enrich the search query with recent conversation context.

        Includes both user and assistant messages for better follow-up
        question handling. For "How about the other one?" or "もう一つは？",
        the assistant context helps the embedding capture the real intent.
        """
        if not conversation_history:
            return user_message

        # Collect the last 2 exchanges (user + assistant) for richer context
        recent = conversation_history[-4:]
        context_parts = []
        for msg in recent:
            role = msg.get("role", "")
            content = msg.get("content", "")
            if role == "user":
                context_parts.append(content)
            elif role == "assistant" and len(content) < 200:
                # Include short assistant responses for topic context
                context_parts.append(content)
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
            return {
                "response": response,
                "sources": [],
                "context_chunks": 0,
                "suggestions": [],
            }

        # 1. Build enriched search query using conversation context
        search_query = self._build_search_query(msg_stripped, conversation_history)

        # 2. Embed the search query
        query_embeddings = await get_embeddings([search_query], input_type="query")
        query_embedding = query_embeddings[0]

        # 3. Retrieve extra candidates for better filtering
        n_retrieve = min(
            settings.max_context_chunks * _RETRIEVAL_MULTIPLIER,
            max(self.vector_store.count(), 1),
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

        # 5. Build messages — always use RAG prompt format
        if context_texts:
            context = "\n---\n".join(context_texts)
            rag_context = build_rag_prompt(
                context=context, question=user_message, language=language
            )
        else:
            rag_context = build_rag_prompt(
                context="", question=user_message, language=language
            )

        messages = [{"role": "system", "content": system_prompt}]
        if conversation_history:
            messages.extend(conversation_history[-6:])
        messages.append({"role": "user", "content": rag_context})

        # 6. Generate response
        raw_response = await chat_completion(
            messages, temperature=0.3, max_tokens=1024
        )

        # 7. Parse out follow-up suggestions
        response, suggestions = _parse_suggestions(raw_response)

        return {
            "response": response,
            "sources": list(source_urls),
            "context_chunks": len(context_texts),
            "suggestions": suggestions,
        }
