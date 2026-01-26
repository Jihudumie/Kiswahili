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
        
        # Pattern ya kutambua na KUONDOA mistari yote ya social media
        # Inaondoa mstari mzima ukiwa na kiungo au bila kiungo
        self.social_media_pattern = re.compile(
            r'🔗\s*(Telegram|X|WhatsApp|Instagram|Facebook|YouTube|TikTok|Twitter):\s*.*',
            re.IGNORECASE
        )
        
        # Pattern ya kutambua hashtags
        self.hashtag_pattern = re.compile(r'#\w+')
    
    def _remove_social_links(self, text: str) -> str:
        """
        Ondoa mistari yote ya viungo vya social media
        """
        # Ondoa kila mstari unaoanzia na emoji ya 🔗
        text = self.social_media_pattern.sub('', text)
        
        # Ondoa mistari mitupu iliyobaki
        lines = [line for line in text.split('\n') if line.strip()]
        
        return '\n'.join(lines)
    
    def _extract_hashtags(self, text: str) -> tuple[str, dict]:
        """
        Ondoa hashtags kabla ya kutafsiri
        Rudisha text iliyosafishwa na dictionary ya hashtags
        """
        protected = {}
        counter = 0
        
        # Hifadhi hashtags
        def replace_hashtag(match):
            nonlocal counter
            placeholder = f"___HASHTAG{counter}___"
            protected[placeholder] = match.group(0)
            counter += 1
            return placeholder
        
        text = self.hashtag_pattern.sub(replace_hashtag, text)
        
        return text, protected
    
    def _restore_hashtags(self, text: str, protected: dict) -> str:
        """
        Rudisha hashtags zilizohifadhiwa
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
        
        # HATUA 1: Ondoa mistari yote ya social media links
        #text = self._remove_social_links(text)
        
        # HATUA 2: Ondoa na hifadhi hashtags
        cleaned_text, protected_hashtags = self._extract_hashtags(text)
        
        # HATUA 3: Tafsiri maandishi iliyosafishwa
        translated = self.translator.translate(cleaned_text)
        
        # HATUA 4: Rudisha hashtags
        translated = self._restore_hashtags(translated, protected_hashtags)

        # HATUA 5: Marekebisho maalum ya maneno baada ya tafsiri
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
