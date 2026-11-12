
import os
from pathlib import Path

import azure.cognitiveservices.speech as speechsdk
from dotenv import load_dotenv

load_dotenv()

SPEECH_KEY = os.getenv("AZURE_SPEECH_KEY")
SPEECH_REGION = os.getenv("AZURE_SPEECH_REGION")


def text_to_speech(
    text: str,
    output_path: str,
    voice_name: str = "fr-FR-DeniseNeural"
) -> str:
    """
    Convertit un texte en fichier audio avec Azure AI Speech.

    Args:
        text: Texte à convertir en audio.
        output_path: Chemin du fichier audio généré.
        voice_name: Voix utilisée pour la synthèse.

    Returns:
        Chemin du fichier audio généré.
    """

    if not SPEECH_KEY or not SPEECH_REGION:
        raise ValueError("Configuration Azure Speech manquante.")

    if not text.strip():
        raise ValueError("Le texte à convertir est vide.")

    # Configuration Azure Speech
    speech_config = speechsdk.SpeechConfig(
        subscription=SPEECH_KEY,
        region=SPEECH_REGION
    )

    # Sélection de la voix
    speech_config.speech_synthesis_voice_name = voice_name

    # Création du dossier de sortie
    audio_file = Path(output_path)
    audio_file.parent.mkdir(parents=True, exist_ok=True)

    # Configuration du fichier audio
    audio_config = speechsdk.audio.AudioOutputConfig(
        filename=str(audio_file.resolve())
    )

    # Création du synthétiseur vocal
    synthesizer = speechsdk.SpeechSynthesizer(
        speech_config=speech_config,
        audio_config=audio_config
    )

    # Génération de la voix
    result = synthesizer.speak_text_async(text).get()

    if result.reason != speechsdk.ResultReason.SynthesizingAudioCompleted:
        details = speechsdk.SpeechSynthesisCancellationDetails(result)
        raise RuntimeError(
            f"Erreur de synthèse vocale : {details.error_details}"
        )

    return str(audio_file.resolve())
