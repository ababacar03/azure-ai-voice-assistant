
from pathlib import Path

from app.speech.speech_to_text import record_audio, transcribe_audio
from app.language.sentiment import analyze_sentiment
from app.rag.answer import generate_answer
from app.speech.text_to_speech import text_to_speech
from app.language.intent import detect_intent
from app.utils.errors import get_error_message
from app.language.pii_detection import detect_pii
from app.language.key_phrases import extract_key_phrases
from app.language.entities import recognize_entities


PROJECT_ROOT = Path(__file__).resolve().parents[1]

def get_social_response(intents: list[str]) -> str | None:
    if "salutation" in intents:
        return "Bonjour ! Comment puis-je vous aider aujourd'hui ?"

    if "remerciement" in intents:
        return "Avec plaisir ! Je suis là pour vous aider."

    if "fin_conversation" in intents:
        return "Au revoir et à bientôt !"

    return None
def main():
    audio_path = PROJECT_ROOT / "data" / "samples" / "recorded.wav"
    output_path = PROJECT_ROOT / "data" / "output" / "response.wav"

    # Historique temporaire : conservé pendant cette session uniquement
    conversation_history = []

    print("\n======================================")
    print("   ASSISTANT VOCAL - SERVICE CLIENT")
    print("======================================")

    while True:
        command = input(
            "\nEntrée pour commencer une nouvelle demande "
            "ou 'q' pour quitter : "
        ).strip().lower()

        if command == "q":
            print("\nFin de la conversation. À bientôt !")
            break

        etape = "Enregistrement audio"

        try:
            # 1. Enregistrement depuis le microphone
            record_audio(str(audio_path))

            if not audio_path.exists() or audio_path.stat().st_size == 0:
                print("Erreur : aucun fichier audio valide.")
                continue

            # 2. Speech-to-Text
            etape = "Speech-to-Text"
            transcription = transcribe_audio(str(audio_path))

            if not transcription or not transcription.strip():
                print("Aucune parole détectée. Réessaie.")
                continue

            print("\n--- TRANSCRIPTION ---")
            print(transcription)

            # 3. Détection et masquage des données personnelles
            etape = "Détection des données personnelles"
            pii_result = detect_pii(transcription)
            texte_securise = pii_result["redacted_text"]

            print("\n--- TEXTE APRÈS MASQUAGE ---")
            print(texte_securise)

            print("\n--- DONNÉES PERSONNELLES DÉTECTÉES ---")
            for entity in pii_result["entities"]:
                print(entity)

            # 4. Détection des intentions
            etape = "Détection des intentions"
            intents = detect_intent(
            texte_securise,
            conversation_history=conversation_history
        )

            print("\n--- INTENTIONS DÉTECTÉES ---")
            for intent in intents:
                print("-", intent)

            # 5. Analyses conditionnelles
            sentiment = None
            key_phrases = []
            entities = []

            if any(intent in ["reclamation", "remboursement"] for intent in intents):
                etape = "Analyse de sentiment"
                sentiment = analyze_sentiment(texte_securise)

                print("\n--- ANALYSE DE SENTIMENT ---")
                print(sentiment)

            if any(intent in [
                "information_produit",
                "question_prix",
                "recommandation"
            ] for intent in intents):
                etape = "Extraction des mots-clés"
                key_phrases = extract_key_phrases(texte_securise)

                print("\n--- MOTS-CLÉS DÉTECTÉS ---")
                for phrase in key_phrases:
                    print("-", phrase)

            if any(intent in [
                "reclamation",
                "remboursement",
                "suivi_livraison",
                "information_produit",
                "question_prix",
                "recommandation"
            ] for intent in intents):
                etape = "Reconnaissance des entités"
                entities = recognize_entities(transcription)

                print("\n--- ENTITÉS DÉTECTÉES ---")
                for entity in entities:
                    print(entity)

            # 6. Génération de la réponse
            etape = "Génération de la réponse"

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

            print("\n--- RÉPONSE DE L'ASSISTANT ---")
            print(result["answer"])

            print("\n--- DOCUMENTS UTILISÉS ---")
            for source in result["sources"]:
                print("-", source)

            # 7. Mise à jour de l'historique
            conversation_history.append({
                "role": "user",
                "content": texte_securise
            })

            conversation_history.append({
                "role": "assistant",
                "content": result["answer"]
            })

            # 8. Text-to-Speech
            etape = "Text-to-Speech"
            text_to_speech(result["answer"], str(output_path))

            print("\nRéponse audio générée :", output_path)
            print("\nTu peux maintenant poursuivre la conversation.")

        except Exception as error:
            print(f"\nErreur pendant l'étape : {etape}")
            print(f"Message : {get_error_message(error)}")
            print(f"Détails techniques : {error}")


if __name__ == "__main__":
    main()
