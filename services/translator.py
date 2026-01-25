from deep_translator import GoogleTranslator
from config import TRANSLATION_SOURCE, TRANSLATION_TARGET
import re


class TranslatorService:
    def __init__(self):
        self.translator = GoogleTranslator(
            source=TRANSLATION_SOURCE,
            target=TRANSLATION_TARGET
        )
        
        # Pattern ya kutambua mistari yote ya social media
        self.social_media_pattern = re.compile(
            r'🔗\s*(Telegram|X|WhatsApp|Instagram|Facebook|YouTube|TikTok|Twitter):\s*.*',
            re.IGNORECASE
        )
        
        # Pattern ya kutambua hashtags
        self.hashtag_pattern = re.compile(r'#\w+')
    
    def _remove_social_links(self, text: str) -> str:
        """Ondoa mistari yote ya viungo vya social media"""
        text = self.social_media_pattern.sub('', text)
        lines = [line for line in text.split('\n') if line.strip()]
        return '\n'.join(lines)
    
    def _extract_hashtags(self, text: str) -> tuple[str, dict]:
        """Ondoa hashtags kabla ya kutafsiri"""
        protected = {}
        counter = 0
        
        def replace_hashtag(match):
            nonlocal counter
            placeholder = f"___HASHTAG{counter}___"
            protected[placeholder] = match.group(0)
            counter += 1
            return placeholder
        
        text = self.hashtag_pattern.sub(replace_hashtag, text)
        return text, protected
    
    def _restore_hashtags(self, text: str, protected: dict) -> str:
        """Rudisha hashtags zilizohifadhiwa"""
        for placeholder, original in protected.items():
            text = text.replace(placeholder, original)
        return text
    
    def _preserve_newlines(self, text: str) -> tuple[str, list]:
        """
        Hifadhi mistari mipya kwa kubadilisha kuwa placeholders
        Rudisha text iliyobadilishwa na orodha ya positions
        """
        # Hifadhi aya (mistari mipya maradufu)
        text = text.replace('\n\n', '___PARAGRAPH___')
        
        # Hifadhi mistari mipya ya kawaida
        text = text.replace('\n', '___NEWLINE___')
        
        return text
    
    def _restore_newlines(self, text: str) -> str:
        """Rudisha mistari mipya"""
        # Rudisha kwa mpangilio sahihi
        text = text.replace('___PARAGRAPH___', '\n\n')
        text = text.replace('___NEWLINE___', '\n')
        return text
    
    def translate(self, text: str) -> str:
        """
        Tafsiri maandishi na fanya marekebisho maalum baada ya tafsiri
        """
        if not text:
            return ""
        
        # HATUA 1: Ondoa mistari yote ya social media links
        text = self._remove_social_links(text)
        
        # HATUA 2: Hifadhi mistari mipya
        text = self._preserve_newlines(text)
        
        # HATUA 3: Ondoa na hifadhi hashtags
        cleaned_text, protected_hashtags = self._extract_hashtags(text)
        
        # HATUA 4: Tafsiri maandishi iliyosafishwa
        try:
            translated = self.translator.translate(cleaned_text)
        except Exception as e:
            # Kama tafsiri imeshindwa, rudisha text ya awali
            print(f"Translation error: {e}")
            return text
        
        # HATUA 5: Rudisha mistari mipya
        translated = self._restore_newlines(translated)
        
        # HATUA 6: Rudisha hashtags
        translated = self._restore_hashtags(translated, protected_hashtags)

        # HATUA 7: Marekebisho maalum ya maneno baada ya tafsiri
        translated = translated.replace("Mwenyezi Mungu", "Allah")
        
        # HATUA 8: Safisha nafasi za ziada (bila kuathiri mistari mipya)
        # Ondoa nafasi nyingi za mfululizo katika mstari mmoja
        lines = translated.split('\n')
        cleaned_lines = [re.sub(r' {2,}', ' ', line.strip()) for line in lines]
        translated = '\n'.join(cleaned_lines)
        
        return translated.strip()
    
    def should_translate(self, original: str, translated: str) -> bool:
        """
        Kagua kama tafsiri ni tofauti na maandishi ya awali
        """
        return translated.strip() != original.strip()


# Instance ya pamoja (global) ya TranslatorService
translator_service = TranslatorService()
