

import threading
from pathlib import Path
from app.config import get_required_setting
import azure.cognitiveservices.speech as speechsdk
from dotenv import load_dotenv

from app.config import get_required_setting

load_dotenv()





def record_audio(output_path: str) -> str:
    """
    Enregistrement local depuis le microphone.
    Utilisé uniquement pour les tests locaux.
    """
    import sounddevice as sd
    import soundfile as sf
    import numpy as np

    sample_rate = 44100
    audio_data = []

    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    input("Appuie sur Entrée pour démarrer l'enregistrement...")

    print("Enregistrement en cours...")

    def callback(indata, frames, time, status):
        if status:
            print(status)
        audio_data.append(indata.copy())

    with sd.InputStream(
        samplerate=sample_rate,
        channels=1,
        dtype="int16",
        callback=callback
    ):
        input("Appuie sur Entrée pour arrêter...")

    if not audio_data:
        raise RuntimeError("Aucun audio enregistré.")

    audio = np.concatenate(audio_data, axis=0)

    sf.write(output_file, audio, sample_rate, subtype="PCM_16")

    return str(output_file)


def transcribe_audio(audio_path: str) -> str:
    """
    Transcription Azure Speech avec détection automatique
    de la langue.
    """
    SPEECH_KEY = get_required_setting("AZURE_SPEECH_KEY")
    SPEECH_REGION = get_required_setting("AZURE_SPEECH_REGION")
    if not SPEECH_KEY or not SPEECH_REGION:
        raise ValueError("Configuration Azure Speech manquante.")

    audio_file = Path(audio_path)

    if not audio_file.is_file():
        raise FileNotFoundError(
            f"Fichier audio introuvable : {audio_file.resolve()}"
        )

    speech_config = speechsdk.SpeechConfig(
        subscription=SPEECH_KEY,
        region=SPEECH_REGION
    )

    auto_detect_config = (
        speechsdk.languageconfig.AutoDetectSourceLanguageConfig(
            languages=["fr-FR", "en-US", "es-ES", "de-DE"]
        )
    )

    audio_config = speechsdk.audio.AudioConfig(
        filename=str(audio_file.resolve())
    )

    recognizer = speechsdk.SpeechRecognizer(
        speech_config=speech_config,
        auto_detect_source_language_config=auto_detect_config,
        audio_config=audio_config
    )

    transcription_parts = []
    detected_languages = set()
    done = threading.Event()
    errors = []

    def on_recognized(event):
        if event.result.reason == speechsdk.ResultReason.RecognizedSpeech:
            text = event.result.text.strip()

            language_result = speechsdk.AutoDetectSourceLanguageResult(
                event.result
            )
            detected_language = language_result.language

            if detected_language:
                detected_languages.add(detected_language)

            if text:
                transcription_parts.append(text)

    def on_session_stopped(event):
        done.set()

    def on_canceled(event):
        details = speechsdk.CancellationDetails(event.result)

        if details.reason == speechsdk.CancellationReason.Error:
            errors.append(details.error_details)

        done.set()

    recognizer.recognized.connect(on_recognized)
    recognizer.session_stopped.connect(on_session_stopped)
    recognizer.canceled.connect(on_canceled)

    try:
        recognizer.start_continuous_recognition_async().get()
        done.wait()

    finally:
        recognizer.stop_continuous_recognition_async().get()

    if errors:
        raise RuntimeError("Erreur Azure Speech : " + errors[0])

    if detected_languages:
        print("Langue(s) détectée(s) :", detected_languages)

    return " ".join(transcription_parts)
