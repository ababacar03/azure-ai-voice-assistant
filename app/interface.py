
import streamlit as st

from app.assistant import process_text


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


# Affichage de la conversation
st.subheader("💬 Conversation")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

        if message["role"] == "assistant" and message.get("sources"):
            with st.expander("📚 Documents utilisés"):
                for source in message["sources"]:
                    st.write(source)


# Saisie utilisateur
user_message = st.chat_input("Écrivez votre demande ici...")

if user_message:

    # Affichage du message utilisateur
    st.session_state.messages.append({
        "role": "user",
        "content": user_message
    })

    with st.chat_message("user"):
        st.write(user_message)

    # Traitement par l'assistant
    with st.chat_message("assistant"):
        with st.spinner("L'assistant réfléchit..."):

            try:
                result = process_text(
                    user_message,
                    st.session_state.conversation_history
                )

                answer = result["answer"]
                sources = result["sources"]

                st.write(answer)

                if sources:
                    with st.expander("📚 Documents utilisés"):
                        for source in sources:
                            st.write(source)

                # Sauvegarde de la réponse
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer,
                    "sources": sources
                })

            except Exception as error:
                st.error(
                    f"Une erreur est survenue : {error}"
                )
