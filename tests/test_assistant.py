
from app.assistant import get_social_response


def test_salutation():
    result = get_social_response(["salutation"])

    assert result == "Bonjour ! Comment puis-je vous aider aujourd'hui ?"


def test_remerciement():
    result = get_social_response(["remerciement"])

    assert result == "Avec plaisir ! Je suis là pour vous aider."


def test_fin_conversation():
    result = get_social_response(["fin_conversation"])

    assert result == "Au revoir et à bientôt !"


def test_intention_metier_prioritaire():
    result = get_social_response(["salutation", "question_prix"])

    assert result is None


def test_aucune_intention_sociale():
    result = get_social_response(["information_produit"])

    assert result is None
