
from pathlib import Path

import azure.cognitiveservices.speech as speechsdk
from dotenv import load_dotenv

from app.config import get_required_setting

load_dotenv()


def text_to_speech(
    text: str,
    output_path: str,
    voice_name: str = "fr-FR-DeniseNeural"
) -> str:
    """
    Convertit un texte en fichier audio avec Azure AI Speech.
    """

    if not text or not text.strip():
        raise ValueError("Le texte à convertir est vide.")

    # Récupération des identifiants Azure Speech
    speech_key = get_required_setting("AZURE_SPEECH_KEY")
    speech_region = get_required_setting("AZURE_SPEECH_REGION")

    # Configuration Azure Speech
    speech_config = speechsdk.SpeechConfig(
        subscription=speech_key,
        region=speech_region
    )

    speech_config.speech_synthesis_voice_name = voice_name

    # Création du dossier de sortie
    audio_file = Path(output_path)
    audio_file.parent.mkdir(parents=True, exist_ok=True)

    audio_config = speechsdk.audio.AudioOutputConfig(
        filename=str(audio_file.resolve())
    )

    synthesizer = speechsdk.SpeechSynthesizer(
        speech_config=speech_config,
        audio_config=audio_config
    )

    result = synthesizer.speak_text_async(text).get()

    if result.reason != speechsdk.ResultReason.SynthesizingAudioCompleted:
        details = speechsdk.SpeechSynthesisCancellationDetails(result)
        raise RuntimeError(
            f"Erreur de synthèse vocale : {details.error_details}"
        )

    return str(audio_file.resolve())
