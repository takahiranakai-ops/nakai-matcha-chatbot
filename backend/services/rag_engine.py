import logging
import random
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

# Pre-written greetings — instant, no LLM call needed
_INSTANT_GREETINGS_EN = [
    "Hey there! Whether you're curious about matcha or ready to find your perfect cup, I'm here for it. What's on your mind?",
    "Welcome! Matcha has this way of turning ordinary moments into something special. How can I help you today?",
    "Hi! Ready to explore the world of matcha? Ask me anything — from brewing tips to finding your perfect match.",
]
_INSTANT_GREETINGS_JA = [
    "ようこそ！抹茶の世界を一緒に楽しみましょう。何でもお気軽にどうぞ。",
    "こんにちは！あなたにぴったりの一杯を一緒に見つけましょう。どんなことが気になりますか？",
    "いらっしゃいませ！淹れ方から商品選びまで、何でもお聞きください。",
]
_INSTANT_THANKS_EN = [
    "You're welcome! Anything else about matcha I can help with?",
]
_INSTANT_THANKS_JA = [
    "こちらこそ！他にも気になることがあればお気軽にどうぞ。",
]

_THANKS_RE = re.compile(
    r"^(ありがとう|thank|thanks|どうも)[\s!?。！？]*$",
    re.IGNORECASE,
)

# Extract [SUGGESTIONS]...[/SUGGESTIONS] from response (closing tag optional)
# Permissive: handles **[SUGGESTIONS]**, whitespace, missing closing tag
_SUGGESTIONS_RE = re.compile(
    r"\*{0,2}\[SUGGESTIONS\]\*{0,2}\s*\n(.*?)(?:\n?\*{0,2}\[/SUGGESTIONS\]\*{0,2}|$)",
    re.DOTALL,
)

# WS22: B2B Lead tag extraction
_B2B_LEAD_RE = re.compile(r"\[B2B_LEAD\](.*?)\[/B2B_LEAD\]", re.DOTALL)

# Detect Matcha Finder mid-flow: assistant's last message had [CHOICES]
_CHOICES_RE = re.compile(r"\[CHOICES\]")

# Detect a NEW recommendation/matcha-finder start request
# (as opposed to a short step answer like "Totally new" or "ラテ")
_RECOMMENDATION_START_RE = re.compile(
    r"(find.*(matcha|right one)|recommend|help me (choose|pick|find)|which matcha|"
    r"what matcha.*(should|for me|best)|best matcha|right matcha|matcha finder|"
    r"おすすめ|探し|選んで|合った抹茶|どの抹茶|どれがいい|ぴったり)",
    re.IGNORECASE,
)

# Product name → Shopify handle mapping for [PRODUCT] tag injection
_PRODUCT_HANDLE_MAP = {
    "四": "shi-4",
    "shi": "shi-4",
    "十六": "ju-roku-16",
    "ju-roku": "ju-roku-16",
    "十七": "ju-nana-17",
    "ju-nana": "ju-nana-17",
    "十八": "ju-hachi-18",
    "ju-hachi": "ju-hachi-18",
    "二十二": "nijyu-ni-22",
    "nijyu-ni": "nijyu-ni-22",
    "discovery bundle": "discovery-bundle",
    "everyday": "the-everyday",
    "signature reserve": "expert-set",
    "hiragoushi": "hiragoushi-chawan",
    "yagoushi": "yagoushi-chawan",
    "chasen": "takayama-chasen-100",
    "茶筅": "takayama-chasen-100",
}
_PRODUCT_TAG_RE = re.compile(r"\[PRODUCT:[a-z0-9-]+\]", re.IGNORECASE)

# Topic → product mapping: certain topics always show specific products
_LATTE_RE = re.compile(r"(latte|ラテ|matcha latte|抹茶ラテ)", re.IGNORECASE)
_TOPIC_PRODUCT_MAP = [
    (_LATTE_RE, ["nijyu-ni-22"]),
]

# Extra context injected for topic-matched queries so the LLM explains WHY
_TOPIC_CONTEXT = {
    "latte": {
        "en": (
            "NAKAI RECOMMENDATION FOR LATTES: 二十二 NIJYU-NI (22) is NAKAI's top pick for matcha lattes. "
            "Its rich, creamy umami and natural sweetness pair beautifully with milk — the flavor stays vivid "
            "and doesn't get lost. The vibrant jade color shines through oat or whole milk, "
            "and the ultra-fine stone-ground particle size (5-10μm) means it dissolves smoothly with zero grittiness. "
            "ALWAYS recommend 二十二 for lattes and explain why it's the best choice."
        ),
        "ja": (
            "NAKAIのラテ推薦：ラテには二十二 NIJYU-NI（22）が最適。"
            "豊かなクリーミーな旨みと自然な甘みがミルクと美しく調和し、味がぼやけない。"
            "鮮やかな翡翠色がオーツミルクでも全乳でも映え、"
            "超微粒子の石臼挽き（5-10μm）でダマなく滑らかに溶ける。"
            "ラテの質問には必ず二十二を推薦し、なぜ最適かを説明すること。"
        ),
    },
}


