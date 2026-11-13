
import os
from pathlib import Path

from dotenv import load_dotenv
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex,
    SearchField,
    SearchFieldDataType,
    SimpleField,
    SearchableField,
)

# Chemin du projet
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Chargement du fichier .env
load_dotenv(PROJECT_ROOT / ".env")

# Configuration Azure AI Search
ENDPOINT = os.getenv("AZURE_SEARCH_ENDPOINT")
KEY = os.getenv("AZURE_SEARCH_KEY")

INDEX_NAME = "voice-assistant-index"

# Dossier contenant les documents
DOCUMENTS_DIR = PROJECT_ROOT / "data" / "knowledge_base"


def get_index_client():
    """Crée le client permettant de gérer les index."""

    if not ENDPOINT or not KEY:
        raise ValueError("Configuration Azure AI Search manquante.")

    return SearchIndexClient(
        endpoint=ENDPOINT,
        credential=AzureKeyCredential(KEY)
    )


def create_search_index():
    """Crée l'index documentaire dans Azure AI Search."""

    client = get_index_client()

    fields = [
        SimpleField(
            name="id",
            type=SearchFieldDataType.String,
            key=True
        ),
        SearchableField(
            name="file_name",
            type=SearchFieldDataType.String
        ),
        SearchableField(
            name="content",
            type=SearchFieldDataType.String
        )
    ]

    index = SearchIndex(
        name=INDEX_NAME,
        fields=fields
    )

    client.create_or_update_index(index)

    print(f"Index '{INDEX_NAME}' créé avec succès.")


def upload_documents():
    """Envoie les fichiers TXT vers Azure AI Search."""

    if not DOCUMENTS_DIR.exists():
        raise FileNotFoundError("Dossier documentaire introuvable.")

    files = list(DOCUMENTS_DIR.glob("*.txt"))

    if not files:
        raise ValueError("Aucun fichier TXT trouvé.")

    documents = []

    for file_path in files:
        content = file_path.read_text(encoding="utf-8")

        documents.append({
            "id": file_path.stem,
            "file_name": file_path.name,
            "content": content
        })

    search_client = SearchClient(
        endpoint=ENDPOINT,
        index_name=INDEX_NAME,
        credential=AzureKeyCredential(KEY)
    )

    results = search_client.upload_documents(documents=documents)

    for result in results:
        if not result.succeeded:
            raise RuntimeError(
                f"Échec de l'indexation du document {result.key}"
            )

    print(f"{len(results)} documents indexés avec succès.")

def search_documents(query: str, top: int = 3):
    """
    Recherche les documents les plus pertinents dans Azure AI Search.

    Args:
        query: Question ou mots-clés de l'utilisateur.
        top: Nombre maximum de résultats.

    Returns:
        Liste des documents retrouvés.
    """
    if not query.strip():
        raise ValueError("La question ne peut pas être vide.")

    search_client = SearchClient(
        endpoint=ENDPOINT,
        index_name=INDEX_NAME,
        credential=AzureKeyCredential(KEY)
    )

    results = search_client.search(
        search_text=query,
        top=top,
        select=["file_name", "content"]
    )

    documents = []

    for result in results:
        documents.append({
            "file_name": result["file_name"],
            "content": result["content"],
            "score": result["@search.score"]
        })

    return documents

