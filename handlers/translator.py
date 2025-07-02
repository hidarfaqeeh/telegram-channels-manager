#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Translation Manager Handler
===========================

Handler wrapper for the translation functionality.
This provides a consistent interface for translation operations within the handlers package.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

# Import the actual translation manager from utils
from utils.translator import TranslationManager as UtilsTranslationManager, TranslationResult

logger = logging.getLogger(__name__)

class TranslationManager:
    """
    Translation manager handler for the bot.
    
    This is a wrapper around the utils.translator.TranslationManager
    to provide a consistent interface within the handlers package.
    
    Features:
    - Text translation between languages
    - Language detection
    - Bulk translation
    - Translation caching
    - Multiple translation services support
    """
    
    def __init__(self):
        self.translator = UtilsTranslationManager()
        self.translation_stats = {
            'total_translations': 0,
            'successful_translations': 0,
            'failed_translations': 0,
            'cached_translations': 0,
            'languages_used': set(),
            'last_reset': datetime.now().date()
        }
    
    async def translate_text(self, 
                           text: str, 
                           target_lang: str = "ar",
                           source_lang: str = "auto",
                           service: str = None) -> TranslationResult:
        """
        Translate text to target language
        
        Args:
            text: Text to translate
            target_lang: Target language code
            source_lang: Source language code (auto-detect if "auto")
            service: Translation service to use
            
        Returns:
            TranslationResult: Translation result
        """
        try:
            # Update stats
            self._update_stats('attempt')
            
            # Check cache first
            cache_key = f"{text[:100]}_{source_lang}_{target_lang}_{service}"
            
            # Perform translation
            result = await self.translator.translate_text(
                text=text,
                target_lang=target_lang,
                source_lang=source_lang,
                service=service
            )
            
            # Update stats based on result
            if result.success:
                self._update_stats('success')
                self.translation_stats['languages_used'].add(target_lang)
                if source_lang != "auto":
                    self.translation_stats['languages_used'].add(source_lang)
            else:
                self._update_stats('failed')
            
            logger.debug(f"Translated text: {text[:50]}... -> {result.translated_text[:50] if result.success else 'Failed'}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error in translation handler: {e}")
            self._update_stats('failed')
            return TranslationResult(
                success=False,
                error_message=f"Translation handler error: {str(e)}"
            )
    
    async def translate_bulk(self, 
                           texts: List[str], 
                           target_lang: str = "ar",
                           source_lang: str = "auto") -> List[TranslationResult]:
        """
        Translate multiple texts in bulk
        
        Args:
            texts: List of texts to translate
            target_lang: Target language code
            source_lang: Source language code
            
        Returns:
            List[TranslationResult]: List of translation results
        """
        try:
            results = await self.translator.translate_bulk(
                texts=texts,
                target_lang=target_lang,
                source_lang=source_lang
            )
            
            # Update stats
            for result in results:
                self._update_stats('attempt')
                if result.success:
                    self._update_stats('success')
                else:
                    self._update_stats('failed')
            
            logger.info(f"Bulk translated {len(texts)} texts")
            return results
            
        except Exception as e:
            logger.error(f"Error in bulk translation: {e}")
            return [TranslationResult(
                success=False,
                error_message=f"Bulk translation error: {str(e)}"
            ) for _ in texts]
    
    async def detect_language(self, text: str) -> Optional[str]:
        """
        Detect the language of given text
        
        Args:
            text: Text to analyze
            
        Returns:
            Optional[str]: Detected language code or None
        """
        try:
            return await self.translator.detect_language(text)
        except Exception as e:
            logger.error(f"Error detecting language: {e}")
            return None
    
    def is_rtl_language(self, lang_code: str) -> bool:
        """Check if language is right-to-left"""
        return self.translator.is_rtl_language(lang_code)
    
    def get_supported_languages(self) -> Dict[str, str]:
        """Get list of supported languages"""
        return self.translator.get_supported_languages()
    
    def clear_cache(self):
        """Clear translation cache"""
        self.translator.clear_cache()
        self._update_stats('cache_cleared')
        logger.info("Translation cache cleared")
    
    def get_cache_size(self) -> int:
        """Get current cache size"""
        return self.translator.get_cache_size()
    
    def _update_stats(self, stat_type: str):
        """Update translation statistics"""
        try:
            # Reset daily stats if needed
            today = datetime.now().date()
            if self.translation_stats['last_reset'] != today:
                self.translation_stats.update({
                    'total_translations': 0,
                    'successful_translations': 0,
                    'failed_translations': 0,
                    'cached_translations': 0,
                    'last_reset': today
                })
                # Keep languages_used across days
            
            # Update stats
            if stat_type == 'attempt':
                self.translation_stats['total_translations'] += 1
            elif stat_type == 'success':
                self.translation_stats['successful_translations'] += 1
            elif stat_type == 'failed':
                self.translation_stats['failed_translations'] += 1
            elif stat_type == 'cached':
                self.translation_stats['cached_translations'] += 1
            
        except Exception as e:
            logger.error(f"Error updating translation stats: {e}")
    
    def get_translation_stats(self) -> Dict[str, Any]:
        """
        Get translation statistics
        
        Returns:
            Dict with translation statistics
        """
        try:
            stats = self.translation_stats.copy()
            stats['languages_used'] = list(stats['languages_used'])
            stats['cache_size'] = self.get_cache_size()
            
            # Calculate success rate
            total = stats['total_translations']
            if total > 0:
                stats['success_rate'] = round(
                    (stats['successful_translations'] / total) * 100, 2
                )
            else:
                stats['success_rate'] = 0
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting translation stats: {e}")
            return {}
    
    async def translate_message_auto(self, 
                                   message_text: str,
                                   target_channel_lang: str = "ar") -> TranslationResult:
        """
        Automatically translate a message with smart language detection
        
        Args:
            message_text: Message text to translate
            target_channel_lang: Target language for the channel
            
        Returns:
            TranslationResult: Translation result
        """
        try:
            # Detect source language
            detected_lang = await self.detect_language(message_text)
            
            # Skip translation if already in target language
            if detected_lang == target_channel_lang:
                return TranslationResult(
                    success=True,
                    translated_text=message_text,
                    source_language=detected_lang,
                    target_language=target_channel_lang,
                    confidence=1.0
                )
            
            # Translate
            return await self.translate_text(
                text=message_text,
                target_lang=target_channel_lang,
                source_lang=detected_lang or "auto"
            )
            
        except Exception as e:
            logger.error(f"Error in auto translation: {e}")
            return TranslationResult(
                success=False,
                error_message=f"Auto translation error: {str(e)}"
            )
    
    async def translate_with_fallback(self, 
                                    text: str,
                                    target_lang: str = "ar",
                                    fallback_services: List[str] = None) -> TranslationResult:
        """
        Translate with fallback to other services if primary fails
        
        Args:
            text: Text to translate
            target_lang: Target language
            fallback_services: List of services to try in order
            
        Returns:
            TranslationResult: Best available translation result
        """
        try:
            services = fallback_services or ["google", "deep", "fallback"]
            
            for service in services:
                result = await self.translate_text(
                    text=text,
                    target_lang=target_lang,
                    service=service
                )
                
                if result.success:
                    logger.debug(f"Translation successful with service: {service}")
                    return result
                
                logger.warning(f"Translation failed with {service}: {result.error_message}")
            
            # All services failed
            return TranslationResult(
                success=False,
                error_message="All translation services failed"
            )
            
        except Exception as e:
            logger.error(f"Error in fallback translation: {e}")
            return TranslationResult(
                success=False,
                error_message=f"Fallback translation error: {str(e)}"
            )

# For backward compatibility, create an instance
translation_manager = TranslationManager()

__all__ = ['TranslationManager', 'translation_manager', 'TranslationResult']