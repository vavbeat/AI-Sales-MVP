import json
import httpx
from config import Config

class RAGService:
    def __init__(self):
        self.clients = self._load_json(Config.CRM_FILE)
        self.products_kb = self._load_json(Config.KB_FILE)
    
    def _load_json(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def get_client_info(self, telegram_user_id):
        """Получает полную информацию о клиенте из CRM"""
        for client in self.clients:
            if client["telegram_user_id"] == telegram_user_id:
                return client
        return None

    def _detect_language(self, query, user_language_code=None):
        """Определяет язык запроса"""
        if user_language_code and user_language_code.startswith('ru'):
            return 'ru'
        elif user_language_code and user_language_code.startswith('en'):
            return 'en'
        
        russian_chars = sum(1 for char in query if 'а' <= char.lower() <= 'я' or char in 'ёЁ')
        english_chars = sum(1 for char in query if 'a' <= char.lower() <= 'z')
        
        return 'ru' if russian_chars > english_chars else 'en'

    def _find_relevant_products(self, query, client_budget=None):
        """Находит релевантные продукты с учетом бюджета клиента"""
        relevant_products = []
        query_lower = query.lower()
        
        # Извлекаем бюджет клиента для фильтрации
        max_budget = None
        if client_budget:
            try:
                # Извлекаем числа из строки бюджета
                import re
                numbers = re.findall(r'\d+', str(client_budget))
                if numbers:
                    max_budget = int(numbers[0]) * 1000 if 'k' in client_budget.lower() else int(numbers[0])
            except:
                pass
        
        for product in self.products_kb['products']:
            # Проверяем релевантность по названию/бренду
            is_relevant = any(word in query_lower for word in [
                product['name'].lower(), 'bentley', 'rolls-royce', 'роллс', 'бентли',
                'автомобиль', 'машина', 'car', 'luxury'
            ])
            
            # Фильтруем по бюджету если указан
            if is_relevant:
                if max_budget is None or product['price_usd'] <= max_budget * 1.2:  # +20% гибкости
                    relevant_products.append(product)
        
        return relevant_products[:3]  # Максимум 3 продукта

    def _get_upsell_recommendations(self, client_info, query):
        """Генерирует рекомендации по апсейлу на основе истории клиента"""
        if not client_info or not client_info.get('previous_purchase'):
            return []
        
        upsell_options = []
        previous_car = client_info['previous_purchase'].lower()
        
        # Логика апсейла на основе предыдущих покупок
        if 'bentley' in previous_car and 'continental' in previous_car:
            upsell_options.append({
                'product': 'Rolls-Royce Phantom',
                'reason': 'Следующий уровень роскоши после Bentley Continental'
            })
        elif 'ghost' in previous_car:
            upsell_options.append({
                'product': 'Rolls-Royce Cullinan',
                'reason': 'Универсальность SUV с той же роскошью'
            })
        
        return upsell_options

    async def get_ai_suggestion(self, query, client_info, user_language_code=None):
        """Генерирует персонализированный ответ ИИ-продавца с учетом CRM данных"""
        language = self._detect_language(query, user_language_code)
        
        # Если клиент не найден в CRM, создаем базовую запись
        if not client_info:
            client_info = {
                "name": "Новый клиент",
                "deal_status": "Новый контакт",
                "previous_purchase": None,
                "budget": "Не указан",
                "preferences": "Не определены"
            }
        
        # Находим релевантные продукты с учетом бюджета
        relevant_products = self._find_relevant_products(query, client_info.get('budget'))
        
        # Получаем рекомендации по апсейлу
        upsell_recommendations = self._get_upsell_recommendations(client_info, query)
        
        # Формируем контекст для ИИ
        context_parts = []
        
        if relevant_products:
            context_parts.append("🚗 ДОСТУПНЫЕ АВТОМОБИЛИ:")
            for product in relevant_products:
                context_parts.append(f"• {product['name']}: ${product['price_usd']:,} - {product['description']}")
        
        if upsell_recommendations:
            context_parts.append("\n💎 РЕКОМЕНДАЦИИ ПО АПСЕЙЛУ:")
            for rec in upsell_recommendations:
                context_parts.append(f"• {rec['product']}: {rec['reason']}")
        
        context = "\n".join(context_parts)
        
        # Системный промпт в зависимости от языка
        if language == 'ru':
            system_prompt = f"""
Ты - элитный ИИ-продавец премиальных автомобилей. Твоя задача - дать персонализированный ответ клиенту.

КРИТИЧЕСКИ ВАЖНО - ОБЯЗАТЕЛЬНО ИСПОЛЬЗУЙ ВСЮ ИНФОРМАЦИЮ О КЛИЕНТЕ:

📋 ДАННЫЕ КЛИЕНТА ИЗ CRM:
• Имя: {client_info.get('name', 'Не указано')}
• Статус: {client_info.get('deal_status', 'Не указан')}
• Предыдущая покупка: {client_info.get('previous_purchase', 'Нет')}
• Бюджет: {client_info.get('budget', 'Не указан')}
• Предпочтения: {client_info.get('preferences', 'Не указаны')}

{context}

ПРАВИЛА ОТВЕТА:
1. ОБЯЗАТЕЛЬНО обратись к клиенту по имени
2. ОБЯЗАТЕЛЬНО упомяни его статус/предыдущие покупки
3. Учти его бюджет при рекомендациях
4. Предложи конкретный автомобиль из доступных
5. Если есть апсейл - обоснуй его
6. Ответ максимум 4 предложения
7. Закончи призывом к действию

Пример: "Аркадий, как наш VIP клиент с опытом владения Bentley Continental GT, рекомендую вам..."
"""
        else:
            system_prompt = f"""
You are an elite AI sales consultant for premium automobiles. Provide personalized response to the client.

CRITICALLY IMPORTANT - MUST USE ALL CLIENT INFORMATION:

📋 CLIENT CRM DATA:
• Name: {client_info.get('name', 'Not specified')}
• Status: {client_info.get('deal_status', 'Not specified')}
• Previous purchase: {client_info.get('previous_purchase', 'None')}
• Budget: {client_info.get('budget', 'Not specified')}
• Preferences: {client_info.get('preferences', 'Not specified')}

{context}

RESPONSE RULES:
1. MUST address client by name
2. MUST mention their status/previous purchases
3. Consider their budget in recommendations
4. Suggest specific car from available options
5. If upsell available - justify it
6. Maximum 4 sentences
7. End with call to action

Example: "Arkady, as our VIP client with Bentley Continental GT experience, I recommend..."
"""
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=Config.OPENROUTER_HEADERS,
                json={
                    "model": Config.FREE_MODEL,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": f"Запрос клиента: {query}"},
                    ],
                    "max_tokens": 400,
                    "temperature": 0.7
                },
                timeout=30
            )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
