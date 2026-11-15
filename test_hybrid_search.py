
from app.rag.search import hybrid_search_documents

query = "Combien de temps faut-il pour recevoir un remboursement ?"

results = hybrid_search_documents(query)

for result in results:
    print("\nFichier :", result["file_name"])
    print("Contenu :", result["content"])
