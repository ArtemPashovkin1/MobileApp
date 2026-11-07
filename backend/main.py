import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from adapters import get_adapter, AnalysisResult

load_dotenv()
app = FastAPI(title="Smart Reader Backend")

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


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


@app.get("/api/health")
async def health():
    return {
        "status": "ok",
        "provider": os.getenv("LLM_PROVIDER", "openai"),
        "model": os.getenv("LLM_MODEL", "unknown")
    }


@app.post("/api/analyze", response_model=AnalyzeResponse)
def analyze(req: AnalyzeRequest):
    if not req.selected_text.strip():
        raise HTTPException(status_code=400, detail="пустой selected_text")
    if not req.context.strip():
        raise HTTPException(status_code=400, detail="пустой context")

    try:
        adapter = get_adapter()
        result = adapter.analyze(
            selected_text=req.selected_text,
            context=req.context,
            book_title=req.book_title,
            language=req.language
        )
        return AnalyzeResponse(
            meaning=result.meaning,
            translation=result.translation,
            nuance=result.nuance,
            tone=result.tone
        )
    except Exception as e:
        print(f"Ошибка LLM: {e}")
        raise HTTPException(status_code=502, detail="llm unavailable")


@app.post("/api/illustrate")
async def illustrate(req: IllustrateRequest):
    raise HTTPException(status_code=501, detail="Image generation is not supported by current LLM provider")