"""Translation system for ClaudeCode-Debugger."""

import json
import locale
import os
from pathlib import Path
from typing import Dict, Optional

class Translator:
    """Handle translations for multiple languages."""
    
    def __init__(self, language: Optional[str] = None):
        """Initialize translator with specified or detected language."""
        self.language = language or self._detect_language()
        self.translations = self._load_translations()
        
    def _detect_language(self) -> str:
        """Detect system language, default to English."""
        # Check environment variable first
        env_lang = os.environ.get('CCDEBUG_LANG')
        if env_lang:
            return env_lang
            
        # Check system locale
        try:
            system_lang = locale.getdefaultlocale()[0]
            if system_lang and system_lang.startswith('zh'):
                return 'zh'
        except:
            pass
            
        return 'en'
    
    def _load_translations(self) -> Dict:
        """Load translation files."""
        translations_dir = Path(__file__).parent / 'locales' / self.language
        messages_file = translations_dir / 'messages.json'
        
        # Fallback to English if translation file doesn't exist
        if not messages_file.exists():
            translations_dir = Path(__file__).parent / 'locales' / 'en'
            messages_file = translations_dir / 'messages.json'
            
        try:
            with open(messages_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            # Return empty dict if no translations found
            return {}
    
    def get(self, key: str, **kwargs) -> str:
        """Get translated message with optional formatting."""
        message = self.translations.get(key, key)
        
        # Apply formatting if kwargs provided
        if kwargs:
            try:
                return message.format(**kwargs)
            except:
                return message
                
        return message
    
    def __call__(self, key: str, **kwargs) -> str:
        """Allow translator to be called directly."""
        return self.get(key, **kwargs)


# Global translator instance
_translator: Optional[Translator] = None


def get_translator(language: Optional[str] = None) -> Translator:
    """Get or create global translator instance."""
    global _translator
    
    if _translator is None or (language and language != _translator.language):
        _translator = Translator(language)
        
    return _translator


def set_language(language: str):
    """Set global language preference."""
    global _translator
    _translator = Translator(language)