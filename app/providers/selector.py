from app.providers.aksharamukha_provider import AksharamukhaProvider
from app.providers.passthrough_provider import PassThroughProvider


class ProviderSelector:
    """
    Selects the appropriate transliteration provider
    based on the requested language.
    """

    def __init__(self):
        self.providers = [
            AksharamukhaProvider(),
            PassThroughProvider(),
        ]

    def get_provider(self, language):
        """
        Return the first provider that supports the language.

        Args:
            language: Language name or language identifier.

        Returns:
            A supported provider instance, or None if no provider
            supports the requested language.
        """

        if not isinstance(language, str):
            return None

        normalized_language = language.strip().lower()

        if not normalized_language:
            return None

        for provider in self.providers:
            if provider.supports(normalized_language):
                return provider

        return None

    def get_supported_languages(self):
        """
        Return a unique list of all languages supported
        by the registered providers.
        """

        languages = []

        for provider in self.providers:
            supported_languages = provider.supported_languages()

            if supported_languages:
                languages.extend(supported_languages)

        # Remove duplicates while preserving the original order.
        return list(dict.fromkeys(languages))