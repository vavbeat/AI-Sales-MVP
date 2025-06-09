import logging
from telegram import Update
from telegram.ext import ContextTypes

from bot.services.rag_service import RAGService
from bot.services.call_analyzer import CallAnalyzer
from bot.services.script_generator import ScriptGenerator
from config import Config

# Инициализируем сервисы один раз
rag_service = RAGService()
call_analyzer = CallAnalyzer()
script_generator = ScriptGenerator()

# Словарь для хранения состояний пользователей
user_states = {}

def add_test_user_to_crm(user_id, first_name):
    """Добавляет тестового пользователя в CRM для демонстрации"""
    test_user = {
        "client_id": 999,
        "telegram_user_id": user_id,
        "name": first_name or "Тестовый клиент",
        "previous_purchase": "Bentley Continental GT (2022)",
        "budget": "400000 USD",
        "deal_status": "VIP клиент",
        "preferences": "Скорость, роскошь, новые технологии",
        "notes": "Интересуется апгрейдом автомобиля",
        "purchase_history": [
            {"car": "Bentley Continental GT", "year": 2022, "price": 280000}
        ]
    }
    
    # Добавляем пользователя в память (в реальном проекте - в базу данных)
    rag_service.clients.append(test_user)
    return test_user

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_states[update.effective_user.id] = "sales"
    
    # Определяем язык для приветствия
    if update.effective_user.language_code and update.effective_user.language_code.startswith('ru'):
        welcome_text = """🏆 **Добро пожаловать в AI Sales MVP!** 

Я ваш ИИ-ассистент по продажам премиальных автомобилей.

**🔧 Доступные режимы работы:**
• `анализ звонка` - анализ качества продаж
• `генерация скрипта` - создание скриптов продаж
• `продажи` - консультации по автомобилям (режим по умолчанию)

**💼 Демонстрация возможностей:**
Попробуйте написать: "Хочу Bentley" или "Интересует Rolls-Royce"

Чем могу помочь?"""
    else:
        welcome_text = """🏆 **Welcome to AI Sales MVP!** 

I'm your AI sales assistant for premium automobiles.

**🔧 Available modes:**
• `call analysis` - sales quality analysis  
• `script generation` - create sales scripts
• `sales` - automobile consultations (default mode)

**💼 Demo capabilities:**
Try typing: "Want Bentley" or "Interested in Rolls-Royce"

How can I help you?"""
    
    await update.message.reply_text(welcome_text, parse_mode='Markdown')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.lower()

    # Логика переключения режимов
    if "анализ звонка" in text or "call analysis" in text:
        user_states[user_id] = "analysis"
        if update.effective_user.language_code and update.effective_user.language_code.startswith('ru'):
            msg = """🔍 **Режим анализа звонков активирован**

Пришлите мне текст звонка для анализа. Я определю:
• Качество звонка (хороший/плохой)
• Что сработало, а что нет
• 3 конкретные рекомендации по улучшению

Ожидаю текст разговора..."""
        else:
            msg = """🔍 **Call analysis mode activated**

Send me call text for analysis. I will determine:
• Call quality (good/bad)
• What worked and what didn't
• 3 specific improvement recommendations

Waiting for conversation text..."""
        await update.message.reply_text(msg, parse_mode='Markdown')
        return
        
    elif "генерация скрипта" in text or "script generation" in text:
        user_states[user_id] = "script_gen"
        if update.effective_user.language_code and update.effective_user.language_code.startswith('ru'):
            msg = """📝 **Режим генерации скрипта активирован**

Отправьте любое сообщение, и я создам профессиональный скрипт продаж на основе лучших практик.

Скрипт будет включать:
• Приветствие и установление контакта
• Выявление потребностей
• Презентация решения
• Работа с возражениями
• Закрытие сделки"""
        else:
            msg = """📝 **Script generation mode activated**

Send any message and I'll create a professional sales script based on best practices.

Script will include:
• Greeting and rapport building
• Needs identification
• Solution presentation
• Objection handling
• Deal closing"""
        await update.message.reply_text(msg, parse_mode='Markdown')
        return
        
    elif "продажи" in text or "sales" in text:
        user_states[user_id] = "sales"
        if update.effective_user.language_code and update.effective_user.language_code.startswith('ru'):
            msg = """💼 **Режим продаж активирован**

Я ваш персональный ИИ-консультант по премиальным автомобилям.
Задайте ваш вопрос о Bentley, Rolls-Royce или других люксовых брендах.

Пример запросов:
• "Хочу Bentley"
• "Что посоветуете в бюджете $300k?"
• "Нужен семейный автомобиль класса люкс" """
        else:
            msg = """💼 **Sales mode activated**

I'm your personal AI consultant for premium automobiles.
Ask your question about Bentley, Rolls-Royce or other luxury brands.

Example queries:
• "Want Bentley"
• "What do you recommend for $300k budget?"
• "Need luxury family car" """
        await update.message.reply_text(msg, parse_mode='Markdown')
        return

    # Обработка в зависимости от режима
    mode = user_states.get(user_id, "sales")
    
    if mode == "sales":
        await handle_sales(update, context)
    elif mode == "analysis":
        await handle_analysis(update, context)
    elif mode == "script_gen":
        await handle_script_gen(update, context)

