import os
from pathlib import Path
from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла
load_dotenv()

# Определяем базовую директорию проекта
BASE_DIR = Path(__file__).resolve().parent

class Config:
    """Основные конфигурации проекта."""
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
    
    # Заголовки, необходимые для OpenRouter API
    OPENROUTER_HEADERS = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "HTTP-Referer": os.getenv("YOUR_SITE_URL", "http://localhost"),
        "X-Title": os.getenv("YOUR_APP_NAME", "AI Sales MVP"),
    }
    
    # Бесплатные модели, доступные на OpenRouter
    FREE_MODEL = "mistralai/mistral-7b-instruct:free"
    # Более мощная модель для сложных задач анализа
    ADVANCED_MODEL = "microsoft/wizardlm-2-8x22b" 
    
    # Пути к данным
    DATA_DIR = BASE_DIR / "data"
    CRM_FILE = DATA_DIR / "crm" / "clients.json"
    KB_FILE = DATA_DIR / "knowledge_base" / "products.json"
    CALLS_DIR = DATA_DIR / "calls"

