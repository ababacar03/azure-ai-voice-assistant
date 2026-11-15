
from app.rag.search import hybrid_search_documents

questions = [
    "Combien de temps faut-il pour recevoir un remboursement ?",
    "Quels sont les délais de livraison ?",
    "Comment contacter le service client ?"
]

for question in questions:
    print("\n" + "=" * 60)
    print("QUESTION :", question)

    results = hybrid_search_documents(
        query=question,
        top=3,
        vector_k=10
    )

    for result in results:
        print("\nFichier :", result["file_name"])
        print("Score :", result["score"])
        print("Contenu :", result["content"])
