"""
Internationalization (i18n) utilities for ComfyUI DCI Extension
"""

import json
import os
import locale
from typing import Dict, Optional


class I18n:
    """Internationalization manager for DCI extension"""

    _instance: Optional['I18n'] = None
    _translations: Dict[str, Dict[str, str]] = {}
    _current_locale: str = "en"

    def __new__(cls) -> 'I18n':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, '_initialized'):
            self._initialized = True
            self._load_translations()
            self._detect_locale()

    def _load_translations(self):
        """Load all translation files from locales directory"""
        current_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        locales_dir = os.path.join(current_dir, 'locales')

        if not os.path.exists(locales_dir):
            print(f"Warning: Locales directory not found: {locales_dir}")
            return

        for filename in os.listdir(locales_dir):
            if filename.endswith('.json'):
                locale_code = filename[:-5]  # Remove .json extension
                file_path = os.path.join(locales_dir, filename)

                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        self._translations[locale_code] = json.load(f)
                    print(f"Loaded translations for locale: {locale_code}")
                except Exception as e:
                    print(f"Error loading translation file {filename}: {e}")

    def _detect_locale(self):
        """Detect system locale and set current locale"""
        try:
            # Try to get system locale
            system_locale = locale.getdefaultlocale()[0]
            if system_locale:
                # Convert system locale format to our format
                if system_locale.startswith('zh'):
                    if 'CN' in system_locale or 'Hans' in system_locale:
                        self._current_locale = "zh-CN"
                    elif 'TW' in system_locale or 'Hant' in system_locale:
                        self._current_locale = "zh-TW"
                    else:
                        self._current_locale = "zh-CN"  # Default to simplified Chinese
                elif system_locale.startswith('en'):
                    self._current_locale = "en"
                else:
                    self._current_locale = "en"  # Default to English
            else:
                self._current_locale = "en"
        except Exception:
            self._current_locale = "en"

        # Check if detected locale is available
        if self._current_locale not in self._translations:
            print(f"Warning: Locale {self._current_locale} not available, falling back to English")
            self._current_locale = "en"

        print(f"Using locale: {self._current_locale}")

    def set_locale(self, locale_code: str):
        """Set current locale manually"""
        if locale_code in self._translations:
            self._current_locale = locale_code
            print(f"Locale changed to: {locale_code}")
        else:
            print(f"Warning: Locale {locale_code} not available")

    def get_current_locale(self) -> str:
        """Get current locale code"""
        return self._current_locale

    def get_available_locales(self) -> list:
        """Get list of available locale codes"""
        return list(self._translations.keys())

    def t(self, key: str, default: Optional[str] = None) -> str:
        """
        Translate a key to current locale

        Args:
            key: Translation key
            default: Default value if translation not found

        Returns:
            Translated string or default value or key itself
        """
        if self._current_locale in self._translations:
            translation = self._translations[self._current_locale].get(key)
            if translation:
                return translation

        # Fallback to English if current locale doesn't have the key
        if self._current_locale != "en" and "en" in self._translations:
            translation = self._translations["en"].get(key)
            if translation:
                return translation

        # Return default or key itself
        return default if default is not None else key

    def has_translation(self, key: str) -> bool:
        """Check if a translation exists for the given key"""
        if self._current_locale in self._translations:
            if key in self._translations[self._current_locale]:
                return True

        # Check fallback English
        if "en" in self._translations:
            return key in self._translations["en"]

        return False


# Global instance
_i18n = I18n()

# Convenience function for translation
def t(key: str, default: Optional[str] = None) -> str:
    """
    Translate a key to current locale

    Args:
        key: Translation key
        default: Default value if translation not found

    Returns:
        Translated string
    """
    return _i18n.t(key, default)

# Convenience function to get i18n instance
def get_i18n() -> I18n:
    """Get the global i18n instance"""
    return _i18n
