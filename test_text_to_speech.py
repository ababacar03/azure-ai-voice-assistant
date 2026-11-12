
from app.speech.text_to_speech import text_to_speech

text = "Bonjour et bienvenue ! Comment puis-je vous aider aujourd'hui ?"

audio_path = text_to_speech(
    text=text,
    output_path="data/output/response.wav"
)

print(f"Audio généré : {audio_path}")
