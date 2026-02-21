import logging
import re
from typing import Optional, List, Dict

from services.nvidia_client import get_embeddings, chat_completion, chat_completion_stream
from services.vector_store import VectorStore
from services.prompt_templates import build_system_prompt, build_rag_prompt
from config import settings

logger = logging.getLogger(__name__)

# Simple greetings and small talk — no RAG needed
_GREETING_RE = re.compile(
    r"^(h[ae]llo|hi|hey|yo|sup|good\s*(morning|afternoon|evening|night)"
    r"|こんにちは|こんばんは|おはよう|はじめまして|ハロー|ハイ|やあ"
    r"|ありがとう|thank|thanks|どうも|よろしく)[\s!?。！？]*$",
    re.IGNORECASE,
)

# Extract [SUGGESTIONS]...[/SUGGESTIONS] from response (closing tag optional)
# Permissive: handles **[SUGGESTIONS]**, whitespace, missing closing tag
_SUGGESTIONS_RE = re.compile(
    r"\*{0,2}\[SUGGESTIONS\]\*{0,2}\s*\n(.*?)(?:\n?\*{0,2}\[/SUGGESTIONS\]\*{0,2}|$)",
    re.DOTALL,
)

# Cosine distance threshold — lower = stricter, higher = more permissive
_RELEVANCE_THRESHOLD = 0.82

# Retrieve extra candidates for better filtering
_RETRIEVAL_MULTIPLIER = 2


# Strip common LLM prefixes from suggestion lines
_SUGGESTION_PREFIX_RE = re.compile(
    r"^(?:(?:Suggestion|提案|Q)\s*\**\d*\**\s*[:：]\s*)?(?:\*\*)?(.+?)(?:\*\*)?$"
)


