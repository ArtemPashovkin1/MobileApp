import os, sys
from fastapi.testclient import TestClient
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import app, limiter

limiter.enabled = False  # Отключаем rate limit в тестах
client = TestClient(app)

def test_health():
    assert client.get("/api/health").status_code == 200

def test_analyze_rejects_empty():
    assert client.post("/api/analyze", json={"selected_text": "", "context": "ctx"}).status_code == 422
    assert client.post("/api/analyze", json={"selected_text": "hi", "context": ""}).status_code == 422
    assert client.post("/api/analyze", json={"selected_text": "x"*6000, "context": "ctx"}).status_code == 422

def test_analyze_contract_fields():
    r = client.post("/api/analyze", json={"selected_text": "Hi", "context": "Hi there", "book_title": "T", "language": "en"})
    assert r.status_code in (200, 502)
    if r.status_code == 200:
        assert set(r.json().keys()) == {"meaning", "translation", "nuance", "tone"}