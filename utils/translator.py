#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Translation Module
=================

Provides automatic translation capabilities for the Telegram bot.
Supports multiple translation services and languages.
"""

import logging
import asyncio
from typing import Optional, Dict, Any, List, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class TranslationResult:
    """Result of translation operation"""
    success: bool
    translated_text: str = ""
    source_language: str = ""
    target_language: str = ""
    confidence: float = 0.0
    error_message: str = ""

class TranslationManager:
    """
    Advanced translation manager supporting multiple services.
    
    Supports:
    - Google Translate
    - Deep Translator
    - Language detection
    - Bulk translation
    - Translation caching
    """
    
    def __init__(self, default_service: str = "google", default_target: str = "ar"):
        self.default_service = default_service
        self.default_target = default_target
        self.translation_cache: Dict[str, TranslationResult] = {}
        self.supported_languages = {
            'ar': 'Arabic',
            'en': 'English', 
            'es': 'Spanish',
            'fr': 'French',
            'de': 'German',
            'it': 'Italian',
            'pt': 'Portuguese',
            'ru': 'Russian',
            'zh': 'Chinese',
            'ja': 'Japanese',
            'ko': 'Korean',
            'hi': 'Hindi',
            'tr': 'Turkish',
            'fa': 'Persian',
            'ur': 'Urdu',
            'bn': 'Bengali'
        }
    
    async def detect_language(self, text: str) -> Optional[str]:
        """
        Detect the language of given text.
        
        Args:
            text: Text to analyze
            
        Returns:
            Optional[str]: Detected language code or None
        """
        if not text or len(text.strip()) < 3:
            return None
            
        try:
            from langdetect import detect
            detected = detect(text)
            return detected if detected in self.supported_languages else None
        except ImportError:
            logger.warning("langdetect not available")
            return None
        except Exception as e:
            logger.error(f"Language detection error: {e}")
            return None
    
    async def translate_text(self, 
                           text: str, 
                           target_lang: str = None,
                           source_lang: str = "auto",
                           service: str = None) -> TranslationResult:
        """
        Translate text to target language.
        
        Args:
            text: Text to translate
            target_lang: Target language code
            source_lang: Source language code (auto-detect if "auto")
            service: Translation service to use
            
        Returns:
            TranslationResult: Translation result
        """
        if not text or not text.strip():
            return TranslationResult(
                success=False,
                error_message="Empty text provided"
            )
        
        target_lang = target_lang or self.default_target
        service = service or self.default_service
        
        # Check cache first
        cache_key = f"{text[:100]}_{source_lang}_{target_lang}_{service}"
        if cache_key in self.translation_cache:
            return self.translation_cache[cache_key]
        
        # Detect source language if auto
        if source_lang == "auto":
            detected = await self.detect_language(text)
            source_lang = detected or "en"
        
        # Skip translation if same language
        if source_lang == target_lang:
            result = TranslationResult(
                success=True,
                translated_text=text,
                source_language=source_lang,
                target_language=target_lang,
                confidence=1.0
            )
            self.translation_cache[cache_key] = result
            return result
        
        # Try translation services
        result = None
        if service == "google":
            result = await self._translate_with_google(text, target_lang, source_lang)
        elif service == "deep":
            result = await self._translate_with_deep(text, target_lang, source_lang)
        else:
            # Fallback to google
            result = await self._translate_with_google(text, target_lang, source_lang)
        
        if result and result.success:
            self.translation_cache[cache_key] = result
        
        return result or TranslationResult(
            success=False,
            error_message="Translation failed with all services"
        )
    
    async def _translate_with_google(self, 
                                   text: str, 
                                   target_lang: str, 
                                   source_lang: str) -> TranslationResult:
        """Translate using Google Translate"""
        try:
            from googletrans import Translator
            translator = Translator()
            
            # Run in thread to avoid blocking
            loop = asyncio.get_event_loop()
            translation = await loop.run_in_executor(
                None, 
                lambda: translator.translate(text, dest=target_lang, src=source_lang)
            )
            
            return TranslationResult(
                success=True,
                translated_text=translation.text,
                source_language=translation.src,
                target_language=target_lang,
                confidence=getattr(translation, 'confidence', 0.9)
            )
            
        except ImportError:
            logger.warning("googletrans not available")
            return await self._translate_with_deep(text, target_lang, source_lang)
        except Exception as e:
            logger.error(f"Google translation error: {e}")
            return TranslationResult(
                success=False,
                error_message=f"Google translation failed: {str(e)}"
            )
    
    async def _translate_with_deep(self, 
                                 text: str, 
                                 target_lang: str, 
                                 source_lang: str) -> TranslationResult:
        """Translate using Deep Translator"""
        try:
            from deep_translator import GoogleTranslator
            
            # Map language codes
            source = source_lang if source_lang != "auto" else None
            
            translator = GoogleTranslator(source=source, target=target_lang)
            
            # Run in thread to avoid blocking
            loop = asyncio.get_event_loop()
            translated = await loop.run_in_executor(
                None,
                translator.translate,
                text
            )
            
            return TranslationResult(
                success=True,
                translated_text=translated,
                source_language=source_lang,
                target_language=target_lang,
                confidence=0.85
            )
            
        except ImportError:
            logger.warning("deep-translator not available")
            return await self._translate_with_fallback(text, target_lang, source_lang)
        except Exception as e:
            logger.error(f"Deep translator error: {e}")
            return TranslationResult(
                success=False,
                error_message=f"Deep translation failed: {str(e)}"
            )
    
    async def _translate_with_fallback(self, 
                                     text: str, 
                                     target_lang: str, 
                                     source_lang: str) -> TranslationResult:
        """Fallback translation using simple rules"""
        try:
            # Simple Arabic/English fallback
            if target_lang == "ar" and source_lang == "en":
                # Basic English to Arabic patterns
                replacements = {
                    "hello": "مرحبا",
                    "hi": "أهلا",
                    "thanks": "شكرا",
                    "yes": "نعم",
                    "no": "لا",
                    "good": "جيد",
                    "bad": "سيء",
                    "news": "أخبار",
                    "channel": "قناة",
                    "message": "رسالة",
                    "welcome": "أهلا وسهلا"
                }
                
                translated = text.lower()
                for en, ar in replacements.items():
                    translated = translated.replace(en, ar)
                
                return TranslationResult(
                    success=True,
                    translated_text=translated,
                    source_language=source_lang,
                    target_language=target_lang,
                    confidence=0.5
                )
            
            elif target_lang == "en" and source_lang == "ar":
                # Basic Arabic to English patterns
                replacements = {
                    "مرحبا": "hello",
                    "أهلا": "hi", 
                    "شكرا": "thanks",
                    "نعم": "yes",
                    "لا": "no",
                    "جيد": "good",
                    "سيء": "bad",
                    "أخبار": "news",
                    "قناة": "channel",
                    "رسالة": "message"
                }
                
                translated = text
                for ar, en in replacements.items():
                    translated = translated.replace(ar, en)
                
                return TranslationResult(
                    success=True,
                    translated_text=translated,
                    source_language=source_lang,
                    target_language=target_lang,
                    confidence=0.5
                )
            
            # If no patterns match, return original
            return TranslationResult(
                success=True,
                translated_text=text,
                source_language=source_lang,
                target_language=target_lang,
                confidence=0.3
            )
            
        except Exception as e:
            logger.error(f"Fallback translation error: {e}")
            return TranslationResult(
                success=False,
                error_message=f"Fallback translation failed: {str(e)}"
            )
    
    async def translate_bulk(self, 
                           texts: List[str], 
                           target_lang: str = None,
                           source_lang: str = "auto") -> List[TranslationResult]:
        """
        Translate multiple texts in bulk.
        
        Args:
            texts: List of texts to translate
            target_lang: Target language code
            source_lang: Source language code
            
        Returns:
            List[TranslationResult]: List of translation results
        """
        target_lang = target_lang or self.default_target
        
        tasks = []
        for text in texts:
            task = self.translate_text(text, target_lang, source_lang)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle exceptions
        final_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                final_results.append(TranslationResult(
                    success=False,
                    error_message=f"Translation failed: {str(result)}"
                ))
            else:
                final_results.append(result)
        
        return final_results
    
    def is_rtl_language(self, lang_code: str) -> bool:
        """Check if language is right-to-left"""
        rtl_languages = {'ar', 'he', 'fa', 'ur', 'ps', 'sd'}
        return lang_code in rtl_languages
    
    def get_supported_languages(self) -> Dict[str, str]:
        """Get list of supported languages"""
        return self.supported_languages.copy()
    
    def clear_cache(self):
        """Clear translation cache"""
        self.translation_cache.clear()
        logger.info("Translation cache cleared")
    
    def get_cache_size(self) -> int:
        """Get current cache size"""
        return len(self.translation_cache)

# Global instance
translator = TranslationManager()

__all__ = ['TranslationManager', 'TranslationResult', 'translator']