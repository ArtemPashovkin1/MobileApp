import os
import time
from dotenv import load_dotenv
from adapters.openai_adapter import OpenAICompatibleAdapter
from adapters.gigachat_adapter import GigaChatAdapter

load_dotenv()

KEY = os.getenv("LLM_API_KEY", "")

adapters = {
    "OpenAI-совместимый (api.giga.chat/v1, модель GigaChat)": OpenAICompatibleAdapter(
        base_url="https://api.giga.chat/v1", model="GigaChat", api_key=KEY),
    "Нативный SDK (другой формат, модель GigaChat-2)": GigaChatAdapter(
        credentials=KEY, model="GigaChat-2"),
}

cases = [
    ("en", "Alice was not a bit hurt, and she jumped up in a moment.",
     "Alice was not a bit hurt, and she jumped up in a moment. She looked up, but it was all dark overhead."),
    ("ru", "Мы все здесь безумны.",
     "Кот усмехнулся. Мы все здесь безумны. Я безумен. Ты безумна."),
    ("de", "Es war einmal ein König.",
     "Es war einmal ein König, der hatte eine schöne Tochter. Sie war aber sehr stolz."),
]

print("=" * 60)
print("ТЕСТОВАЯ МАТРИЦА: 2 адаптера x 3 языка")
print("=" * 60)

for name, adapter in adapters.items():
    print(f"\n--- {name} ---")
    for lang, text, context in cases:
        start = time.time()
        try:
            res = adapter.analyze(text, context, "Test Book", lang)
            ok = "OK " if res.translation and res.translation != "Ошибка формата" else "?? "
            print(f"  [{ok}] язык={lang} | {time.time()-start:.1f}s | перевод: {res.translation[:40]}")
        except Exception as e:
            print(f"  [ERR] язык={lang} | {type(e).__name__}: {str(e)[:80]}")

print("\n" + "=" * 60)
print("ГОТОВО. Сохрани вывод: py test_matrix.py > test_log.txt")