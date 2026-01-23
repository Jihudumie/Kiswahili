import re
from deep_translator import GoogleTranslator
from config import TRANSLATION_SOURCE, TRANSLATION_TARGET


class TranslatorService:
    def __init__(self):
        self.translator = GoogleTranslator(
            source=TRANSLATION_SOURCE,
            target=TRANSLATION_TARGET
        )

    def clean_text(self, text: str) -> str:
        pattern = r"^🔗\s*(Telegramu|X|WhatsApp|Instagram):.*$"
        cleaned = re.sub(pattern, "", text, flags=re.MULTILINE)
        return cleaned.strip()

    def protect_hashtags(self, text: str):
        """
        Linda hashtags zisitafsiriwe
        """
        hashtags = re.findall(r"#\w+", text)
        protected_text = text

        for i, tag in enumerate(hashtags):
            protected_text = protected_text.replace(
                tag, f"__HASHTAG_{i}__"
            )

        return protected_text, hashtags

    def restore_hashtags(self, text: str, hashtags: list):
        """
        Rudisha hashtags baada ya tafsiri
        """
        for i, tag in enumerate(hashtags):
            text = text.replace(f"__HASHTAG_{i}__", tag)
        return text

    def translate(self, text: str) -> str:
        if not text:
            return ""

        # 1. Safisha social links
        cleaned_text = self.clean_text(text)

        # 2. Linda hashtags
        protected_text, hashtags = self.protect_hashtags(cleaned_text)

        # 3. Tafsiri
        try:
            translated = self.translator.translate(protected_text)
        except Exception:
            return cleaned_text

        # 4. Rudisha hashtags
        translated = self.restore_hashtags(translated, hashtags)

        # 5. Marekebisho maalum
        translated = translated.replace("Mwenyezi Mungu", "Allah")

        return translated
