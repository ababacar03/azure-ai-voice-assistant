
import os
import threading
from pathlib import Path

import azure.cognitiveservices.speech as speechsdk
from dotenv import load_dotenv

load_dotenv()

SPEECH_KEY = os.getenv("AZURE_SPEECH_KEY")
SPEECH_REGION = os.getenv("AZURE_SPEECH_REGION")


def transcribe_audio(audio_path: str) -> str:
    """
    Transcrit intégralement un fichier audio avec Azure AI Speech
    grâce à la reconnaissance continue et à la détection automatique
    de la langue.
    """

    if not SPEECH_KEY or not SPEECH_REGION:
        raise ValueError("Configuration Azure Speech manquante.")

    audio_file = Path(audio_path)

    if not audio_file.is_file():
        raise FileNotFoundError(
            f"Fichier audio introuvable : {audio_file.resolve()}"
        )

    # Configuration Azure Speech
    speech_config = speechsdk.SpeechConfig(
        subscription=SPEECH_KEY,
        region=SPEECH_REGION
    )

    # AJOUT : Configuration de la détection automatique de la langue
    auto_detect_config = (
        speechsdk.languageconfig.AutoDetectSourceLanguageConfig(
            languages=["fr-FR", "en-US", "es-ES", "de-DE"]
        )
    )

    # Configuration du fichier audio
    audio_config = speechsdk.audio.AudioConfig(
        filename=str(audio_file.resolve())
    )

    # Création du recognizer
    recognizer = speechsdk.SpeechRecognizer(
        speech_config=speech_config,
        auto_detect_source_language_config=auto_detect_config,
        audio_config=audio_config
    )

    # Stockage des phrases reconnues
    transcription_parts = []
    detected_languages = set()
    done = threading.Event()
    errors = []

    # Événement : une phrase est reconnue
    def on_recognized(event):
        if event.result.reason == speechsdk.ResultReason.RecognizedSpeech:
            text = event.result.text.strip()

            # AJOUT : Récupération de la langue détectée
            language_result = speechsdk.AutoDetectSourceLanguageResult(
                event.result
            )
            detected_language = language_result.language

            if detected_language and detected_language not in detected_languages:
                detected_languages.add(detected_language)
                print(f"Langue détectée : {detected_language}")

            if text:
                transcription_parts.append(text)
                print(f"Reconnu : {text}")

    # Événement : la lecture du fichier est terminée
    def on_session_stopped(event):
        done.set()

    # Événement : reconnaissance annulée
    def on_canceled(event):
        details = speechsdk.CancellationDetails(event.result)

        if details.reason == speechsdk.CancellationReason.Error:
            errors.append(
                f"{details.reason}: {details.error_details}"
            )

        done.set()

    # Abonnement aux événements
    recognizer.recognized.connect(on_recognized)
    recognizer.session_stopped.connect(on_session_stopped)
    recognizer.canceled.connect(on_canceled)

    try:
        print("Démarrage de la transcription...")

        recognizer.start_continuous_recognition_async().get()

        # Attendre la fin du fichier audio
        done.wait()

    finally:
        recognizer.stop_continuous_recognition_async().get()

    if errors:
        raise RuntimeError("Erreur Azure Speech : " + errors[0])

    if not transcription_parts:
        return "Aucune parole reconnue dans le fichier audio."

    # Assemblage de toutes les phrases
    return " ".join(transcription_parts)
