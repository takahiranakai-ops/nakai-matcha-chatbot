from typing import Optional, List, Dict

from services.nvidia_client import get_embeddings, chat_completion
from services.vector_store import VectorStore
from services.prompt_templates import build_system_prompt, build_rag_prompt
from config import settings


class RAGEngine:
    def __init__(self, vector_store: VectorStore):
        self.vector_store = vector_store

    async def answer(
        self,
        user_message: str,
        conversation_history: Optional[List[Dict]] = None,
        language: str = "en",
    ) -> dict:
        # 1. Embed the user query
        query_embeddings = await get_embeddings([user_message], input_type="query")
        query_embedding = query_embeddings[0]

        # 2. Retrieve relevant documents
        results = self.vector_store.query(
            query_embedding=query_embedding,
            n_results=settings.max_context_chunks,
        )

        # 3. Build context from retrieved chunks
        context_texts = []
        source_urls = set()
        for result in results:
            context_texts.append(result["text"])
            url = result["metadata"].get("url")
            if url:
                source_urls.add(url)

        context = "\n---\n".join(context_texts) if context_texts else "No store data available."

        # 4. Build messages
        system_prompt = build_system_prompt(language=language)
        rag_context = build_rag_prompt(context=context, question=user_message)

        messages = [{"role": "system", "content": system_prompt}]

        if conversation_history:
            messages.extend(conversation_history[-6:])

        messages.append({"role": "user", "content": rag_context})

        # 5. Generate response
        response = await chat_completion(messages, temperature=0.3)

        return {
            "response": response,
            "sources": list(source_urls),
        }
