import httpx
from config import Config
import json

class CallAnalyzer:
    async def analyze(self, call_text):
        system_prompt = """
        Ты - опытный руководитель отдела продаж. Твоя задача - проанализировать транскрипцию звонка.
        
        Проанализируй звонок по следующим критериям:
        1.  **Качество звонка:** Хороший или плохой?
        2.  **Обоснование:** Почему ты так считаешь? Что сработало, а что нет? (Приветствие, выявление потребностей, презентация, работа с возражениями, закрытие).
        3.  **Рекомендации:** Дай ровно 3 конкретные рекомендации по улучшению скрипта или действий менеджера.

        Ответ дай СТРОГО в формате JSON:
        {
            "call_quality": "хороший" | "плохой",
            "analysis": "Твой детальный анализ...",
            "recommendations": [
                "Рекомендация 1",
                "Рекомендация 2",
                "Рекомендация 3"
            ]
        }
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=Config.OPENROUTER_HEADERS,
                json={
                    "model": Config.ADVANCED_MODEL, # Используем более мощную модель для анализа
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": f"Проанализируй этот звонок:\n\n{call_text}"},
                    ],
                    "response_format": {"type": "json_object"}
                },
                timeout=60
            )
        response.raise_for_status()
        # Извлекаем JSON-строку из ответа и парсим ее
        analysis_data = json.loads(response.json()["choices"][0]["message"]["content"])
        return analysis_data
