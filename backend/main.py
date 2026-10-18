import json
import os

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from openai import AsyncOpenAI
from pydantic import BaseModel

load_dotenv()

API_KEY = os.getenv("LLM_API_KEY", "")
BASE_URL = os.getenv("LLM_BASE_URL", "https://api.openai.com/v1")
MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini")

app = FastAPI(title="Smart Reader Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

client = AsyncOpenAI(api_key=API_KEY, base_url=BASE_URL)


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
    return {"status": "ok", "model": MODEL}


@app.post("/api/analyze", response_model=AnalyzeResponse)
async def analyze(req: AnalyzeRequest):
    if not req.selected_text.strip():
        raise HTTPException(status_code=400, detail="пустой selected_text")
    if not req.context.strip():
        raise HTTPException(status_code=400, detail="пустой context")

    user_prompt = f'Книга: {req.book_title or "неизвестна"}.\nАбзац: "{req.context}"\nВыделено: "{req.selected_text}"'

    try:
        resp = await client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            response_format={"type": "json_object"},
        )
    except Exception:
        raise HTTPException(status_code=502, detail="llm unavailable")

    raw = resp.choices[0].message.content
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        data = {"meaning": raw, "translation": "", "nuance": "", "tone": ""}

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
    prompt = "atmospheric book illustration, no text: " + req.context[:800]
    try:
        resp = await client.images.generate(model="gpt-image-1", prompt=prompt, size="512x512")
        url = resp.data[0].url
    except Exception:
        raise HTTPException(status_code=502, detail="image model unavailable")
    return {"image_url": url}