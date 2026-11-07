import os
from .openai_adapter import OpenAICompatibleAdapter
from .gigachat_adapter import GigaChatAdapter


def get_adapter():
    provider = os.getenv("LLM_PROVIDER", "openai").lower()

    if provider == "openai":
        return OpenAICompatibleAdapter(
            base_url=os.getenv("LLM_BASE_URL", "https://api.giga.chat/v1"),
            model=os.getenv("LLM_MODEL", "GigaChat"),
            api_key=os.getenv("LLM_API_KEY", ""),
        )
    elif provider == "gigachat":
        return GigaChatAdapter(
            credentials=os.getenv("LLM_API_KEY", ""),
            model=os.getenv("LLM_MODEL", "GigaChat-2"),
        )

    raise ValueError(f"Неизвестный провайдер: {provider}. Доступны: openai, gigachat")