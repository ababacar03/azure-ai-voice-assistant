
from app.language.sentiment import analyze_sentiment
from app.rag.answer import generate_answer
from app.language.intent import detect_intent
from app.language.pii_detection import detect_pii
from app.language.key_phrases import extract_key_phrases
from app.language.entities import recognize_entities


def get_social_response(intents: list[str]) -> str | None:
    if "salutation" in intents:
        return "Bonjour ! Comment puis-je vous aider aujourd'hui ?"

    if "remerciement" in intents:
        return "Avec plaisir ! Je suis là pour vous aider."

    if "fin_conversation" in intents:
        return "Au revoir et à bientôt !"

    return None


def process_text(
    transcription: str,
    conversation_history: list
) -> dict:

    # 1. Détection et masquage des données personnelles
    pii_result = detect_pii(transcription)
    texte_securise = pii_result["redacted_text"]

    # 2. Détection des intentions
    intents = detect_intent(
        texte_securise,
        conversation_history=conversation_history
    )

    # 3. Analyses conditionnelles
    sentiment = None
    key_phrases = []
    entities = []

    if any(intent in ["reclamation", "remboursement"] for intent in intents):
        sentiment = analyze_sentiment(texte_securise)

    if any(intent in [
        "information_produit",
        "question_prix",
        "recommandation"
    ] for intent in intents):
        key_phrases = extract_key_phrases(texte_securise)

    if any(intent in [
        "reclamation",
        "remboursement",
        "suivi_livraison",
        "information_produit",
        "question_prix",
        "recommandation"
    ] for intent in intents):
        entities = recognize_entities(transcription)

    # 4. Génération de la réponse
    social_response = get_social_response(intents)

    if social_response:
        result = {
            "answer": social_response,
            "sources": []
        }

    elif "hors_sujet" in intents:
        result = {
            "answer": (
                "Désolé, je suis un assistant dédié à notre service client. "
                "Je peux vous aider concernant nos produits, nos tarifs, "
                "les commandes et les remboursements."
            ),
            "sources": []
        }

    else:
        result = generate_answer(
            texte_securise,
            intents,
            conversation_history=conversation_history
        )

    # 5. Mise à jour de l'historique
    conversation_history.append({
        "role": "user",
        "content": texte_securise
    })

    conversation_history.append({
        "role": "assistant",
        "content": result["answer"]
    })

    return {
        "answer": result["answer"],
        "sources": result["sources"],
        "intents": intents,
        "pii": pii_result["entities"],
        "sentiment": sentiment,
        "key_phrases": key_phrases,
        "entities": entities
    }
