import os
import logging
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from adapters import get_adapter

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()

app = FastAPI(title="Smart Reader Backend", version="1.0.0")

# Rate limiting: 10 запросов в минуту на IP
limiter = Limiter(key_func=get_remote_address, default_limits=["10/minute"])
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["POST", "GET"], allow_headers=["*"]
)

class AnalyzeRequest(BaseModel):
    selected_text: str = Field(..., min_length=1, max_length=5000, description="Выделенный текст")
    context: str = Field(..., min_length=1, max_length=10000, description="Контекст абзаца")
    book_title: str = Field(default="", max_length=500)
    language: str = Field(default="", max_length=10)

class AnalyzeResponse(BaseModel):
    meaning: str
    translation: str
    nuance: str
    tone: str

@app.get("/api/health")
async def health():
    return {"status": "ok", "provider": os.getenv("LLM_PROVIDER", "unknown"), "model": os.getenv("LLM_MODEL", "unknown")}

@app.post("/api/analyze", response_model=AnalyzeResponse)
@limiter.limit("10/minute")
async def analyze(req: AnalyzeRequest, request: Request):
    logger.info(f"Анализ: язык={req.language}, длина={len(req.selected_text)}")
    try:
        adapter = get_adapter()
        result = adapter.analyze(req.selected_text, req.context, req.book_title, req.language)

        if not result.translation or result.translation == "Ошибка формата":
            logger.warning("Модель вернула некорректный JSON")
            raise HTTPException(status_code=502, detail="Неверный ответ модели: ожидался валидный JSON")

        return AnalyzeResponse(meaning=result.meaning, translation=result.translation, nuance=result.nuance, tone=result.tone)

    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"Ошибка конфигурации: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка конфигурации провайдера: {e}")
    except TimeoutError as e:
        logger.error(f"Тайм-аут: {e}")
        raise HTTPException(status_code=504, detail="Провайдер не ответил вовремя (тайм-аут)")
    except Exception as e:
        logger.error(f"Сбой провайдера: {type(e).__name__}: {e}")
        raise HTTPException(status_code=502, detail=f"Провайдер временно недоступен ({type(e).__name__})")

@app.post("/api/illustrate")
@limiter.limit("5/minute")
async def illustrate(request: Request):
    raise HTTPException(status_code=501, detail="Генерация изображений не поддерживается")