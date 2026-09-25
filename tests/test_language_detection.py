from app.detectors.detector_service import detect_text_information


def test_telugu_detection():

    result = detect_text_information(
        "నమస్కారం"
    )

    assert result["script"] == "telugu"
    assert result["language"] == "telugu"


def test_hindi_detection():

    result = detect_text_information(
        "नमस्ते, आप कैसे हैं?"
    )

    assert result["script"] == "devanagari"
    assert result["language"] == "hindi"


def test_marathi_detection():

    result = detect_text_information(
        "तुम्ही कसे आहात?"
    )

    assert result["script"] == "devanagari"
    assert result["language"] == "marathi"


def test_bengali_detection():

    result = detect_text_information(
        "তুমি কেমন আছো?"
    )

    assert result["script"] == "bengali"
    assert result["language"] == "bengali"


def test_assamese_detection():

    result = detect_text_information(
        "আপুনি কেনে আছে? মই অসমীয়া ভাষা শিকি আছোঁ।"
    )

    assert result["script"] == "bengali"
    assert result["language"] == "assamese"


def test_english_detection():

    result = detect_text_information(
        "Hello world"
    )

    assert result["script"] == "latin"
    assert result["language"] == "english"