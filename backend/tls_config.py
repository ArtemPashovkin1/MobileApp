import os
import warnings

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CERTS_DIR = os.path.join(BASE_DIR, "certs")
BUNDLE_PATH = os.path.join(CERTS_DIR, "ca_bundle.pem")


def build_ca_bundle() -> str | None:
    """Собирает bundle: стандартные CA (certifi) + сертификаты Минцифры."""
    try:
        import certifi
        sources = [certifi.where()]
    except ImportError:
        sources = []

    if os.path.isdir(CERTS_DIR):
        for name in sorted(os.listdir(CERTS_DIR)):
            # Ищем .pem, .crt, .cer файлы
            if name.endswith((".pem", ".crt", ".cer")) and name != "ca_bundle.pem":
                sources.append(os.path.join(CERTS_DIR, name))

    if len(sources) <= 1:
        # Только certifi, российских сертификатов нет
        return None

    with open(BUNDLE_PATH, "w", encoding="utf-8") as out:
        for path in sources:
            with open(path, "r", encoding="utf-8") as f:
                out.write(f.read())
                out.write("\n")
    return BUNDLE_PATH


def get_verify_setting():
    """Возвращает путь к bundle для проверки TLS. Если нет — False (с warning)."""
    bundle = build_ca_bundle()
    if bundle:
        return bundle
    warnings.warn(
        "Сертификаты Минцифры не найдены в backend/certs/. "
        "TLS-проверка отключена (только для разработки!). "
        "Скачайте PEM с https://www.gosuslugi.ru/crt",
        RuntimeWarning,
    )
    return False


def setup_tls_environment() -> bool:
    """Вызывать ДО создания HTTP-клиентов (requests читает эти переменные)."""
    bundle = build_ca_bundle()
    if bundle:
        os.environ["SSL_CERT_FILE"] = bundle
        os.environ["REQUESTS_CA_BUNDLE"] = bundle
        return True
    return False