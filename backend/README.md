# Smart Reader Backend
Прокси-бэкенд для анализа текста внешними нейросетями.

## Запуск (Разработка)
1. `python -m venv venv` и `venv\Scripts\activate`
2. `pip install -r requirements.txt`
3. Скопируй `.env.example` в `.env` и вставь свой `LLM_API_KEY`.
4. (Опционально) Скачай PEM-сертификаты Минцифры с gosuslugi.ru/crt и положи в папку `certs/`.
5. `uvicorn main:app --host 0.0.0.0 --port 8000 --reload`

## Тестирование
- `pytest tests/ -v` (Unit, контракт, E2E)
- `python test_matrix.py` (Матрица 2 адаптера × 3 языка)

## Безопасность и надёжность
- Rate limit: 10 запросов/мин на IP.
- Тайм-ауты: 60 секунд на запрос к провайдеру.
- Валидация: `selected_text` ≤ 5000, `context` ≤ 10000 символов.
- TLS: проверка включена (через `tls_config.py`).
- Секреты: хранятся только в `.env` (в `.gitignore`).