def _inject_product_tags(
    response: str,
    conversation_history: Optional[List[Dict]] = None,
    user_message: str = "",
) -> str:
    """If the model mentioned a product but didn't output [PRODUCT:handle]
    tags, inject them automatically. Works for ALL responses — not just
    Matcha Finder step 3 — so product cards always appear.
    Also injects topic-based products (e.g. latte → nijyu-ni-22)."""
    # Collect handles from [PRODUCT] tags already present
    existing_tags = set(m.group(0).lower() for m in _PRODUCT_TAG_RE.finditer(response))

    # Topic-based injection takes priority: if matched, use ONLY topic products
    topic_matched = False
    handles = []
    if user_message:
        for pattern, topic_handles in _TOPIC_PRODUCT_MAP:
            if pattern.search(user_message):
                topic_matched = True
                for h in topic_handles:
                    if h not in handles:
                        handles.append(h)

    # Fall back to name-based detection only if no topic matched
    if not topic_matched:
        lower = response.lower()
        for name, handle in _PRODUCT_HANDLE_MAP.items():
            if name in lower and handle not in handles:
                handles.append(handle)

    # Filter out handles already present as [PRODUCT] tags
    handles = [h for h in handles if f"[product:{h}]" not in existing_tags]

    if handles:
        tags = "\n".join(f"[PRODUCT:{h}]" for h in handles)
        response = response.rstrip() + "\n" + tags
    return response


_CHOICES_BLOCK_RE = re.compile(r"\s*\*{0,2}\[CHOICES\]\*{0,2}.*?\*{0,2}\[/CHOICES\]\*{0,2}\s*", re.DOTALL)
_SUGGESTIONS_BLOCK_RE = re.compile(r"\s*\*{0,2}\[SUGGESTIONS\]\*{0,2}.*?(?:\*{0,2}\[/SUGGESTIONS\]\*{0,2}|$)", re.DOTALL)


def _choices_to_text(match: re.Match) -> str:
    """Convert [CHOICES]a|b|c[/CHOICES] to plain text options."""
    inner = match.group(0)
    # Extract the pipe-separated options
    m = re.search(r"\[CHOICES\]\*{0,2}\s*(.*?)\s*\*{0,2}\[/CHOICES\]", inner, re.DOTALL)
    if m:
        options = [o.strip() for o in m.group(1).split("|") if o.strip()]
        return "\n(Options: " + " / ".join(options) + ")"
    return ""


def _clean_history_for_llm(conversation_history: Optional[List[Dict]]) -> List[Dict]:
    """Replace [CHOICES]/[SUGGESTIONS] blocks in history with plain text
    to preserve context while preventing the model from echoing tags."""
    if not conversation_history:
        return []
    cleaned = []
    for msg in conversation_history:
        content = msg.get("content", "")
        role = msg.get("role", "")
        if role == "assistant":
            content = _CHOICES_BLOCK_RE.sub(_choices_to_text, content)
            content = _SUGGESTIONS_BLOCK_RE.sub("", content)
            content = content.strip()
        cleaned.append({"role": role, "content": content})
    return cleaned


def _matcha_finder_step(conversation_history: Optional[List[Dict]], current_message: str = "") -> int:
    """Return the current Matcha Finder step (0 if not in flow, 1-3 otherwise).
    If current_message is a new recommendation request, treat as fresh start (0)."""
    if not conversation_history:
        return 0
    choices_count = sum(
        1 for msg in conversation_history
        if msg.get("role") == "assistant" and _CHOICES_RE.search(msg.get("content", ""))
    )
    if choices_count == 0:
        return 0
    # If user is starting a NEW recommendation request, reset the flow
    if current_message and _RECOMMENDATION_START_RE.search(current_message):
        return 0
    return choices_count + 1  # 1 CHOICES = step 2, 2 CHOICES = step 3


