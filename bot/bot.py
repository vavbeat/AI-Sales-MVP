import logging
from typing import Dict, Any
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, 
    CallbackQueryHandler, filters, ContextTypes
)

from config import Config
from .services.rag_service import RAGService
from .services.openrouter_service import OpenRouterService
from .services.call_analyzer import CallAnalyzer
from .services.script_generator import ScriptGenerator
from .models.client import ClientManager

class AISalesBot:
    def __init__(self):
        self.rag_service = RAGService()
        self.ai_service = OpenRouterService()
        self.call_analyzer = CallAnalyzer()
        self.script_generator = ScriptGenerator()
        self.client_manager = ClientManager()
        self.user_states: Dict[int, Dict[str, Any]] = {}
        
    async def initialize(self):
        await self.rag_service.initialize()
        await self.ai_service.initialize()
        await self.call_analyzer.initialize()
        await self.script_generator.initialize()
        await self.client_manager.initialize()
    
    async def setup_handlers(self, application: Application):
        application.add_handler(CommandHandler("start", self.start_command))
        application.add_handler(MessageHandler(filters.TEXT, self.handle_message))
        application.add_handler(MessageHandler(filters.VOICE | filters.AUDIO, self.handle_audio))
