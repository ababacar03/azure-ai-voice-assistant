
from app.rag.search import get_preferred_files

intents = [
    "remboursement",
    "suivi_livraison",
    "contact",
    "paiement",
    "information_produit",
    "question_prix",
    "recommandation",
    "reclamation",
    "autre"
]

for intent in intents:
    files = get_preferred_files(intent)

    print(f"{intent} -> {files}")