def _parse_suggestions(response: str) -> tuple[str, list[str]]:
    """Extract follow-up suggestions from the LLM response.
    Returns (clean_response, suggestions_list)."""
    match = _SUGGESTIONS_RE.search(response)
    if not match:
        return response.strip(), []

    suggestions_text = match.group(1).strip()
    suggestions = []
    for line in suggestions_text.split("\n"):
        line = line.strip().lstrip("0123456789.-) ・•")
        if not line:
            continue
        # Strip "Suggestion **1**: ..." or "提案1: ..." prefixes
        m = _SUGGESTION_PREFIX_RE.match(line)
        if m:
            line = m.group(1).strip()
        # Remove any remaining bold markers
        line = line.replace("**", "")
        if line:
            suggestions.append(line)
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

        Uses both user and assistant messages so follow-up questions like
        "How about the other one?" carry the full topical context into
        the embedding.
        """
        if not conversation_history:
            return user_message

        # Collect the last 3 exchanges for rich multi-turn context
        recent = conversation_history[-6:]
        context_parts = []
        for msg in recent:
            role = msg.get("role", "")
            content = msg.get("content", "")
            if role == "user":
                context_parts.append(content)
            elif role == "assistant" and len(content) < 300:
                # Include shorter assistant responses for topic context
                context_parts.append(content)
        # Append current question
        context_parts.append(user_message)
        return " ".join(context_parts)

    async def answer(
        self,
        user_message: str,
        conversation_history: Optional[List[Dict]] = None,
        language: str = "en",
        source: str = "pwa",
    ) -> dict:
        system_prompt = build_system_prompt(language=language, source=source)
        msg_stripped = user_message.strip()

        # For greetings / small talk, skip RAG entirely (faster + more natural)
        if _GREETING_RE.match(msg_stripped):
            messages = [{"role": "system", "content": system_prompt}]
            if conversation_history:
                messages.extend(conversation_history[-6:])
            messages.append({"role": "user", "content": msg_stripped})
            response = await chat_completion(
                messages, temperature=0.6, max_tokens=80, language=language
            )
            # Truncate after the first question mark to keep greetings short
            for end_char in ("？", "?"):
                idx = response.find(end_char)
                if idx != -1:
                    response = response[: idx + 1]
                    break
            return {
                "response": response.strip(),
                "sources": [],
                "context_chunks": 0,
                "suggestions": [],
            }

        # 1. Build enriched search query using conversation context
        search_query = self._build_search_query(msg_stripped, conversation_history)

        _error_result = {
            "response": "I'm sorry, I'm having trouble processing your request right now. Please try again in a moment.",
            "sources": [], "context_chunks": 0, "suggestions": [],
        }

        # 2. Embed the search query
        try:
            query_embeddings = await get_embeddings([search_query], input_type="query")
            query_embedding = query_embeddings[0]
        except Exception as e:
            logger.error(f"Embedding generation failed: {e}")
            return _error_result

        # 3. Retrieve extra candidates for better filtering
        n_retrieve = min(
            settings.max_context_chunks * _RETRIEVAL_MULTIPLIER,
            max(self.vector_store.count(), 1),
        )
        try:
            results = self.vector_store.query(
                query_embedding=query_embedding,
                n_results=max(n_retrieve, 1),
            )
        except Exception as e:
            logger.error(f"Vector store query failed: {e}")
            results = []

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
                context=context, question=user_message, language=language,
                source=source,
            )
        else:
            rag_context = build_rag_prompt(
                context="", question=user_message, language=language,
                source=source,
            )

        messages = [{"role": "system", "content": system_prompt}]
        if conversation_history:
            # Include more history for better multi-turn understanding
            messages.extend(conversation_history[-8:])
        messages.append({"role": "user", "content": rag_context})

        # 6. Generate response with tuned parameters
        try:
            raw_response = await chat_completion(
                messages, temperature=0.45, max_tokens=800, language=language
            )
        except Exception as e:
            logger.error(f"Chat completion failed: {e}")
            return _error_result

        # 7. Parse out follow-up suggestions
        response, suggestions = _parse_suggestions(raw_response)

        return {
            "response": response,
            "sources": list(source_urls),
            "context_chunks": len(context_texts),
            "suggestions": suggestions,
        }

    async def answer_stream(
        self,
        user_message: str,
        conversation_history: Optional[List[Dict]] = None,
        language: str = "en",
        source: str = "pwa",
    ):
        """Yield (event_type, data) tuples for SSE streaming."""
        system_prompt = build_system_prompt(language=language, source=source)
        msg_stripped = user_message.strip()

        # Greetings — skip RAG, non-streaming (fast enough)
        if _GREETING_RE.match(msg_stripped):
            messages = [{"role": "system", "content": system_prompt}]
            if conversation_history:
                messages.extend(conversation_history[-6:])
            messages.append({"role": "user", "content": msg_stripped})
            response = await chat_completion(
                messages, temperature=0.6, max_tokens=80, language=language
            )
            for end_char in ("\uff1f", "?"):
                idx = response.find(end_char)
                if idx != -1:
                    response = response[: idx + 1]
                    break
            yield ("text", response.strip())
            yield ("done", {"sources": [], "suggestions": []})
            return

        # 1-4: Same RAG retrieval as non-streaming
        search_query = self._build_search_query(msg_stripped, conversation_history)
        try:
            query_embeddings = await get_embeddings([search_query], input_type="query")
            query_embedding = query_embeddings[0]
        except Exception as e:
            logger.error(f"Streaming embedding failed: {e}")
            yield ("text", "I'm sorry, I'm having trouble right now. Please try again.")
            yield ("done", {"sources": [], "suggestions": []})
            return

        n_retrieve = min(
            settings.max_context_chunks * _RETRIEVAL_MULTIPLIER,
            max(self.vector_store.count(), 1),
        )
        try:
            results = self.vector_store.query(
                query_embedding=query_embedding,
                n_results=max(n_retrieve, 1),
            )
        except Exception as e:
            logger.error(f"Streaming vector query failed: {e}")
            results = []

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

        if context_texts:
            context = "\n---\n".join(context_texts)
            rag_context = build_rag_prompt(
                context=context, question=user_message, language=language,
                source=source,
            )
        else:
            rag_context = build_rag_prompt(
                context="", question=user_message, language=language,
                source=source,
            )

        messages = [{"role": "system", "content": system_prompt}]
        if conversation_history:
            messages.extend(conversation_history[-8:])
        messages.append({"role": "user", "content": rag_context})

        # 5. Stream LLM response
        full_response = []
        try:
            async for chunk in chat_completion_stream(
                messages, temperature=0.45, max_tokens=800, language=language
            ):
                full_response.append(chunk)
                yield ("text", chunk)
        except Exception as e:
            logger.error(f"Streaming chat completion failed: {e}")
            if not full_response:
                yield ("text", "I'm sorry, I'm having trouble right now. Please try again.")
            yield ("done", {"sources": list(source_urls), "suggestions": []})
            return

        # 6. Parse suggestions from full response
        raw = "".join(full_response)
        _, suggestions = _parse_suggestions(raw)

        yield ("done", {
            "sources": list(source_urls),
            "suggestions": suggestions,
        })
