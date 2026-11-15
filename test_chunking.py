
from app.rag.chunking import split_text_into_chunks

text = """
Les remboursements sont possibles dans les 14 jours
suivant l'achat. Le client doit fournir son numéro
de commande et le motif de sa demande.

Après validation, le remboursement est effectué
sous 5 à 10 jours ouvrés.
"""

chunks = split_text_into_chunks(
    text,
    chunk_size=20,
    overlap=5
)

for i, chunk in enumerate(chunks, start=1):
    print(f"\n--- CHUNK {i} ---")
    print(chunk)
