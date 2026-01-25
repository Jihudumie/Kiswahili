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
            placeholder = f"HASHTAG{counter}PLACEHOLDER"
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
    
    def translate(self, text: str) -> str:
        """
        Tafsiri maandishi kwa kuhifadhi muundo wa mistari
        """
        if not text:
            return ""
        
        # HATUA 1: Ondoa mistari yote ya social media links
        text = self._remove_social_links(text)
        
        # HATUA 2: Gawanya maandishi katika aya (separated by \n\n)
        paragraphs = text.split('\n\n')
        translated_paragraphs = []
        
        for paragraph in paragraphs:
            if not paragraph.strip():
                continue
            
            # Gawanya kila aya katika mistari
            lines = paragraph.split('\n')
            translated_lines = []
            
            for line in lines:
                if not line.strip():
                    continue
                
                # HATUA 3: Ondoa na hifadhi hashtags
                cleaned_line, protected_hashtags = self._extract_hashtags(line)
                
                # HATUA 4: Tafsiri mstari
                try:
                    translated_line = self.translator.translate(cleaned_line)
                except Exception as e:
                    print(f"Translation error: {e}")
                    translated_line = cleaned_line
                
                # HATUA 5: Rudisha hashtags
                translated_line = self._restore_hashtags(translated_line, protected_hashtags)
                
                translated_lines.append(translated_line)
            
            # Unganisha mistari ya aya kwa \n
            translated_paragraph = '\n'.join(translated_lines)
            translated_paragraphs.append(translated_paragraph)
        
        # HATUA 6: Unganisha aya kwa \n\n
        translated = '\n\n'.join(translated_paragraphs)
        
        # HATUA 7: Marekebisho maalum ya maneno baada ya tafsiri
        translated = translated.replace("Mwenyezi Mungu", "Allah")
        
        # HATUA 8: Safisha nafasi za ziada
        translated = re.sub(r' {2,}', ' ', translated)
        
        return translated.strip()
    
    def should_translate(self, original: str, translated: str) -> bool:
        """
        Kagua kama tafsiri ni tofauti na maandishi ya awali
        """
        return translated.strip() != original.strip()


# Instance ya pamoja (global) ya TranslatorService
translator_service = TranslatorService()
