from typing import List


class TextChunker:

    def __init__(self, chunk_size: int = 500, overlap: int = 50):
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk(self, text: str, doc_id: int) -> List[dict]:
        """Split text into overlapping chunks."""
        if not text.strip():
            return []

        words = text.split()
        chunks = []
        start = 0
        chunk_number = 0

        while start < len(words):
            end = min(start + self.chunk_size, len(words))
            chunk_words = words[start:end]
            chunk_text = " ".join(chunk_words)

            if chunk_text.strip():
                chunks.append({
                    "document_id": doc_id,
                    "chunk_number": chunk_number,
                    "chunk_text": chunk_text,
                    "word_count": len(chunk_words),
                    "char_count": len(chunk_text),
                })
                chunk_number += 1

            if end == len(words):
                break
            start = end - self.overlap

        return chunks