"""
Lightweight RAG module for indexing a game script and retrieving
the most relevant chunks for a given query.

Uses sentence-transformers (local, offline) for embeddings and
numpy cosine similarity for retrieval. The index is persisted to
disk so embeddings are only computed once per script.
"""

from pathlib import Path
import pickle
import numpy as np
from sentence_transformers import SentenceTransformer


# =============================================================================
# Chunking
# =============================================================================

def chunk_text(text: str, chunk_size: int = 800, overlap: int = 150) -> list[str]:
    """Split text into overlapping chunks on paragraph boundaries.

    Overlap preserves local context across chunk edges (e.g. a character
    introduced in one paragraph and described in the next).
    """
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks = []
    current = ""

    for para in paragraphs:
        if len(current) + len(para) + 2 <= chunk_size:
            current = f"{current}\n\n{para}" if current else para
        else:
            if current:
                chunks.append(current)
                current = current[-overlap:] + "\n\n" + para if overlap > 0 else para
            else:
                current = para

            while len(current) > chunk_size:
                chunks.append(current[:chunk_size])
                current = current[chunk_size - overlap:]

    if current:
        chunks.append(current)

    return chunks


def slice_script(text: str, start_marker: str, end_marker: str = None) -> str:
    """Slice a section of the script between two markers.

    start_marker: string to search for; slicing begins at its position.
    end_marker:   string to search for; slicing ends just before it.
                  If None or not found, slices to end of file.

    Raises ValueError if start_marker is not found.
    """
    start = text.find(start_marker)
    if start == -1:
        raise ValueError(f"Start marker not found: {start_marker!r}")

    if end_marker:
        end = text.find(end_marker, start)
        if end == -1:
            end = len(text)
    else:
        end = len(text)

    return text[start:end].strip()


# =============================================================================
# ScriptRAG
# =============================================================================

class ScriptRAG:
    """Index a script and retrieve the most relevant chunks for a query.

    Replaces the "dump the whole script into the prompt" pattern with
    targeted semantic retrieval.
    """

    DEFAULT_MODEL = "all-MiniLM-L6-v2"  # 384-dim, fast, general-purpose

    def __init__(self, model_name: str = DEFAULT_MODEL):
        self.model_name = model_name
        self._model = None
        self.chunks: list[str] = []
        self.embeddings: np.ndarray | None = None

    @property
    def model(self) -> SentenceTransformer:
        if self._model is None:
            print(f"Loading embedding model: {self.model_name}")
            self._model = SentenceTransformer(self.model_name)
        return self._model

    def build(self, text: str, chunk_size: int = 800, overlap: int = 150) -> None:
        """Chunk the text and compute embeddings."""
        self.chunks = chunk_text(text, chunk_size=chunk_size, overlap=overlap)
        print(f"Split script into {len(self.chunks)} chunks. Embedding...")
        self.embeddings = self.model.encode(
            self.chunks,
            normalize_embeddings=True,
            show_progress_bar=True,
            convert_to_numpy=True,
        )
        print(f"Indexed {len(self.chunks)} chunks.")

    def query(self, query: str, top_k: int = 5) -> list[str]:
        """Return the top_k chunks most semantically relevant to the query."""
        if self.embeddings is None or not self.chunks:
            raise ValueError("Index is empty — call build() or load() first.")

        query_vec = self.model.encode(
            [query], normalize_embeddings=True, convert_to_numpy=True
        )[0]

        scores = self.embeddings @ query_vec
        top_k = min(top_k, len(self.chunks))
        top_idx = np.argpartition(-scores, top_k - 1)[:top_k]
        top_idx = top_idx[np.argsort(-scores[top_idx])]
        return [self.chunks[i] for i in top_idx]

    def retrieve_context(self, query: str, top_k: int = 5,
                         separator: str = "\n\n---\n\n") -> str:
        """Retrieve top_k chunks joined into a single string for prompt injection."""
        return separator.join(self.query(query, top_k=top_k))

    # -------------------------------------------------------------------------
    # Persistence
    # -------------------------------------------------------------------------

    def save(self, path: Path) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "wb") as f:
            pickle.dump({
                "model_name": self.model_name,
                "chunks": self.chunks,
                "embeddings": self.embeddings,
            }, f)
        print(f"Saved RAG index to {path}")

    def load(self, path: Path) -> None:
        path = Path(path)
        with open(path, "rb") as f:
            data = pickle.load(f)
        self.model_name = data["model_name"]
        self.chunks = data["chunks"]
        self.embeddings = data["embeddings"]
        print(f"Loaded RAG index from {path} ({len(self.chunks)} chunks)")

    @classmethod
    def from_file_or_build(
        cls,
        text_path: Path,
        index_path: Path,
        start_marker: str = None,
        end_marker: str = None,
        chunk_size: int = 800,
        overlap: int = 150,
    ) -> "ScriptRAG":
        """Load a cached index if it's newer than the source; otherwise build.

        start_marker / end_marker: optional strings to slice the script
        before indexing (e.g. to restrict to a single act or quest range).
        """
        text_path = Path(text_path)
        index_path = Path(index_path)
        rag = cls()

        if index_path.exists() and index_path.stat().st_mtime >= text_path.stat().st_mtime:
            rag.load(index_path)
            return rag

        with open(text_path, "r", encoding="utf-8") as f:
            text = f.read()

        if start_marker or end_marker:
            text = slice_script(text, start_marker or text[:1], end_marker)

        rag.build(text, chunk_size=chunk_size, overlap=overlap)
        rag.save(index_path)
        return rag