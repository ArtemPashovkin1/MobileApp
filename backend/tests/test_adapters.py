import os, sys, pytest
from dotenv import load_dotenv
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
load_dotenv()

from adapters.openai_adapter import OpenAICompatibleAdapter
from adapters.gigachat_adapter import GigaChatAdapter

KEY = os.getenv("LLM_API_KEY", "")

def test_gigachat_adapter_init():
    adapter = GigaChatAdapter(credentials=KEY, model="GigaChat-2")
    assert adapter.name == "gigachat"

@pytest.mark.parametrize("lang,text,context", [
    ("en", "Hello", "Hello world"), ("ru", "Привет", "Привет мир"), ("de", "Hallo", "Hallo Welt")
])
def test_gigachat_analyze_languages(lang, text, context):
    adapter = GigaChatAdapter(credentials=KEY, model="GigaChat-2")
    result = adapter.analyze(text, context, "Test", lang)
    assert result.translation and result.translation != "Ошибка формата"