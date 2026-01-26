import re
from deep_translator import GoogleTranslator
from config import TRANSLATION_SOURCE, TRANSLATION_TARGET


# Pattern ya kukata maandishi kabla ya social media links
Kata = re.compile(r"🔗\s*(Telegram|X|WhatsApp|Instagram|Facebook|YouTube|TikTok)")


class TranslatorService:
    def __init__(self):
        self.translator = GoogleTranslator(
            source=TRANSLATION_SOURCE,
            target=TRANSLATION_TARGET
        )
        
        # Pattern ya kutambua hashtags
        self.hashtag_pattern = re.compile(r'#\w+')
    
    def translate(self, text: str) -> str:
        """
        Tafsiri maandishi na fanya marekebisho maalum baada ya tafsiri
        """
        if not text:
            return ""
        
        # Kata maandishi kabla ya social media links
        text = Kata.split(text, 1)[0].strip()
        
        # Hifadhi hashtags kabla ya kutafsiri
        protected_hashtags = {}
        counter = 0
        
        def replace_hashtag(match):
            nonlocal counter
            placeholder = f"___HASHTAG{counter}___"
            protected_hashtags[placeholder] = match.group(0)
            counter += 1
            return placeholder
        
        # Badilisha hashtags kwa placeholders
        text_with_placeholders = self.hashtag_pattern.sub(replace_hashtag, text)
        
        # Tafsiri maandishi yenye placeholders
        translated = self.translator.translate(text_with_placeholders)
        
        # Rudisha hashtags za asili
        for placeholder, original_hashtag in protected_hashtags.items():
            translated = translated.replace(placeholder, original_hashtag)

        # Marekebisho maalum
        translated = translated.replace("Mwenyezi Mungu", "Allah")
        
        return translated
    
    def should_translate(self, original: str, translated: str) -> bool:
        """
        Kagua kama tafsiri ni tofauti na maandishi ya awali
        """
        return translated.strip() != original.strip()


# Instance ya global
translator_service = TranslatorService()
