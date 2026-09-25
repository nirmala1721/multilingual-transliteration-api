from app.services.transliteration_service import transliterate_text
from app.detectors.detector_service import detect_text_information


def test_empty_text():

    try:

        transliterate_text("")

        assert False, "Expected ValueError"

    except ValueError as error:

        assert "language" in str(error).lower()


def test_english_text():

    result = transliterate_text(
        "Hello world"
    )

    assert result.language == "english"
    assert result.text == "Hello world"


def test_numbers():

    try:

        transliterate_text("12345")

        assert False, "Expected ValueError"

    except ValueError as error:

        assert "language" in str(error).lower()


def test_telugu_with_english_and_numbers():

    result = transliterate_text(
        "నా పేరు Nirmala 123"
    )

    assert result.language == "telugu"
    assert "Nirmala" in result.text
    assert "123" in result.text


def test_unsupported_language():

    try:

        transliterate_text(
            "こんにちは"
        )

        assert False, "Expected ValueError"

    except ValueError as error:

        assert "provider" in str(error).lower() or \
               "language" in str(error).lower()


def test_wrong_language_override():

    try:

        transliterate_text(
            "నమస్కారం",
            language="hindi"
        )

        assert False, "Expected ValueError"

    except ValueError as error:

        assert "mismatch" in str(error).lower()
        
        
def test_short_hindi_text():

    result = detect_text_information(
        "नमस्ते"
    )

    assert result["script"] == "devanagari"


def test_longer_hindi_text():

    result = detect_text_information(
        "नमस्ते, आप कैसे हैं? मुझे हिंदी भाषा सीखना अच्छा लगता है।"
    )

    assert result["script"] == "devanagari"
    assert result["language"] == "hindi"


def test_short_marathi_text():

    result = detect_text_information(
        "मराठी"
    )

    assert result["script"] == "devanagari"


def test_longer_marathi_text():

    result = detect_text_information(
        "तुम्ही कसे आहात? मला मराठी भाषा शिकायला आवडते."
    )

    assert result["script"] == "devanagari"
    assert result["language"] == "marathi"


def test_short_bengali_text():

    result = detect_text_information(
        "বাংলা"
    )

    assert result["script"] == "bengali"


def test_short_telugu_text():

    result = detect_text_information(
        "తెలుగు"
    )

    assert result["script"] == "telugu"
    assert result["language"] == "telugu"
    
def test_detected_but_unsupported_indian_language():

    try:

        transliterate_text(
            "നമസ്കാരം"
        )

        assert False, "Expected ValueError"

    except ValueError as error:

        assert "provider" in str(error).lower()