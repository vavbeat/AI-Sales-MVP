import httpx
from config import Config
import json

class ScriptGenerator:
    async def generate(self, successful_calls_texts: list):
        examples = "\n\n---\n\n".join(successful_calls_texts)
        system_prompt = f"""
        Ты - методолог по продажам. Твоя задача - создать универсальный шаблон скрипта продаж на основе нескольких успешных звонков.

        ПРИМЕРЫ УСПЕШНЫХ ЗВОНКОВ:
        {examples}
        
        ЗАДАЧА:
        1. Проанализируй структуру, триггеры и лучшие фразы из примеров.
        2. Создай универсальный шаблон скрипта, разбитый на этапы:
           - Приветствие и установление контакта
           - Выявление потребностей (квалифицирующие вопросы)
           - Презентация решения
           - Работа с возражениями (предложи 2-3 варианта)
           - Закрытие сделки (предложение следующего шага)
        3. В каждом этапе приведи лучшие фразы-примеры из проанализированных звонков.
        4. Кратко объясни логику структуры: почему именно такие этапы и триггеры эффективны.

        Ответ дай в формате Markdown.
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=Config.OPENROUTER_HEADERS,
                json={
                    "model": Config.ADVANCED_MODEL,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": "Создай шаблон скрипта на основе предоставленных примеров."},
                    ],
                },
                timeout=90
            )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
