
from pathlib import Path

from app.speech.speech_to_text import transcribe_audio
from app.language.sentiment import analyze_sentiment
from app.rag.answer import generate_answer
from app.speech.text_to_speech import text_to_speech


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def main():
    audio_path = PROJECT_ROOT / "data" / "samples" / "test.wav"
    output_path = PROJECT_ROOT / "data" / "output" / "response.wav"

    try:
        # 1. Speech-to-Text
        transcription = transcribe_audio(str(audio_path))

        print("\n--- TRANSCRIPTION ---")
        print(transcription)

        # 2. Analyse de sentiment
        sentiment = analyze_sentiment(transcription)

        print("\n--- ANALYSE DE SENTIMENT ---")
        print(sentiment)

        # 3. Recherche documentaire + GPT-5
        result = generate_answer(transcription)

        print("\n--- RÉPONSE DE L'ASSISTANT ---")
        print(result["answer"])

        print("\n--- DOCUMENTS UTILISÉS ---")
        for source in result["sources"]:
            print("-", source)

        # 4. Text-to-Speech
        text_to_speech(result["answer"], str(output_path))

        print("\nRéponse audio générée :", output_path)

    except Exception as error:
        print(f"Erreur : {error}")


if __name__ == "__main__":
    main()
