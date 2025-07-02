#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
from typing import Optional
from deep_translator import GoogleTranslator
from langdetect import detect, LangDetectError

logger = logging.getLogger(__name__)

class TranslationManager:
    def __init__(self, db):
        self.db = db
        self.translator = GoogleTranslator()
    
    async def translate_text(self, text: str, target_language: str = 'ar') -> str:
        """Translate text to target language"""
        try:
            if not text or not text.strip():
                return text
            
            # Detect source language
            try:
                source_lang = detect(text)
                if source_lang == target_language:
                    return text  # Already in target language
            except LangDetectError:
                source_lang = 'auto'
            
            # Translate
            translated = GoogleTranslator(source=source_lang, target=target_language).translate(text)
            return translated or text
            
        except Exception as e:
            logger.error(f"Error translating text: {e}")
            return text
    
    async def detect_language(self, text: str) -> Optional[str]:
        """Detect text language"""
        try:
            return detect(text)
        except Exception as e:
            logger.error(f"Error detecting language: {e}")
            return None