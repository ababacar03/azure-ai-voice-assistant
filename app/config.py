
import os


def get_setting(name: str, default=None):
    """Récupère une configuration depuis Streamlit Secrets ou l'environnement."""

    try:
        import streamlit as st
        value = st.secrets.get(name)
        if value:
            return value
    except Exception:
        pass

    return os.getenv(name, default)


def get_required_setting(name: str) -> str:
    """Récupère une variable obligatoire ou déclenche une erreur explicite."""

    value = get_setting(name)

    if not value:
        raise ValueError(f"Configuration manquante : {name}")

    return value
