
from app.rag.search import search_documents

questions = [
    "Comment obtenir un remboursement ?",
    "Quel est le délai de livraison ?",
    "Quels sont les tarifs des restaurants ?",
    "Quels moyens de paiement sont acceptés ?"
]

for question in questions:
    print("\n" + "=" * 60)
    print(f"QUESTION : {question}")
    print("=" * 60)

    documents = search_documents(question, top=3)

    if not documents:
        print("Aucun document trouvé.")
        continue

    for doc in documents:
        print(f"\nDocument : {doc['file_name']}")
        print(f"Score : {doc['score']:.4f}")
        print(f"Contenu : {doc['content'][:150]}...")
