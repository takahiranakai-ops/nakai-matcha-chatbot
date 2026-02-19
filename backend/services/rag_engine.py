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
_RELEVANCE_THRESHOLD = 0.65


class RAGEngine:
    def __init__(self, vector_store: VectorStore):
        self.vector_store = vector_store

    async def answer(
        self,
        user_message: str,
        conversation_history: Optional[List[Dict]] = None,
        language: str = "en",
    ) -> dict:
        system_prompt = build_system_prompt(language=language)
        msg_stripped = user_message.strip()

        # For greetings / small talk, skip RAG entirely (faster + more natural)
        if _GREETING_RE.match(msg_stripped) or len(msg_stripped) <= 5:
            messages = [{"role": "system", "content": system_prompt}]
            if conversation_history:
                messages.extend(conversation_history[-6:])
            messages.append({"role": "user", "content": msg_stripped})
            response = await chat_completion(messages, temperature=0.5, max_tokens=256)
            return {"response": response, "sources": []}

        # 1. Embed the user query
        query_embeddings = await get_embeddings([user_message], input_type="query")
        query_embedding = query_embeddings[0]

        # 2. Retrieve relevant documents
        results = self.vector_store.query(
            query_embedding=query_embedding,
            n_results=settings.max_context_chunks,
        )

        # 3. Filter by relevance — drop low-quality matches
        context_texts = []
        source_urls = set()
        for result in results:
            if result["distance"] > _RELEVANCE_THRESHOLD:
                continue
            context_texts.append(result["text"])
            url = result["metadata"].get("url")
            if url:
                source_urls.add(url)

        # 4. Build messages
        if context_texts:
            context = "\n---\n".join(context_texts)
            rag_context = build_rag_prompt(context=context, question=user_message)
        else:
            rag_context = user_message

        messages = [{"role": "system", "content": system_prompt}]
        if conversation_history:
            messages.extend(conversation_history[-6:])
        messages.append({"role": "user", "content": rag_context})

        # 5. Generate response
        response = await chat_completion(messages, temperature=0.3, max_tokens=512)

        return {
            "response": response,
            "sources": list(source_urls),
        }
