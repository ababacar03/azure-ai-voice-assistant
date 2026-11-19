
from pathlib import Path

from app.speech.speech_to_text import transcribe_audio
from app.language.sentiment import analyze_sentiment
from app.rag.answer import generate_answer
from app.speech.text_to_speech import text_to_speech
from app.language.intent import detect_intent
from app.utils.errors import get_error_message
from app.language.pii_detection import detect_pii


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def main():
    audio_path = PROJECT_ROOT / "data" / "samples" / "test.wav"
    output_path = PROJECT_ROOT / "data" / "output" / "response.wav"
    if not audio_path.exists():
        print(f"Erreur : le fichier audio est introuvable : {audio_path}")
        return

    if audio_path.stat().st_size == 0:
        print("Erreur : le fichier audio est vide.")
        return
    etape = "Speech-to-Text"

    try:
       # 1. Speech-to-Text
        transcription = transcribe_audio(str(audio_path))

        if not transcription or not transcription.strip():
            print("Erreur : aucune parole n'a été détectée dans l'audio.")
            return

        print("\n--- TRANSCRIPTION ---")
        print(transcription)


        # 2. Détection et masquage des données personnelles
        etape = "Détection des données personnelles"
        pii_result = detect_pii(transcription)

        texte_securise = pii_result["redacted_text"]

        print("\n--- TEXTE APRÈS MASQUAGE ---")
        print(texte_securise)

        print("\n--- DONNÉES PERSONNELLES DÉTECTÉES ---")
        for entity in pii_result["entities"]:
            print(entity)

        # 2. Analyse de sentiment
        etape = "Analyse de sentiment"
        sentiment = analyze_sentiment(texte_securise)

        print("\n--- ANALYSE DE SENTIMENT ---")
        print(sentiment)

        # 3. Détection de l'intention
        etape = "Détection de l'intention"
        intent = detect_intent(texte_securise)

        print("\n--- INTENTION DÉTECTÉE ---")
        print(intent)

       
        # 4. Génération de la réponse
        etape = "Génération de la réponse"
        if intent == "hors_sujet":
            result = {
                "answer": (
                    "Désolé, je suis un assistant dédié à notre service client. "
                    "Je peux vous aider concernant nos produits, nos tarifs, "
                    "les commandes et les remboursements."
                ),
                "sources": []
            }
        else:
            result = generate_answer(texte_securise, intent)

        print("\n--- RÉPONSE DE L'ASSISTANT ---")
        print(result["answer"])

        print("\n--- DOCUMENTS UTILISÉS ---")
        for source in result["sources"]:
            print("-", source)

        # 4. Text-to-Speech
        etape = "Text-to-Speech"
        text_to_speech(result["answer"], str(output_path))

        print("\nRéponse audio générée :", output_path)

    except Exception as error:
        print(f"\nErreur pendant l'étape : {etape}")
        print(f"Message : {get_error_message(error)}")
        print(f"Détails techniques : {error}")


if __name__ == "__main__":
    main()
