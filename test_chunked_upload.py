from app.rag.search import delete_all_documents, upload_documents

# Nettoyer complètement l'index
delete_all_documents()

# Réimporter les documents avec leur découpage en chunks
upload_documents()