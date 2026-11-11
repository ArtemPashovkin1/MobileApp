import os, sys
from fastapi.testclient import TestClient
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import app, limiter

limiter.enabled = False
client = TestClient(app)

def test_e2e_english():
    r = client.post("/api/analyze", json={"selected_text": "Alice jumped", "context": "Alice jumped up.", "book_title": "Alice", "language": "en"})
    assert r.status_code in (200, 502)
    if r.status_code == 200: assert len(r.json()["translation"]) > 5