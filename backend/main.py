import json
import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Импортируем актуальные классы из новой версии SDK
from gigachat import GigaChat
from gigachat.models import ChatCompletionRequest, ChatMessage

load_dotenv()

GIGACHAT_CREDENTIALS = os.getenv("LLM_API_KEY", "")
GIGACHAT_MODEL = os.getenv("LLM_MODEL", "GigaChat")

app = FastAPI(title="Smart Reader Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Инициализируем клиент с указанием модели
gc_client = GigaChat(
    credentials=GIGACHAT_CREDENTIALS,
    verify_ssl_certs=False,
    model=GIGACHAT_MODEL  # Явно указываем модель
)


class AnalyzeRequest(BaseModel):
    selected_text: str
    context: str
    book_title: str = ""
    language: str = ""


class AnalyzeResponse(BaseModel):
    meaning: str
    translation: str
    nuance: str
    tone: str


class IllustrateRequest(BaseModel):
    context: str


SYSTEM_PROMPT = """Ты — профессиональный филолог-переводчик. Анализируешь выделенный текст из книги с учётом контекста абзаца.

КРИТИЧЕСКИ ВАЖНО:
- ОТВЕЧАЙ ИСКЛЮЧИТЕЛЬНО НА РУССКОМ ЯЗЫКЕ. НИ ОДНОГО СЛОВА НА ДРУГОМ ЯЗЫКЕ.
- Если не знаешь ответа — пиши "неизвестно" на русском.
- Отвечай ТОЛЬКО валидным JSON, без markdown, без кодовых блоков, без пояснений.

Формат ответа СТРОГО:
{"meaning": "скрытый смысл на русском", "translation": "перевод на русский", "nuance": "нюанс или этимология на русском", "tone": "эмоциональный окрас на русском"}

ПРИМЕР ПРАВИЛЬНОГО ОТВЕТА:
{"meaning": "выражение удивления необычной ситуацией", "translation": "Какое странное чувство!", "nuance": "метафора сравнения с телескопом — резкое изменение размера", "tone": "удивление и любопытство"}"""


@app.get("/api/health")
async def health():
    return {"status": "ok", "model": GIGACHAT_MODEL}


@app.post("/api/analyze", response_model=AnalyzeResponse)
def analyze(req: AnalyzeRequest):
    if not req.selected_text.strip():
        raise HTTPException(status_code=400, detail="пустой selected_text")
    if not req.context.strip():
        raise HTTPException(status_code=400, detail="пустой context")

    user_prompt = f'Книга: {req.book_title or "неизвестна"}.\nАбзац: "{req.context}"\nВыделено: "{req.selected_text}"'

    try:
        # Передаём модель в запросе (приоритет над дефолтной)
        request = ChatCompletionRequest(
            model=GIGACHAT_MODEL,
            messages=[
                ChatMessage(role="system", content=SYSTEM_PROMPT),
                ChatMessage(role="user", content=user_prompt)
            ]
        )
        response = gc_client.chat.create(request)
    except Exception as e:
        print(f" Ошибка GigaChat API: {e}")
        raise HTTPException(status_code=502, detail="llm unavailable")

    # В новом API ответ лежит в response.messages[0].content[0].text
    raw = response.messages[0].content[0].text
    
    # Очистка от markdown-блоков, если модель всё же их добавила
    if raw and raw.startswith("```"):
        raw = raw.split("```json", 1)[-1].split("```", 1)[0].strip()
    elif raw and raw.startswith("```"):
        raw = raw.split("```", 1)[-1].split("```", 1)[0].strip()

    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        print(f"⚠️ Не удалось распарсить JSON. Сырой ответ: {raw}")
        data = {
            "meaning": raw[:100] + "...", 
            "translation": "Ошибка формата", 
            "nuance": "", 
            "tone": ""
        }

    return AnalyzeResponse(
        meaning=str(data.get("meaning", "")),
        translation=str(data.get("translation", "")),
        nuance=str(data.get("nuance", "")),
        tone=str(data.get("tone", "")),
    )


@app.post("/api/illustrate")
async def illustrate(req: IllustrateRequest):
    if not req.context.strip():
        raise HTTPException(status_code=400, detail="пустой context")
    
    raise HTTPException(status_code=501, detail="Image generation is not supported by current LLM provider")