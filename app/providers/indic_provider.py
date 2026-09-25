from indic_transliteration import sanscript

from app.providers.base import TransliterationProvider
from app.providers.result import TransliterationResult


class IndicProvider(TransliterationProvider):

    LANGUAGE_SCHEMES = {
        "telugu": sanscript.TELUGU,
        "hindi": sanscript.DEVANAGARI,
        "tamil": sanscript.TAMIL,
        "bengali": sanscript.BENGALI,
    }

    def supports(self, language):

        return language.lower() in self.LANGUAGE_SCHEMES

    def supported_languages(self):

        return list(self.LANGUAGE_SCHEMES.keys())

    def transliterate(self, text, language):

        language = language.lower()

        if not self.supports(language):
            raise ValueError(
                f"Unsupported language: {language}"
            )

        scheme = self.LANGUAGE_SCHEMES[language]

        result = sanscript.transliterate(
            text,
            scheme,
            sanscript.OPTITRANS
        )

        result = sanscript.SCHEMES[
            sanscript.OPTITRANS
        ].to_lay_indian(result)

        return TransliterationResult(
        text=result,
        language=language,
        provider=self.__class__.__name__,
        provider_type="local"
    )