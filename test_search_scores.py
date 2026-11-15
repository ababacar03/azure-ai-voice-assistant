
from app.rag.search import hybrid_search_documents

questions = [
    "Combien de temps faut-il pour recevoir un remboursement ?",
    "Quels sont les délais de livraison ?",
    "Comment contacter le service client ?",
    "Est-ce que vous acceptez les paiements par PayPal ?",
    "Quels sont vos horaires d'ouverture ?"
]

for question in questions:
    print("\n" + "=" * 60)
    print(f"QUESTION : {question}")

    documents = hybrid_search_documents(
        question,
        top=3,
        vector_k=10
    )

    if not documents:
        print("Aucun document trouvé.")
        continue

    for document in documents:
        print(f"\nFichier : {document['file_name']}")
        print(f"Score : {document['score']}")
