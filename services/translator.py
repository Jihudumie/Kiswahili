from deep_translator import GoogleTranslator
from config import TRANSLATION_SOURCE, TRANSLATION_TARGET


class TranslatorService:
    def __init__(self):
        self.translator = GoogleTranslator(
            source=TRANSLATION_SOURCE,
            target=TRANSLATION_TARGET
        )
    
    def translate(self, text: str) -> str:
        """Translate text and apply custom replacements"""
        if not text:
            return ""
        
        translated = self.translator.translate(text)
        # Custom replacements
        translated = translated.replace("Mwenyezi Mungu", "Allah")
        
        return translated
    
    def should_translate(self, original: str, translated: str) -> bool:
        """Check if translation is different from original"""
        return translated.strip() != original.strip()


# Global instance
translator_service = TranslatorServic
