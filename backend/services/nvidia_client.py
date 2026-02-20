import re

import httpx

from config import settings

# Strip <think>...</think> blocks from reasoning models
_THINK_RE = re.compile(r"<think>.*?</think>\s*", re.DOTALL)


def _headers() -> dict:
    return {
        "Authorization": f"Bearer {settings.ngc_api_key}",
        "Content-Type": "application/json",
    }


async def get_embeddings(
    texts: list[str], input_type: str = "query"
) -> list[list[float]]:
    """Get embeddings from NVIDIA NIM embedding model.

    Args:
        texts: List of texts to embed.
        input_type: "query" for user questions, "passage" for documents.
    """
    results = []
    batch_size = 50
    async with httpx.AsyncClient(timeout=60.0) as client:
        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]
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
            )
            response.raise_for_status()
            data = response.json()
            results.extend([item["embedding"] for item in data["data"]])
    return results


async def chat_completion(
    messages: list[dict],
    temperature: float = 0.45,
    max_tokens: int = 1500,
) -> str:
    """Get chat completion from NVIDIA NIM model."""
    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(
            f"{settings.nvidia_base_url}/chat/completions",
            headers=_headers(),
            json={
                "model": settings.nvidia_chat_model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "top_p": 0.92,
                "frequency_penalty": 0.15,
                "stream": False,
            },
        )
        response.raise_for_status()
        data = response.json()
        msg = data["choices"][0]["message"]
        content = msg.get("content") or msg.get("reasoning_content") or ""
        # Strip <think> blocks from reasoning models
        content = _THINK_RE.sub("", content).strip()
        return content
