
from app.rag.search import hybrid_search_documents

questions = [
    "Comment récupérer mon argent après un achat ?",
    "Quand vais-je recevoir mon colis ?",
    "Comment contacter le service client ?"
]

for question in questions:
    print(f"\nQuestion : {question}")

    documents = hybrid_search_documents(question)

    for doc in documents:
        print(
            f"Document : {doc['file_name']} | "
            f"Score RRF : {doc['score']:.4f}"
        )
