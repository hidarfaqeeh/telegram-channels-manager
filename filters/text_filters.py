#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Text Filters Module
==================

Advanced text filtering capabilities for the Telegram bot.
Provides comprehensive text analysis, filtering, and content moderation.
"""

import re
import logging
from typing import List, Dict, Any, Optional, Tuple, Set
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class FilterResult:
    """Result of text filtering operation"""
    passed: bool
    reason: str = ""
    score: float = 0.0
    matched_patterns: List[str] = None
    suggestions: List[str] = None
    
    def __post_init__(self):
        if self.matched_patterns is None:
            self.matched_patterns = []
        if self.suggestions is None:
            self.suggestions = []

class TextFilterManager:
    """
    Advanced text filtering and analysis manager.
    
    Provides various filtering capabilities including:
    - Blacklist/whitelist word filtering
    - Pattern matching
    - Language detection
    - Spam detection
    - Content quality analysis
    - Profanity filtering
    """
    
    def __init__(self):
        self.blacklist_words: Set[str] = set()
        self.whitelist_words: Set[str] = set()
        self.blacklist_patterns: List[re.Pattern] = []
        self.whitelist_patterns: List[re.Pattern] = []
        self.spam_patterns: List[re.Pattern] = []
        self.profanity_words: Set[str] = set()
        
        # Initialize default patterns
        self._init_default_patterns()
        self._init_spam_patterns()
        self._init_profanity_words()
    
    def _init_default_patterns(self):
        """Initialize default filtering patterns"""
        # Common spam patterns
        spam_patterns = [
            r'(?i)click\s+here',
            r'(?i)free\s+money',
            r'(?i)make\s+money\s+fast',
            r'(?i)viagra|cialis',
            r'(?i)weight\s+loss',
            r'(?i)get\s+rich\s+quick',
            r'(?i)no\s+questions\s+asked',
            r'(?i)limited\s+time\s+offer',
            r'(?i)act\s+now',
            r'(?i)call\s+now',
        ]
        
        for pattern in spam_patterns:
            try:
                self.spam_patterns.append(re.compile(pattern))
            except re.error:
                logger.warning(f"Invalid spam pattern: {pattern}")
    
    def _init_spam_patterns(self):
        """Initialize spam detection patterns"""
        patterns = [
            # Excessive capitalization
            r'[A-Z]{5,}',
            # Excessive punctuation
            r'[!?]{3,}',
            # Multiple consecutive dots
            r'\.{4,}',
            # Excessive emojis
            r'[\U0001F600-\U0001F64F]{3,}',
            # Suspicious URLs
            r'bit\.ly|tinyurl|goo\.gl',
            # Phone numbers (possible spam)
            r'\+?\d{10,15}',
            # Email addresses (potential spam)
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        ]
        
        for pattern in patterns:
            try:
                self.spam_patterns.append(re.compile(pattern))
            except re.error:
                logger.warning(f"Invalid pattern: {pattern}")
    
    def _init_profanity_words(self):
        """Initialize basic profanity word list"""
        # Basic profanity words (add more as needed)
        basic_profanity = {
            'spam', 'scam', 'fake', 'fraud', 'cheat', 'hack', 'virus',
            'malware', 'phishing', 'clickbait', 'misleading'
        }
        self.profanity_words.update(basic_profanity)
    
    def add_blacklist_words(self, words: List[str]):
        """Add words to blacklist"""
        for word in words:
            self.blacklist_words.add(word.lower().strip())
        logger.info(f"Added {len(words)} words to blacklist")
    
    def add_whitelist_words(self, words: List[str]):
        """Add words to whitelist"""
        for word in words:
            self.whitelist_words.add(word.lower().strip())
        logger.info(f"Added {len(words)} words to whitelist")
    
    def add_blacklist_pattern(self, pattern: str):
        """Add regex pattern to blacklist"""
        try:
            compiled_pattern = re.compile(pattern, re.IGNORECASE)
            self.blacklist_patterns.append(compiled_pattern)
            logger.info(f"Added blacklist pattern: {pattern}")
        except re.error as e:
            logger.error(f"Invalid regex pattern '{pattern}': {e}")
    
    def add_whitelist_pattern(self, pattern: str):
        """Add regex pattern to whitelist"""
        try:
            compiled_pattern = re.compile(pattern, re.IGNORECASE)
            self.whitelist_patterns.append(compiled_pattern)
            logger.info(f"Added whitelist pattern: {pattern}")
        except re.error as e:
            logger.error(f"Invalid regex pattern '{pattern}': {e}")
    
    def filter_text(self, text: str, strict_mode: bool = False) -> FilterResult:
        """
        Comprehensive text filtering
        
        Args:
            text: Text to filter
            strict_mode: Whether to use strict filtering
            
        Returns:
            FilterResult: Filtering result
        """
        if not text or not isinstance(text, str):
            return FilterResult(passed=False, reason="Empty or invalid text")
        
        text_lower = text.lower()
        matched_patterns = []
        score = 0.0
        
        # Check whitelist first (if whitelisted, allow regardless of other filters)
        if self._check_whitelist(text, text_lower):
            return FilterResult(passed=True, reason="Whitelisted content")
        
        # Check blacklist words
        blacklist_result = self._check_blacklist_words(text_lower)
        if not blacklist_result[0]:
            matched_patterns.extend(blacklist_result[1])
            score += 30
        
        # Check blacklist patterns
        pattern_result = self._check_blacklist_patterns(text)
        if not pattern_result[0]:
            matched_patterns.extend(pattern_result[1])
            score += 25
        
        # Check for spam
        spam_result = self._check_spam_patterns(text)
        if not spam_result[0]:
            matched_patterns.extend(spam_result[1])
            score += 20
        
        # Check profanity
        profanity_result = self._check_profanity(text_lower)
        if not profanity_result[0]:
            matched_patterns.extend(profanity_result[1])
            score += 15
        
        # Additional quality checks
        quality_score = self._analyze_text_quality(text)
        score += quality_score
        
        # Determine if text passes based on score and strict mode
        threshold = 50 if strict_mode else 70
        passed = score < threshold
        
        reason = self._generate_reason(matched_patterns, score, strict_mode)
        
        return FilterResult(
            passed=passed,
            reason=reason,
            score=score,
            matched_patterns=matched_patterns,
            suggestions=self._generate_suggestions(matched_patterns)
        )
    
    def _check_whitelist(self, text: str, text_lower: str) -> bool:
        """Check if text matches whitelist criteria"""
        # Check whitelist words
        for word in self.whitelist_words:
            if word in text_lower:
                return True
        
        # Check whitelist patterns
        for pattern in self.whitelist_patterns:
            if pattern.search(text):
                return True
        
        return False
    
    def _check_blacklist_words(self, text_lower: str) -> Tuple[bool, List[str]]:
        """Check text against blacklist words"""
        matched_words = []
        
        for word in self.blacklist_words:
            if word in text_lower:
                matched_words.append(f"blacklist_word:{word}")
        
        return len(matched_words) == 0, matched_words
    
    def _check_blacklist_patterns(self, text: str) -> Tuple[bool, List[str]]:
        """Check text against blacklist patterns"""
        matched_patterns = []
        
        for pattern in self.blacklist_patterns:
            if pattern.search(text):
                matched_patterns.append(f"blacklist_pattern:{pattern.pattern}")
        
        return len(matched_patterns) == 0, matched_patterns
    
    def _check_spam_patterns(self, text: str) -> Tuple[bool, List[str]]:
        """Check text for spam patterns"""
        matched_patterns = []
        
        for pattern in self.spam_patterns:
            matches = pattern.findall(text)
            if matches:
                matched_patterns.append(f"spam_pattern:{pattern.pattern}")
        
        return len(matched_patterns) == 0, matched_patterns
    
    def _check_profanity(self, text_lower: str) -> Tuple[bool, List[str]]:
        """Check text for profanity"""
        matched_words = []
        
        words = re.findall(r'\b\w+\b', text_lower)
        for word in words:
            if word in self.profanity_words:
                matched_words.append(f"profanity:{word}")
        
        return len(matched_words) == 0, matched_words
    
    def _analyze_text_quality(self, text: str) -> float:
        """Analyze text quality and return penalty score"""
        penalty = 0.0
        
        # Check for excessive capitalization
        if len(re.findall(r'[A-Z]', text)) / len(text) > 0.5:
            penalty += 10
        
        # Check for excessive punctuation
        punct_count = len(re.findall(r'[!?.,;:]', text))
        if punct_count / len(text) > 0.3:
            penalty += 10
        
        # Check for repetitive characters
        if re.search(r'(.)\1{4,}', text):
            penalty += 15
        
        # Check for very short or very long messages
        if len(text.strip()) < 5:
            penalty += 20
        elif len(text) > 4000:
            penalty += 10
        
        # Check for excessive emojis
        emoji_count = len(re.findall(r'[\U0001F600-\U0001F64F]', text))
        if emoji_count > 10 or (emoji_count / len(text) > 0.1 and len(text) > 50):
            penalty += 15
        
        return penalty
    
    def _generate_reason(self, matched_patterns: List[str], score: float, strict_mode: bool) -> str:
        """Generate human-readable reason for filtering result"""
        if not matched_patterns and score < (50 if strict_mode else 70):
            return "Content passed all filters"
        
        reasons = []
        
        # Categorize matched patterns
        blacklist_words = [p for p in matched_patterns if p.startswith('blacklist_word:')]
        blacklist_patterns = [p for p in matched_patterns if p.startswith('blacklist_pattern:')]
        spam_patterns = [p for p in matched_patterns if p.startswith('spam_pattern:')]
        profanity = [p for p in matched_patterns if p.startswith('profanity:')]
        
        if blacklist_words:
            reasons.append(f"Contains blacklisted words: {len(blacklist_words)} matches")
        
        if blacklist_patterns:
            reasons.append(f"Matches blacklisted patterns: {len(blacklist_patterns)} matches")
        
        if spam_patterns:
            reasons.append(f"Contains spam indicators: {len(spam_patterns)} matches")
        
        if profanity:
            reasons.append(f"Contains inappropriate content: {len(profanity)} matches")
        
        if score >= (50 if strict_mode else 70):
            reasons.append(f"Quality score too low: {score:.1f}")
        
        return "; ".join(reasons) if reasons else "Content quality issues detected"
    
    def _generate_suggestions(self, matched_patterns: List[str]) -> List[str]:
        """Generate suggestions for improving content"""
        suggestions = []
        
        if any('spam_pattern' in p for p in matched_patterns):
            suggestions.append("Remove excessive punctuation and capitalization")
            suggestions.append("Avoid suspicious links and contact information")
        
        if any('profanity' in p for p in matched_patterns):
            suggestions.append("Use appropriate language")
            suggestions.append("Review content for professional tone")
        
        if any('blacklist' in p for p in matched_patterns):
            suggestions.append("Remove or replace flagged words/phrases")
            suggestions.append("Ensure content complies with community guidelines")
        
        # Add general suggestions
        suggestions.extend([
            "Keep messages concise and relevant",
            "Use proper grammar and spelling",
            "Avoid excessive emojis and special characters"
        ])
        
        return list(set(suggestions))  # Remove duplicates
    
    def check_language(self, text: str, allowed_languages: List[str] = None) -> Tuple[bool, str]:
        """
        Check if text is in allowed language(s)
        
        Args:
            text: Text to check
            allowed_languages: List of allowed language codes
            
        Returns:
            Tuple[bool, str]: (is_allowed, detected_language)
        """
        if not allowed_languages:
            return True, "any"
        
        try:
            from langdetect import detect
            detected_lang = detect(text)
            is_allowed = detected_lang in allowed_languages
            return is_allowed, detected_lang
        except ImportError:
            logger.warning("langdetect not available, skipping language check")
            return True, "unknown"
        except Exception as e:
            logger.error(f"Language detection error: {e}")
            return True, "error"
    
    def get_text_statistics(self, text: str) -> Dict[str, Any]:
        """
        Get comprehensive text statistics
        
        Args:
            text: Text to analyze
            
        Returns:
            Dict containing various text statistics
        """
        stats = {
            'character_count': len(text),
            'word_count': len(re.findall(r'\b\w+\b', text)),
            'sentence_count': len(re.findall(r'[.!?]+', text)),
            'paragraph_count': len(text.split('\n\n')),
            'line_count': len(text.split('\n')),
            'emoji_count': len(re.findall(r'[\U0001F600-\U0001F64F]', text)),
            'url_count': len(re.findall(r'http[s]?://\S+', text)),
            'mention_count': len(re.findall(r'@\w+', text)),
            'hashtag_count': len(re.findall(r'#\w+', text)),
            'uppercase_ratio': len(re.findall(r'[A-Z]', text)) / len(text) if text else 0,
            'punctuation_ratio': len(re.findall(r'[!?.,;:]', text)) / len(text) if text else 0,
        }
        
        return stats
    
    def clean_text(self, text: str, aggressive: bool = False) -> str:
        """
        Clean text by removing or replacing unwanted content
        
        Args:
            text: Text to clean
            aggressive: Whether to use aggressive cleaning
            
        Returns:
            str: Cleaned text
        """
        if not text:
            return ""
        
        cleaned = text
        
        # Remove excessive whitespace
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        
        # Remove excessive punctuation
        cleaned = re.sub(r'[!?]{3,}', '!', cleaned)
        cleaned = re.sub(r'[.]{4,}', '...', cleaned)
        
        # Remove excessive capitalization
        cleaned = re.sub(r'[A-Z]{5,}', lambda m: m.group().capitalize(), cleaned)
        
        if aggressive:
            # Remove URLs
            cleaned = re.sub(r'http[s]?://\S+', '[URL]', cleaned)
            
            # Remove email addresses
            cleaned = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL]', cleaned)
            
            # Remove phone numbers
            cleaned = re.sub(r'\+?\d{10,15}', '[PHONE]', cleaned)
            
            # Limit emojis
            cleaned = re.sub(r'([\U0001F600-\U0001F64F])\1{2,}', r'\1\1', cleaned)
        
        return cleaned.strip()
    
    def export_settings(self) -> Dict[str, Any]:
        """Export current filter settings"""
        return {
            'blacklist_words': list(self.blacklist_words),
            'whitelist_words': list(self.whitelist_words),
            'blacklist_patterns': [p.pattern for p in self.blacklist_patterns],
            'whitelist_patterns': [p.pattern for p in self.whitelist_patterns],
            'profanity_words': list(self.profanity_words),
            'exported_at': datetime.now().isoformat()
        }
    
    def import_settings(self, settings: Dict[str, Any]):
        """Import filter settings"""
        try:
            if 'blacklist_words' in settings:
                self.blacklist_words = set(settings['blacklist_words'])
            
            if 'whitelist_words' in settings:
                self.whitelist_words = set(settings['whitelist_words'])
            
            if 'blacklist_patterns' in settings:
                self.blacklist_patterns = []
                for pattern in settings['blacklist_patterns']:
                    try:
                        self.blacklist_patterns.append(re.compile(pattern, re.IGNORECASE))
                    except re.error:
                        logger.warning(f"Skipped invalid pattern: {pattern}")
            
            if 'whitelist_patterns' in settings:
                self.whitelist_patterns = []
                for pattern in settings['whitelist_patterns']:
                    try:
                        self.whitelist_patterns.append(re.compile(pattern, re.IGNORECASE))
                    except re.error:
                        logger.warning(f"Skipped invalid pattern: {pattern}")
            
            if 'profanity_words' in settings:
                self.profanity_words = set(settings['profanity_words'])
            
            logger.info("Filter settings imported successfully")
            
        except Exception as e:
            logger.error(f"Error importing filter settings: {e}")

__all__ = ['TextFilterManager', 'FilterResult']