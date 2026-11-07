import json
import os
import sys
import requests

current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(current_dir)
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from .base import LLMAdapter, AnalysisResult

try:
    from .prompts import SYSTEM_PROMPT, build_user_prompt
except ImportError:
    from prompts import SYSTEM_PROMPT, build_user_prompt


class OpenAICompatibleAdapter(LLMAdapter):
    name = "openai_compatible"

    def __init__(self, base_url: str, model: str, api_key: str):
        self.endpoint = base_url.rstrip("/") + "/chat/completions"
        self.model = model
        self.api_key = api_key

    def analyze(self, selected_text: str, context: str, book_title: str, language: str) -> AnalysisResult:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": build_user_prompt(selected_text, context, book_title)}
            ]
        }

        try:
            response = requests.post(
                self.endpoint,
                json=payload,
                headers=headers,
                verify=False,
                timeout=60.0
            )
            response.raise_for_status()
            data = response.json()

            raw = data["choices"][0]["message"]["content"].strip()

            if raw.startswith("```"):
                raw = raw.split("```json", 1)[-1].split("```", 1)[0].strip()

            try:
                parsed_data = json.loads(raw)
            except json.JSONDecodeError:
                parsed_data = {
                    "meaning": raw[:100] + "...",
                    "translation": "Ошибка формата",
                    "nuance": "",
                    "tone": ""
                }

            return AnalysisResult(
                meaning=str(parsed_data.get("meaning", "")),
                translation=str(parsed_data.get("translation", "")),
                nuance=str(parsed_data.get("nuance", "")),
                tone=str(parsed_data.get("tone", "")),
            )
        except requests.exceptions.RequestException as e:
            print(f"Ошибка OpenAI-совместимого запроса: {e}")
            raise Exception("LLM unavailable")