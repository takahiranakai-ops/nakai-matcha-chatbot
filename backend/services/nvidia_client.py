import json as _json
import logging
import re

import httpx

from config import settings

logger = logging.getLogger(__name__)

# Strip <think>...</think> blocks from reasoning models (also unclosed)
_THINK_RE = re.compile(r"<think>.*?</think>\s*", re.DOTALL)
_THINK_UNCLOSED_RE = re.compile(r"<think>.*", re.DOTALL)

# ── Shared HTTP client ──────────────────────────────────────
_client: httpx.AsyncClient | None = None


def _get_client() -> httpx.AsyncClient:
    global _client
    if _client is None or _client.is_closed:
        _client = httpx.AsyncClient(timeout=httpx.Timeout(120.0, connect=10.0))
    return _client


async def close():
    global _client
    if _client and not _client.is_closed:
        await _client.aclose()
        _client = None


def _headers() -> dict:
    return {
        "Authorization": f"Bearer {settings.ngc_api_key}",
        "Content-Type": "application/json",
    }


async def get_embeddings(
    texts: list[str], input_type: str = "query"
) -> list[list[float]]:
    """Get embeddings from NVIDIA NIM embedding model."""
    results = []
    batch_size = 50
    client = _get_client()
    for i in range(0, len(texts), batch_size):
        batch = texts[i : i + batch_size]
        try:
            response = await client.post(
                f"{settings.nvidia_base_url}/embeddings",
                headers=_headers(),
                json={
                    "model": settings.nvidia_embed_model,
                    "input": batch,
                    "input_type": input_type,
                    "encoding_format": "float",
                    "truncate": "END",
                },
                timeout=60.0,
            )
            response.raise_for_status()
        except httpx.TimeoutException as exc:
            raise RuntimeError("Embedding service timed out. Please try again.") from exc
        except httpx.HTTPStatusError as exc:
            raise RuntimeError(f"Embedding service error: {exc.response.status_code}") from exc
        data = response.json()
        results.extend([item["embedding"] for item in data["data"]])
    return results


# Common Nemotron CJK tokenization errors → correct forms
_JA_FIXES = [
    ("抹ちゃ", "抹茶"), ("まっちゃ", "抹茶"),
    ("抹cha", "抹茶"), ("抹 cha", "抹茶"),
    ("抹ча", "抹茶"), ("抹 ча", "抹茶"),
    ("抹 tea", "抹茶"), ("薄 tea", "薄茶"), ("濃 tea", "濃茶"),
    ("みるく", "ミルク"), ("らて", "ラテ"),
]
# Buffer size for streaming fix — must be >= longest wrong pattern
_JA_FIX_BUF = max(len(w) for w, _ in _JA_FIXES)


def _fix_japanese(text: str) -> str:
    """Fix known Nemotron CJK tokenization artifacts in Japanese text."""
    for wrong, correct in _JA_FIXES:
        text = text.replace(wrong, correct)
    return text


async def chat_completion(
    messages: list[dict],
    temperature: float = 0.45,
    max_tokens: int = 1600,
    language: str = "en",
) -> str:
    """Get chat completion from NVIDIA NIM model."""
    client = _get_client()
    try:
        response = await client.post(
            f"{settings.nvidia_base_url}/chat/completions",
            headers=_headers(),
            json={
                "model": settings.nvidia_chat_model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "top_p": 0.85,
                "stream": False,
            },
        )
        response.raise_for_status()
    except httpx.TimeoutException as exc:
        raise RuntimeError("Chat service timed out. Please try again.") from exc
    except httpx.HTTPStatusError as exc:
        raise RuntimeError(f"Chat service error: {exc.response.status_code}") from exc
    data = response.json()
    msg = data["choices"][0]["message"]
    content = msg.get("content") or msg.get("reasoning_content") or ""
    # Strip <think> blocks from reasoning models (closed and unclosed)
    content = _THINK_RE.sub("", content)
    content = _THINK_UNCLOSED_RE.sub("", content).strip()
    # Fix Japanese tokenization artifacts
    if language == "ja":
        content = _fix_japanese(content)
    return content


async def chat_completion_stream(
    messages: list[dict],
    temperature: float = 0.45,
    max_tokens: int = 1600,
    language: str = "en",
):
    """Yield text chunks from NVIDIA NIM model via streaming."""
    client = _get_client()
    try:
        async with client.stream(
            "POST",
            f"{settings.nvidia_base_url}/chat/completions",
            headers=_headers(),
            json={
                "model": settings.nvidia_chat_model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "top_p": 0.85,
                "stream": True,
            },
        ) as response:
            response.raise_for_status()
            think_buf = ""
            past_think = False
            ja_buf = ""  # buffer for cross-chunk JA fix
            async for line in response.aiter_lines():
                if not line.startswith("data: "):
                    continue
                payload = line[6:]
                if payload.strip() == "[DONE]":
                    break
                try:
                    chunk = _json.loads(payload)
                except _json.JSONDecodeError:
                    continue
                delta = chunk.get("choices", [{}])[0].get("delta", {})
                text = delta.get("content") or ""
                if not text:
                    continue
                # Buffer to strip <think>...</think> across chunk boundaries
                if not past_think:
                    think_buf += text
                    if "</think>" in think_buf:
                        past_think = True
                        text = think_buf.split("</think>", 1)[1]
                        think_buf = ""
                        if not text.strip():
                            continue
                    elif len(think_buf) > 7 and "<think" not in think_buf:
                        past_think = True
                        text = think_buf
                        think_buf = ""
                    else:
                        continue
                if language == "ja":
                    # Buffer to catch patterns split across chunks
                    ja_buf += text
                    ja_buf = _fix_japanese(ja_buf)
                    if len(ja_buf) > _JA_FIX_BUF:
                        emit = ja_buf[:-_JA_FIX_BUF]
                        ja_buf = ja_buf[-_JA_FIX_BUF:]
                        yield emit
                else:
                    yield text
            # Flush remaining JA buffer
            if language == "ja" and ja_buf:
                yield _fix_japanese(ja_buf)
    except httpx.TimeoutException as exc:
        raise RuntimeError("Streaming service timed out. Please try again.") from exc
    except httpx.HTTPStatusError as exc:
        raise RuntimeError(f"Streaming service error: {exc.response.status_code}") from exc
