
from app.speech.speech_to_text import transcribe_audio


def main():
    audio_path = "app/data/samples/test.wav"

    try:
        transcription = transcribe_audio(audio_path)

        print("\n--- TRANSCRIPTION ---")
        print(transcription)

    except Exception as error:
        print(f"Erreur : {error}")


if __name__ == "__main__":
    main()
