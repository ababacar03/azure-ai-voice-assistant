
import streamlit as st

# Configuration de la page
st.set_page_config(
    page_title="Assistant vocal - Service client",
    page_icon="🎙️",
    layout="wide"
)

# Titre
st.title("🎙️ Assistant vocal - Service client")

st.markdown(
    """
    Bienvenue sur votre assistant intelligent !

    Posez vos questions concernant les produits,
    les commandes, les tarifs et les remboursements.
    """
)

# Initialisation de l'historique
if "messages" not in st.session_state:
    st.session_state.messages = []

# Affichage de la conversation
st.subheader("💬 Conversation")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Zone de saisie textuelle
user_message = st.chat_input("Écrivez votre demande ici...")

if user_message:
    st.session_state.messages.append({
        "role": "user",
        "content": user_message
    })

    with st.chat_message("user"):
        st.write(user_message)
