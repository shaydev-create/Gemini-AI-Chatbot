# Test básico para verificar que pytest funciona correctamente


def test_basic():
    """Test básico que siempre pasa para verificar que pytest funciona."""
    assert True


def test_string_operations():
    """Test de operaciones básicas con strings."""
    # Test de concatenación
    assert "Gemini" + "AI" == "GeminiAI"

    # Test de mayúsculas
    assert "gemini".upper() == "GEMINI"

    # Test de longitud
    assert len("Chatbot") == 7
