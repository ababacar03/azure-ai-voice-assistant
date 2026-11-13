
from app.rag.search import search_documents

question = "Comment obtenir un remboursement ?"

results = search_documents(question)

print(f"\nQuestion : {question}")
print("\nRésultats :")

for document in results:
    print(f"\nFichier : {document['file_name']}")
    print(f"Score : {document['score']}")
    print(f"Contenu : {document['content']}")
