
from app.rag.embeddings import generate_embedding

text = "Comment obtenir un remboursement ?"

embedding = generate_embedding(text)

print("Embedding généré avec succès.")
print("Nombre de dimensions :", len(embedding))
print("Premières valeurs :", embedding[:5])