def _is_matcha_finder_mid_flow(conversation_history: Optional[List[Dict]], current_message: str = "") -> bool:
    """Return True only when exactly 1 [CHOICES] exchange has occurred
    (step 1 answered, step 2 question needed). When 2+ [CHOICES] have
    been sent, the model should recommend a product using RAG data.
    Returns False if current_message is a new recommendation request."""
    if not conversation_history:
        return False
    # If user is restarting the flow, don't treat as mid-flow
    if current_message and _RECOMMENDATION_START_RE.search(current_message):
        return False
    choices_count = sum(
        1 for msg in conversation_history
        if msg.get("role") == "assistant" and _CHOICES_RE.search(msg.get("content", ""))
    )
    # Skip RAG only when exactly 1 CHOICES exchange — need step 2 question
    return choices_count == 1


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


def _extract_b2b_lead(response: str) -> tuple[str, Optional[dict]]:
    """Extract [B2B_LEAD] tag from response.
    Returns (clean_response, lead_data_or_None)."""
    match = _B2B_LEAD_RE.search(response)
    if not match:
        return response, None
    parts = match.group(1).strip().split("|")
    lead = {
        "business_type": parts[0].strip() if len(parts) > 0 else "",
        "volume": parts[1].strip() if len(parts) > 1 else "",
        "notes": parts[2].strip() if len(parts) > 2 else "",
    }
    clean = response[:match.start()] + response[match.end():]
    return clean.strip(), lead


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

        # For greetings / small talk — instant pre-written response, no LLM needed
        if _GREETING_RE.match(msg_stripped):
            if _THANKS_RE.match(msg_stripped):
                pool = _INSTANT_THANKS_JA if language == "ja" else _INSTANT_THANKS_EN
            else:
                pool = _INSTANT_GREETINGS_JA if language == "ja" else _INSTANT_GREETINGS_EN
            return {
                "response": random.choice(pool),
                "sources": [],
                "context_chunks": 0,
                "suggestions": [],
            }

        # Matcha Finder mid-flow: skip RAG so model follows step flow
        if _is_matcha_finder_mid_flow(conversation_history, msg_stripped):
            messages = [{"role": "system", "content": system_prompt}]
            if conversation_history:
                messages.extend(_clean_history_for_llm(conversation_history[-8:]))
            messages.append({"role": "user", "content": msg_stripped})
            try:
                raw_response = await chat_completion(
                    messages, temperature=0.45, max_tokens=900, language=language
                )
            except Exception as e:
                logger.error(f"Matcha Finder chat completion failed: {e}")
                return {
                    "response": "I'm sorry, I'm having trouble right now. Please try again.",
                    "sources": [], "context_chunks": 0, "suggestions": [],
                }
            response, suggestions = _parse_suggestions(raw_response)
            return {
                "response": response,
                "sources": [],
                "context_chunks": 0,
                "suggestions": suggestions,
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
        # Wholesale product queries need more context for comprehensive specs
        _max_chunks = 10 if "wholesale" in source else settings.max_context_chunks
        n_retrieve = min(
            _max_chunks * _RETRIEVAL_MULTIPLIER,
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
            if len(context_texts) >= _max_chunks:
                break
            context_texts.append(result["text"])
            url = result["metadata"].get("url")
            if url:
                source_urls.add(url)

        logger.info(
            "RAG retrieval [%s/%s]: %d candidates -> %d chunks (max=%d, threshold=%.2f)",
            source, language, len(results), len(context_texts),
            _max_chunks, _RELEVANCE_THRESHOLD,
        )
        if "wholesale" in source and context_texts:
            for i, ct in enumerate(context_texts):
                logger.info("  chunk %d (%d chars): %.80s...", i, len(ct), ct.replace("\n", " "))

        # 5. Inject topic-specific context (e.g. latte → 二十二 recommendation)
        if _LATTE_RE.search(msg_stripped):
            lang_key = "ja" if language == "ja" else "en"
            context_texts.insert(0, _TOPIC_CONTEXT["latte"][lang_key])

        # 6. Build messages — always use RAG prompt format
        mf_step = _matcha_finder_step(conversation_history, msg_stripped)
        if context_texts:
            context = "\n---\n".join(context_texts)
            rag_context = build_rag_prompt(
                context=context, question=user_message, language=language,
                source=source, matcha_finder_step=mf_step,
            )
        else:
            rag_context = build_rag_prompt(
                context="", question=user_message, language=language,
                source=source, matcha_finder_step=mf_step,
            )

        messages = [{"role": "system", "content": system_prompt}]
        if conversation_history:
            # Clean [CHOICES]/[SUGGESTIONS] from history to prevent echoing
            messages.extend(_clean_history_for_llm(conversation_history[-8:]))
        messages.append({"role": "user", "content": rag_context})

        # 7. Generate response with tuned parameters
        _max_tok = 1200 if "wholesale" in source else 800
        try:
            raw_response = await chat_completion(
                messages, temperature=0.45, max_tokens=_max_tok, language=language
            )
        except Exception as e:
            logger.error(f"Chat completion failed: {e}")
            return _error_result

        # 7. Parse out follow-up suggestions
        response, suggestions = _parse_suggestions(raw_response)

        # 7b. Extract B2B lead data if present (WS22)
        response, b2b_lead = _extract_b2b_lead(response)
        if b2b_lead:
            logger.info(f"B2B lead captured: {b2b_lead}")

        # 8. Inject [PRODUCT] tags for Matcha Finder step 3 + topic-based
        response = _inject_product_tags(response, conversation_history, user_message=msg_stripped)

        return {
            "response": response,
            "sources": list(source_urls),
            "context_chunks": len(context_texts),
            "suggestions": suggestions,
            "b2b_lead": b2b_lead,
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

        # Greetings — instant pre-written response, no LLM needed
        if _GREETING_RE.match(msg_stripped):
            if _THANKS_RE.match(msg_stripped):
                pool = _INSTANT_THANKS_JA if language == "ja" else _INSTANT_THANKS_EN
            else:
                pool = _INSTANT_GREETINGS_JA if language == "ja" else _INSTANT_GREETINGS_EN
            yield ("text", random.choice(pool))
            yield ("done", {"sources": [], "suggestions": []})
            return

        # Matcha Finder mid-flow: skip RAG, stream directly
        if _is_matcha_finder_mid_flow(conversation_history, msg_stripped):
            messages = [{"role": "system", "content": system_prompt}]
            if conversation_history:
                messages.extend(_clean_history_for_llm(conversation_history[-8:]))
            messages.append({"role": "user", "content": msg_stripped})
            full_response = []
            try:
                async for chunk in chat_completion_stream(
                    messages, temperature=0.45, max_tokens=900, language=language
                ):
                    full_response.append(chunk)
                    yield ("text", chunk)
            except Exception as e:
                logger.error(f"Matcha Finder streaming failed: {e}")
                if not full_response:
                    yield ("text", "I'm sorry, I'm having trouble right now. Please try again.")
                yield ("done", {"sources": [], "suggestions": []})
                return
            raw = "".join(full_response)
            _, suggestions = _parse_suggestions(raw)
            yield ("done", {"sources": [], "suggestions": suggestions})
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

        _max_chunks = 10 if "wholesale" in source else settings.max_context_chunks
        n_retrieve = min(
            _max_chunks * _RETRIEVAL_MULTIPLIER,
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
            if len(context_texts) >= _max_chunks:
                break
            context_texts.append(result["text"])
            url = result["metadata"].get("url")
            if url:
                source_urls.add(url)

        logger.info(
            "RAG stream [%s/%s]: %d candidates -> %d chunks (max=%d)",
            source, language, len(results), len(context_texts), _max_chunks,
        )

        # Inject topic-specific context (e.g. latte → 二十二 recommendation)
        if _LATTE_RE.search(msg_stripped):
            lang_key = "ja" if language == "ja" else "en"
            context_texts.insert(0, _TOPIC_CONTEXT["latte"][lang_key])

        mf_step = _matcha_finder_step(conversation_history, msg_stripped)
        if context_texts:
            context = "\n---\n".join(context_texts)
            rag_context = build_rag_prompt(
                context=context, question=user_message, language=language,
                source=source, matcha_finder_step=mf_step,
            )
        else:
            rag_context = build_rag_prompt(
                context="", question=user_message, language=language,
                source=source, matcha_finder_step=mf_step,
            )

        messages = [{"role": "system", "content": system_prompt}]
        if conversation_history:
            messages.extend(_clean_history_for_llm(conversation_history[-8:]))
        messages.append({"role": "user", "content": rag_context})

        # 5. Stream LLM response
        _max_tok = 1200 if "wholesale" in source else 800
        full_response = []
        try:
            async for chunk in chat_completion_stream(
                messages, temperature=0.45, max_tokens=_max_tok, language=language
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

        # 6b. Extract B2B lead data if present (WS22)
        raw, b2b_lead = _extract_b2b_lead(raw)
        if b2b_lead:
            logger.info(f"B2B lead captured (stream): {b2b_lead}")

        # 7. Inject [PRODUCT] tags for Matcha Finder step 3 + topic-based
        injected = _inject_product_tags(raw, conversation_history, user_message=msg_stripped)
        if injected != raw:
            # Emit the product tags as additional text so frontend can parse them
            extra = injected[len(raw):]
            if extra:
                yield ("text", extra)

        yield ("done", {
            "sources": list(source_urls),
            "suggestions": suggestions,
        })
