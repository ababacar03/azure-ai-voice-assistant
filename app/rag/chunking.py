
def split_text_into_chunks(
    text: str,
    chunk_size: int = 500,
    overlap: int = 100
) -> list[str]:
    """
    Découpe un texte en plusieurs chunks
    avec un chevauchement entre les passages.
    """

    if not text or not text.strip():
        return []

    if chunk_size <= 0:
        raise ValueError("chunk_size doit être positif.")

    if overlap < 0 or overlap >= chunk_size:
        raise ValueError(
            "overlap doit être positif et inférieur à chunk_size."
        )

    words = text.split()
    chunks = []

    start = 0

    while start < len(words):
        end = start + chunk_size

        chunk = " ".join(words[start:end])
        chunks.append(chunk)

        start += chunk_size - overlap

    return chunks
