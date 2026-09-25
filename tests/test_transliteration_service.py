from app.services.transliteration_service import transliterate_text


def test_telugu_transliteration():

    result = transliterate_text(
        "తిన్నావా?"
    )

    assert result.language == "telugu"
    assert result.text == "tinnava?"
    assert result.provider == "AksharamukhaProvider"
    
def test_hindi_transliteration():

    result = transliterate_text(
        "तुम कैसे हो?"
    )

    assert result.language == "hindi"
    assert result.text == "tuma kaise ho?"
    assert result.provider == "AksharamukhaProvider"


def test_marathi_transliteration():

    result = transliterate_text(
        "तुम्ही कसे आहात?"
    )

    assert result.language == "marathi"
    assert result.text == "tumhi kase ahata?"
    assert result.provider == "AksharamukhaProvider"


def test_tamil_transliteration():

    result = transliterate_text(
        "தமிழ் மொழி"
    )

    assert result.language == "tamil"
    assert result.text == "thamizh mozhi"
    assert result.provider == "AksharamukhaProvider"


def test_bengali_transliteration():

    result = transliterate_text(
        "বাংলা ভাষা"
    )

    assert result.language == "bengali"
    assert result.text == "bamla bhasha"
    assert result.provider == "AksharamukhaProvider"


def test_mixed_text_transliteration():

    result = transliterate_text(
        "నేను Python నేర్చుకుంటున్నాను."
    )

    assert result.language == "telugu"
    assert result.text == "nenu Python nerchukuntunnanu."
    assert result.provider == "AksharamukhaProvider"