from app.providers.base import TransliterationProvider
from app.providers.result import TransliterationResult


class PassThroughProvider(TransliterationProvider):

    LANGUAGE_LIST: list[str] = [
        "english",
    ]

    def supports(
        self,
        language: str | None,
    ) -> bool:
        """
        Return True when the provider supports the language.
        """

        if language is None:
            return False

        return language.lower().strip() in self.LANGUAGE_LIST

    def supported_languages(self) -> list[str]:
        """
        Return all languages supported by this provider.
        """

        return self.LANGUAGE_LIST.copy()

    def transliterate(
        self,
        text: str,
        language: str,
    ) -> TransliterationResult:
        """
        Return English text unchanged.
        """

        language = language.lower().strip()

        if not self.supports(language):
            raise ValueError(
                f"Unsupported language: {language}"
            )

        return TransliterationResult(
            text=text,
            language=language,
            provider=self.__class__.__name__,
            provider_type="local",
        )