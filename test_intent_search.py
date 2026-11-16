
from app.rag.search import hybrid_search_documents
from app.rag.search import get_preferred_files

tests = [
    {
        "question": "Combien de temps faut-il pour recevoir un remboursement ?",
        "intent": "remboursement"
    },
    {
        "question": "Quels sont les délais de livraison ?",
        "intent": "suivi_livraison"
    },
    {
        "question": "Comment contacter le service client ?",
        "intent": "contact"
    },
    {
        "question": "Est-ce que vous acceptez PayPal ?",
        "intent": "paiement"
    },
    {
    "question": "Combien coûte le service premium ?",
    "intent": "question_prix"
    },
    {
    "question": "Quel est le prix du service entreprise ?",
    "intent": "question_prix"
    }
]

for test in tests:
    print("\n" + "=" * 60)
    print("QUESTION :", test["question"])
    print("INTENTION :", test["intent"])
    print("FICHIERS PRIORITAIRES :", get_preferred_files(test["intent"]))

    results = hybrid_search_documents(
        test["question"],
        top=3,
        intent=test["intent"]
    )

    for result in results:
        print(
            f"Fichier : {result['file_name']} "
            f"| Score : {result['score']:.5f}"
        )
