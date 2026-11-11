import json
import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(current_dir)
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

# ✅ Инициализация TLS ДО импорта GigaChat!
from tls_config import setup_tls_environment
setup_tls_environment()

from gigachat import GigaChat
from gigachat.models import ChatCompletionRequest, ChatMessage
from .base import LLMAdapter, AnalysisResult

try:
    from .prompts import SYSTEM_PROMPT, build_user_prompt
except ImportError:
    from prompts import SYSTEM_PROMPT, build_user_prompt


class GigaChatAdapter(LLMAdapter):
    name = "gigachat"

    def __init__(self, credentials: str, model: str, timeout: float = 60.0):
        self.client = GigaChat(
            credentials=credentials,
            verify_ssl_certs=True,
            model=model,
            timeout=timeout
        )
        self.model = model

    def analyze(self, selected_text: str, context: str, book_title: str, language: str) -> AnalysisResult:
        request = ChatCompletionRequest(
            model=self.model,
            messages=[
                ChatMessage(role="system", content=SYSTEM_PROMPT),
                ChatMessage(role="user", content=build_user_prompt(selected_text, context, book_title))
            ]
        )
        response = self.client.chat.create(request)
        raw = response.messages[0].content[0].text.strip()

        if raw.startswith("```"):
            raw = raw.split("```json", 1)[-1].split("```", 1)[0].strip()

        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            data = {"meaning": raw[:100], "translation": "Ошибка формата", "nuance": "", "tone": ""}

        return AnalysisResult(
            meaning=str(data.get("meaning", "")),
            translation=str(data.get("translation", "")),
            nuance=str(data.get("nuance", "")),
            tone=str(data.get("tone", "")),
        )