async def handle_sales(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик режима продаж с использованием CRM данных"""
    await update.message.reply_chat_action("typing")
    
    try:
        user_language_code = update.effective_user.language_code
        user_id = update.effective_user.id
        
        # Получаем информацию о клиенте из CRM
        client_info = rag_service.get_client_info(user_id)
        
        # Если клиента нет в CRM, добавляем его как тестового для демонстрации
        if not client_info:
            client_info = add_test_user_to_crm(user_id, update.effective_user.first_name)
            
        # Генерируем персонализированный ответ
        suggestion = await rag_service.get_ai_suggestion(
            update.message.text, 
            client_info, 
            user_language_code
        )
        
        # Определяем язык для отображения CRM информации
        is_russian = user_language_code and user_language_code.startswith('ru')
        
        if is_russian:
            crm_info = f"""📊 **Данные клиента из CRM:**
• **Имя:** {client_info['name']}
• **Статус:** {client_info['deal_status']}
• **Предыдущая покупка:** {client_info.get('previous_purchase', 'Нет')}
• **Бюджет:** {client_info['budget']}
• **Предпочтения:** {client_info.get('preferences', 'Не указаны')}

---

{suggestion}"""
        else:
            crm_info = f"""📊 **Client CRM Data:**
• **Name:** {client_info['name']}
• **Status:** {client_info['deal_status']}
• **Previous Purchase:** {client_info.get('previous_purchase', 'None')}
• **Budget:** {client_info['budget']}
• **Preferences:** {client_info.get('preferences', 'Not specified')}

---

{suggestion}"""
        
        await update.message.reply_text(
            crm_info, 
            parse_mode='Markdown',
            disable_web_page_preview=True
        )
        
    except Exception as e:
        logging.error(f"Ошибка в режиме продаж: {e}")
        
        # Определяем язык для сообщения об ошибке
        if update.effective_user.language_code and update.effective_user.language_code.startswith('ru'):
            error_msg = "❌ Произошла ошибка при обработке запроса. Попробуйте еще раз или переформулируйте вопрос."
        else:
            error_msg = "❌ An error occurred while processing your request. Please try again or rephrase your question."
            
        await update.message.reply_text(error_msg)

async def handle_analysis(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик режима анализа звонков"""
    await update.message.reply_chat_action("typing")
    
    # Определяем язык пользователя
    is_russian = update.effective_user.language_code and update.effective_user.language_code.startswith('ru')
    
    if is_russian:
        processing_msg = "🔍 **Анализирую звонок...** \n\nЭто может занять до минуты. Пожалуйста, подождите."
    else:
        processing_msg = "🔍 **Analyzing call...** \n\nThis may take up to a minute. Please wait."
    
    status_message = await update.message.reply_text(processing_msg, parse_mode='Markdown')
    
    try:
        # Анализируем звонок с помощью ИИ
        analysis = await call_analyzer.analyze(update.message.text)
        
        if is_russian:
            response_text = f"""📊 **Результат анализа звонка**

🎯 **Качество звонка:** {analysis['call_quality']}

📝 **Детальный анализ:**
{analysis['analysis']}

💡 **Рекомендации по улучшению:**
1️⃣ {analysis['recommendations'][0]}

2️⃣ {analysis['recommendations'][1]}

3️⃣ {analysis['recommendations'][2]}

---
💬 Для анализа нового звонка просто пришлите другой текст разговора."""
        else:
            response_text = f"""📊 **Call Analysis Results**

🎯 **Call Quality:** {analysis['call_quality']}

📝 **Detailed Analysis:**
{analysis['analysis']}

💡 **Improvement Recommendations:**
1️⃣ {analysis['recommendations'][0]}

2️⃣ {analysis['recommendations'][1]}

3️⃣ {analysis['recommendations'][2]}

---
💬 To analyze another call, simply send another conversation text."""
        
        # Удаляем сообщение о процессе и отправляем результат
        await status_message.delete()
        await update.message.reply_text(response_text, parse_mode='Markdown')
        
    except Exception as e:
        logging.error(f"Ошибка в режиме анализа: {e}")
        
        await status_message.delete()
        
        if is_russian:
            error_msg = "❌ Не удалось проанализировать звонок. Убедитесь, что текст содержит диалог между менеджером и клиентом."
        else:
            error_msg = "❌ Failed to analyze the call. Make sure the text contains a dialogue between manager and client."
            
        await update.message.reply_text(error_msg)

async def handle_script_gen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик режима генерации скриптов продаж"""
    # Определяем язык пользователя
    is_russian = update.effective_user.language_code and update.effective_user.language_code.startswith('ru')
    
    if is_russian:
        processing_msg = "📝 **Создаю профессиональный скрипт продаж...** \n\nЭто может занять до 90 секунд. Анализирую лучшие практики."
    else:
        processing_msg = "📝 **Creating professional sales script...** \n\nThis may take up to 90 seconds. Analyzing best practices."
    
    status_message = await update.message.reply_text(processing_msg, parse_mode='Markdown')
    await update.message.reply_chat_action("typing")
    
    try:
        # Загружаем пример успешного звонка
        with open(Config.CALLS_DIR / "example_call_good.txt", 'r', encoding='utf-8') as f:
            good_call_1 = f.read()
        
        # Генерируем скрипт на основе успешных звонков
        script = await script_generator.generate([good_call_1])
        
        # Удаляем сообщение о процессе
        await status_message.delete()
        
        if is_russian:
            header = """📋 **Профессиональный скрипт продаж создан!**

Основан на анализе успешных звонков и лучших практик продаж.

---

"""
            footer = """

---
💡 **Совет:** Адаптируйте скрипт под вашу специфику и стиль общения.
📝 Для создания нового скрипта отправьте любое сообщение."""
        else:
            header = """📋 **Professional Sales Script Created!**

Based on analysis of successful calls and sales best practices.

---

"""
            footer = """

---
💡 **Tip:** Adapt the script to your specifics and communication style.
📝 To create a new script, send any message."""
        
        full_response = header + script + footer
        
        # Отправляем скрипт частями если он слишком длинный
        if len(full_response) > 4000:
            # Разбиваем на части
            parts = [full_response[i:i+4000] for i in range(0, len(full_response), 4000)]
            for part in parts:
                await update.message.reply_text(part, parse_mode='Markdown')
        else:
            await update.message.reply_text(full_response, parse_mode='Markdown')
            
    except Exception as e:
        logging.error(f"Ошибка в режиме генерации скрипта: {e}")
        
        await status_message.delete()
        
        if is_russian:
            error_msg = "❌ Не удалось создать скрипт. Попробуйте еще раз через несколько секунд."
        else:
            error_msg = "❌ Failed to create script. Please try again in a few seconds."
            
        await update.message.reply_text(error_msg)
