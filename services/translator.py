from deep_translator import GoogleTranslator
from config import TRANSLATION_SOURCE, TRANSLATION_TARGET
import re


class TranslatorService:
    def __init__(self):
        # Tengeneza kifaa cha kutafsiri kwa kutumia GoogleTranslator
        # source = lugha ya awali
        # target = lugha lengwa
        self.translator = GoogleTranslator(
            source=TRANSLATION_SOURCE,
            target=TRANSLATION_TARGET
        )
        
        # Pattern ya kutambua viungo vya social media
        self.social_media_pattern = re.compile(
            r'🔗\s*(Telegram|X|WhatsApp|Instagram|Facebook|YouTube|TikTok|Twitter):\s*\S+',
            re.IGNORECASE
        )
        
        # Pattern ya kutambua hashtags
        self.hashtag_pattern = re.compile(r'#\w+')
    
    def _extract_protected_content(self, text: str) -> tuple[str, dict]:
        """
        Ondoa viungo vya social media na hashtags kabla ya kutafsiri
        Rudisha text iliyosafishwa na dictionary ya kumbukumbu
        """
        protected = {}
        counter = 0
        
        # Hifadhi viungo vya social media
        def replace_social_link(match):
            nonlocal counter
            placeholder = f"___SOCIALLINK{counter}___"
            protected[placeholder] = match.group(0)
            counter += 1
            return placeholder
        
        text = self.social_media_pattern.sub(replace_social_link, text)
        
        # Hifadhi hashtags
        def replace_hashtag(match):
            nonlocal counter
            placeholder = f"___HASHTAG{counter}___"
            protected[placeholder] = match.group(0)
            counter += 1
            return placeholder
        
        text = self.hashtag_pattern.sub(replace_hashtag, text)
        
        return text, protected
    
    def _restore_protected_content(self, text: str, protected: dict) -> str:
        """
        Rudisha viungo na hashtags zilizohifadhiwa
        """
        for placeholder, original in protected.items():
            text = text.replace(placeholder, original)
        return text
    
    def translate(self, text: str) -> str:
        """
        Tafsiri maandishi na fanya marekebisho maalum baada ya tafsiri
        """
        # Kama hakuna maandishi, rudisha maandishi tupu
        if not text:
            return ""
        
        # Ondoa na hifadhi social media links na hashtags
        cleaned_text, protected_content = self._extract_protected_content(text)
        
        # Tafsiri maandishi iliyosafishwa kwa kutumia Google Translator
        translated = self.translator.translate(cleaned_text)
        
        # Rudisha social media links na hashtags
        translated = self._restore_protected_content(translated, protected_content)

        # Marekebisho maalum ya maneno baada ya tafsiri
        # Badilisha "Mwenyezi Mungu" kuwa "Allah"
        translated = translated.replace("Mwenyezi Mungu", "Allah")
        
        return translated
    
    def should_translate(self, original: str, translated: str) -> bool:
        """
        Kagua kama tafsiri ni tofauti na maandishi ya awali
        Inarudisha True kama kuna tofauti, vinginevyo False
        """
        return translated.strip() != original.strip()


'''Instance ya pamoja (global) ya TranslatorService'''
# Inatumika sehemu mbalimbali za programu bila kuunda upya
translator_service = TranslatorService()
