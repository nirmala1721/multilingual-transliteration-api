from typing import cast

from aksharamukha import transliterate

from app.providers.base import TransliterationProvider
from app.providers.result import TransliterationResult


class AksharamukhaProvider(TransliterationProvider):

    LANGUAGE_SCRIPTS: dict[str, str] = {
        "telugu": "Telugu",
        "hindi": "Devanagari",
        "marathi": "Devanagari",
        "tamil": "Tamil",
        "bengali": "Bengali",
        "kannada": "Kannada",
        "gujarati": "Gujarati",
        "odia": "Oriya",
        "punjabi": "Gurmukhi",
        "assamese": "Assamese",
    }

    def supports(
        self,
        language: str | None,
    ) -> bool:
        """
        Return True when the provider supports the language.
        """

        if language is None:
            return False

        return language.lower().strip() in self.LANGUAGE_SCRIPTS

    def supported_languages(self) -> list[str]:
        """
        Return all languages supported by Aksharamukha.
        """

        return list(
            self.LANGUAGE_SCRIPTS.keys()
        )

    def transliterate(
        self,
        text: str,
        language: str,
    ) -> TransliterationResult:
        """
        Transliterate Indian-language text into
        Roman colloquial representation.
        """

        language = language.lower().strip()

        if not self.supports(language):
            raise ValueError(
                f"Unsupported language: {language}"
            )

        script = self.LANGUAGE_SCRIPTS[language]

        result = transliterate.process(
            script,
            "RomanColloquial",
            text,
        )

        result_text = cast(
            str,
            result,
        )

        return TransliterationResult(
            text=result_text,
            language=language,
            provider=self.__class__.__name__,
            provider_type="local",
        )