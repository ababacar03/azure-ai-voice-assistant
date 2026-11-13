from app.language.key_phrases import extract_key_phrases

text = (
    "Je voudrais connaître les délais de livraison "
    "de ma commande et savoir comment obtenir "
    "un remboursement."
)

result = extract_key_phrases(text)

print("\n--- EXTRACTION DES MOTS-CLÉS ---")

for phrase in result:
    print("-", phrase)