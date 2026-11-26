import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))
from pathlib import Path

import streamlit as st

from app.assistant import process_text
from app.speech.speech_to_text import transcribe_audio
from app.speech.text_to_speech import text_to_speech


PROJECT_ROOT = Path(__file__).resolve().parents[1]

AUDIO_INPUT_PATH = PROJECT_ROOT / "data" / "samples" / "streamlit_recorded.wav"
AUDIO_OUTPUT_PATH = PROJECT_ROOT / "data" / "output" / "response.wav"


st.set_page_config(
    page_title="Assistant vocal - Service client",
    page_icon="🎙️",
    layout="wide"
)

st.title("🎙️ Assistant vocal - Service client")

st.markdown(
    """
    Bienvenue sur votre assistant intelligent !

    Posez vos questions concernant les produits,
    les commandes, les tarifs et les remboursements.
    """
)

# Initialisation de la session
if "messages" not in st.session_state:
    st.session_state.messages = []

if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = []

if "audio_widget_version" not in st.session_state:
    st.session_state.audio_widget_version = 0


# Affichage de la conversation
st.subheader("💬 Conversation")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

        if message.get("sources"):
            with st.expander("📚 Documents utilisés"):
                for source in message["sources"]:
                    st.write(source)

        if message.get("audio_path"):
            audio_file = Path(message["audio_path"])

            if audio_file.exists():
                st.audio(str(audio_file))


# --------------------------------------------------
# 1. INTERACTION VOCALE
# --------------------------------------------------

st.divider()
st.subheader("🎙️ Parler avec l'assistant")

audio_key = f"audio_input_{st.session_state.audio_widget_version}"

audio_value = st.audio_input(
    "Enregistrez votre demande :",
    key=audio_key
)

if st.button(
    "Traiter l'enregistrement",
    disabled=audio_value is None
):

    try:
        AUDIO_INPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
        AUDIO_OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

        # Sauvegarde de l'enregistrement
        AUDIO_INPUT_PATH.write_bytes(audio_value.getvalue())

        with st.spinner("Transcription de votre demande..."):

            # 2. Speech-to-Text
            transcription = transcribe_audio(str(AUDIO_INPUT_PATH))

        if not transcription or not transcription.strip():
            st.warning("Aucune parole détectée. Réessayez.")

        else:
            st.session_state.messages.append({
                "role": "user",
                "content": transcription
            })

            with st.spinner("L'assistant prépare sa réponse..."):

                # 3. Traitement par le pipeline Azure AI
                result = process_text(
                    transcription,
                    st.session_state.conversation_history
                )
                st.write("Intentions détectées :", result["intents"])

            answer = result["answer"]
            sources = result["sources"]

            # 4. Text-to-Speech
            audio_path = None

            try:
                text_to_speech(
                    answer,
                    str(AUDIO_OUTPUT_PATH)
                )

                if AUDIO_OUTPUT_PATH.exists():
                    audio_path = str(AUDIO_OUTPUT_PATH)

            except Exception as tts_error:
                st.warning(
                    f"La réponse audio n'a pas pu être générée : {tts_error}"
                )

            # Sauvegarde de la réponse
            st.session_state.messages.append({
                "role": "assistant",
                "content": answer,
                "sources": sources,
                "audio_path": audio_path
            })

        # Réinitialisation du composant audio
        st.session_state.audio_widget_version += 1
        st.rerun()

    except Exception as error:
        st.error(f"Une erreur est survenue : {error}")


# --------------------------------------------------
# 2. INTERACTION ÉCRITE
# --------------------------------------------------

st.divider()
st.subheader("⌨️ Écrire à l'assistant")

user_message = st.chat_input("Écrivez votre demande ici...")

if user_message:

    st.session_state.messages.append({
        "role": "user",
        "content": user_message
    })

    with st.spinner("L'assistant réfléchit..."):

        try:
            result = process_text(
                user_message,
                st.session_state.conversation_history
            )

            answer = result["answer"]
            sources = result["sources"]

            st.session_state.messages.append({
                "role": "assistant",
                "content": answer,
                "sources": sources
            })

            st.rerun()

        except Exception as error:
            st.error(f"Une erreur est survenue : {error}")
