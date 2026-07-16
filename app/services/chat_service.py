from collections.abc import Iterator

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models import Chat, Message
from app.services.llm import generate_answer, generate_answer_stream
from app.services.redis_client import redis_client
from app.services.retrieval_service import retrieve_chunks


class ChatAccessService:
    """Handles authorization checks for chat resources."""

    def __init__(self, db: Session):
        self.db = db

    def ensure_owned_by(self, chat_id: int, user_id: int) -> Chat:
        chat = self.db.query(Chat).filter(
            Chat.id == chat_id,
            Chat.owner_id == user_id,
        ).first()

        if not chat:
            raise HTTPException(status_code=404, detail="Chat not found")

        return chat


class MessageService:
    """Persists messages and formats recent conversation history."""

    def __init__(self, db: Session):
        self.db = db

    def save(self, chat_id: int, role: str, content: str) -> Message:
        message = Message(chat_id=chat_id, role=role, content=content)
        self.db.add(message)
        self.db.commit()
        return message

    def get_recent_history(self, chat_id: int, limit: int = 6) -> str:
        messages = self.db.query(Message).filter(
            Message.chat_id == chat_id,
        ).order_by(Message.created_at.asc()).all()

        return "".join(
            f"{message.role}: {message.content}\n"
            for message in messages[-limit:]
        )


class PromptBuilder:
    """Builds prompts for document-grounded chat answers."""

    def build(self, history: str, chunks: list[str], question: str) -> str:
        context = "\n\n".join(chunks)
        return f"""
You are a helpful AI assistant. Give short and straightforward answers strictly from the context. Do not hallucinate.

Conversation History:
{history}

Retrieved Context:
{context}

Current User Question:
{question}

Answer naturally and clearly. If context not found say directly that you don't know.
"""


class ChatMessageService:
    """Coordinates the document-grounded chat-message use case."""

    def __init__(self, db: Session):
        self.db = db
        self.chat_access = ChatAccessService(db)
        self.messages = MessageService(db)
        self.prompt_builder = PromptBuilder()

    def send_message(self, chat_id: int, user_id: int, query: str) -> dict:
        self.chat_access.ensure_owned_by(chat_id, user_id)
        self.messages.save(chat_id, "user", query)

        cache_key = self._cache_key(user_id, query)
        cached_answer = redis_client.get(cache_key)
        if cached_answer:
            self.messages.save(chat_id, "assistant", cached_answer)
            return {
                "chat_id": chat_id,
                "response": cached_answer,
                "source": "redis_cache",
            }

        prompt, chunks = self._build_prompt(chat_id, user_id, query)
        answer = generate_answer(prompt)
        redis_client.set(cache_key, answer, ex=3600)
        self.messages.save(chat_id, "assistant", answer)

        return {
            "chat_id": chat_id,
            "response": answer,
            "retrieved_chunks": chunks,
        }

    def prepare_stream(
        self, chat_id: int, user_id: int, query: str
    ) -> Iterator[str]:
        self.chat_access.ensure_owned_by(chat_id, user_id)
        self.messages.save(chat_id, "user", query)
        prompt, _ = self._build_prompt(chat_id, user_id, query)

        return self._stream_answer(chat_id, prompt)

    def _stream_answer(self, chat_id: int, prompt: str) -> Iterator[str]:
        full_answer: list[str] = []
        for token in generate_answer_stream(prompt):
            full_answer.append(token)
            yield f"data: {token}\n\n"

        self.messages.save(chat_id, "assistant", "".join(full_answer))
        yield "data: [DONE]\n\n"

    def _build_prompt(self, chat_id: int, user_id: int, query: str) -> tuple[str, list[str]]:
        chunks = retrieve_chunks(
            question=query,
            db=self.db,
            user_id=user_id,
            top_k=10,
            final_k=5,
        )
        if not chunks:
            raise HTTPException(
                status_code=400,
                detail="No document chunks found. Please upload a document first.",
            )

        history = self.messages.get_recent_history(chat_id)
        return self.prompt_builder.build(history, chunks, query), chunks

    @staticmethod
    def _cache_key(user_id: int, query: str) -> str:
        return f"user:{user_id}:query:{query}"
