from abc import ABC, abstractmethod

from app.providers.result import TransliterationResult


class TransliterationProvider(ABC):

    @abstractmethod
    def supports(self, language: str | None) -> bool:
        """
        Return True if this provider supports the given language.
        """
        raise NotImplementedError

    @abstractmethod
    def transliterate(
        self,
        text: str,
        language: str,
    ) -> TransliterationResult:
        """
        Transliterate text using this provider.
        """
        raise NotImplementedError

    @abstractmethod
    def supported_languages(self) -> list[str]:
        """
        Return the languages supported by this provider.
        """
        raise NotImplementedError