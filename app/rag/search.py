
import os
from pathlib import Path

from dotenv import load_dotenv
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from app.rag.embeddings import generate_embedding
from azure.search.documents.models import VectorizedQuery
from app.rag.chunking import split_text_into_chunks
from app.config import get_required_setting
from azure.search.documents.indexes.models import (
    SearchIndex,
    SearchField,
    SearchFieldDataType,
    SimpleField,
    SearchableField,
    HnswAlgorithmConfiguration,
    VectorSearch,
    VectorSearchProfile,
)

# Chemin du projet
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Chargement du fichier .env
load_dotenv(PROJECT_ROOT / ".env")

# Configuration Azure AI Search
INDEX_NAME = "voice-assistant-index"

# Dossier contenant les documents
DOCUMENTS_DIR = PROJECT_ROOT / "data" / "knowledge_base"



def get_index_client():
    """Crée le client permettant de gérer les index."""

    endpoint = get_required_setting("AZURE_SEARCH_ENDPOINT")
    key = get_required_setting("AZURE_SEARCH_KEY")

    return SearchIndexClient(
        endpoint=endpoint,
        credential=AzureKeyCredential(key)
    )


def get_search_client():
    """Crée le client permettant de rechercher des documents."""

    endpoint = get_required_setting("AZURE_SEARCH_ENDPOINT")
    key = get_required_setting("AZURE_SEARCH_KEY")

    return SearchClient(
        endpoint=endpoint,
        index_name=INDEX_NAME,
        credential=AzureKeyCredential(key)
    )



def create_search_index():
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
        ),
        SearchField(
            name="content_vector",
            type=SearchFieldDataType.Collection(
                SearchFieldDataType.Single
            ),
            searchable=True,
            vector_search_dimensions=1536,
            vector_search_profile_name="vector-profile"
        )
    ]

    vector_search = VectorSearch(
        algorithms=[
            HnswAlgorithmConfiguration(
                name="hnsw-config"
            )
        ],
        profiles=[
            VectorSearchProfile(
                name="vector-profile",
                algorithm_configuration_name="hnsw-config"
            )
        ]
    )

    index = SearchIndex(
        name=INDEX_NAME,
        fields=fields,
        vector_search=vector_search
    )

    client.create_or_update_index(index)

    print(f"Index '{INDEX_NAME}' mis à jour avec succès.")


def upload_documents():
    search_client = get_search_client()

    documents = []

    for file_path in DOCUMENTS_DIR.glob("*.txt"):
        content = file_path.read_text(encoding="utf-8")

        # Découper le fichier en chunks
        chunks = split_text_into_chunks(
            content,
            chunk_size=500,
            overlap=100
        )

        print(f"\nFichier : {file_path.name}")
        print(f"Nombre de chunks : {len(chunks)}")

        for chunk_index, chunk in enumerate(chunks):
            embedding = generate_embedding(chunk)

            documents.append({
                "id": f"{file_path.stem}-{chunk_index}",
                "file_name": file_path.name,
                "content": chunk,
                "content_vector": embedding
            })

    if documents:
        result = search_client.upload_documents(documents=documents)
        print(f"\n{len(result)} chunks envoyés vers Azure AI Search.")

    return documents


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

    search_client = get_search_client()

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

def vector_search_documents(query: str, top: int = 3):
    """
    Recherche des documents similaires à la question
    grâce aux embeddings et à Azure AI Search.
    """

    if not query or not query.strip():
        raise ValueError("La question ne peut pas être vide.")

    # Transformer la question en vecteur
    query_embedding = generate_embedding(query)

    search_client = get_search_client()

    vector_query = VectorizedQuery(
        vector=query_embedding,
        k_nearest_neighbors=top,
        fields="content_vector"
    )

    results = search_client.search(
        search_text=None,
        vector_queries=[vector_query],
        select=["file_name", "content"],
        top=top
    )

    documents = []

    for result in results:
        documents.append({
            "file_name": result["file_name"],
            "content": result["content"],
            "score": result["@search.score"]
        })

    return documents




def hybrid_search_documents(
    query: str,
    top: int = 3,
    vector_k: int = 10,
    min_score: float = 0.0,
    intent: str | list[str] = "autre"
):
    """
    Combine BM25 et la recherche vectorielle.
    Privilégie les documents associés à l'intention détectée.
    """

    if not query or not query.strip():
        raise ValueError("La question ne peut pas être vide.")

    if top <= 0 or vector_k <= 0:
        raise ValueError("Les paramètres top et vector_k doivent être positifs.")

    if min_score < 0:
        raise ValueError("Le score minimum ne peut pas être négatif.")

    # Fichiers à privilégier selon l'intention
    preferred_files = get_preferred_files(intent)

    query_embedding = generate_embedding(query)

    search_client = get_search_client()

    vector_query = VectorizedQuery(
        vector=query_embedding,
        k_nearest_neighbors=vector_k,
        fields="content_vector"
    )

    results = search_client.search(
        search_text=query,
        vector_queries=[vector_query],
        select=["file_name", "content"],
        top=max(top, vector_k)
    )

    documents = []

    for result in results:
        score = result["@search.score"]

        if score >= min_score:
            documents.append({
                "file_name": result["file_name"],
                "content": result["content"],
                "score": score
            })

    # Prioriser les fichiers associés à l'intention
    documents.sort(
        key=lambda doc: doc["file_name"] not in preferred_files
    )

    return documents[:top]


def delete_document(document_id: str):
    """Supprime un document de l'index Azure AI Search."""

    search_client = get_search_client()

    result = search_client.delete_documents(
        documents=[{"id": document_id}]
    )

    for item in result:
        if not item.succeeded:
            raise RuntimeError(
                f"Échec de suppression du document : {document_id}"
            )

    print(f"Document supprimé : {document_id}")
def delete_all_documents():
    """
    Supprime tous les documents présents dans l'index Azure AI Search.
    """

    search_client = get_search_client()

    # Récupérer tous les identifiants des documents
    results = search_client.search(
        search_text="*",
        select=["id"]
    )

    documents_to_delete = [
        {"id": document["id"]}
        for document in results
    ]

    if not documents_to_delete:
        print("Aucun document à supprimer.")
        return

    # Suppression par lots de 1000 documents maximum
    for start in range(0, len(documents_to_delete), 1000):
        batch = documents_to_delete[start:start + 1000]
        search_client.delete_documents(documents=batch)

        print(f"{len(batch)} documents supprimés.")

    print("Nettoyage de l'index terminé.")


def get_preferred_files(intent: str | list[str]) -> list[str]:
    """
    Retourne les fichiers à privilégier selon une ou plusieurs intentions.
    """

    intent_files = {
        "remboursement": ["remboursements.txt"],
        "suivi_livraison": ["livraison.txt"],
        "contact": ["faq_client.txt"],
        "paiement": ["faq_client.txt"],
        "information_produit": ["produits.txt"],
        "question_prix": ["tarifs.txt"],
        "recommandation": ["produits.txt"],
        "reclamation": ["faq_client.txt", "remboursements.txt"],
        "hors_sujet": [],
        "autre": []
    }

    # Accepter une seule intention ou plusieurs
    if isinstance(intent, str):
        intents = [intent]
    else:
        intents = intent

    # Regrouper les fichiers sans doublons
    preferred_files = []

    for current_intent in intents:
        for file_name in intent_files.get(current_intent, []):
            if file_name not in preferred_files:
                preferred_files.append(file_name)

    return preferred_files

