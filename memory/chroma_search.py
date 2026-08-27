"""Chroma retrieval kept separate from the manual vector implementation."""

import chromadb # type: ignore

from .embeddings import embed_query, ensure_embeddings, store_embedding
from .storage import DATA_DIR, load_memories

CHROMA_PATH = DATA_DIR / "chroma_db"
COLLECTION_NAME = "memories"


def _collection():
    client = chromadb.PersistentClient(path=str(CHROMA_PATH))
    return client.get_or_create_collection(name=COLLECTION_NAME)


def index_memory(memory: dict, embedding: list[float] | None = None) -> None:
    """Upsert one saved memory into Chroma using its stable storage ID."""
    vector = embedding if embedding is not None else store_embedding(
        memory["id"], 
        memory["memory"]
        )
    _collection().upsert(
        ids=[memory["id"]], 
        documents=[memory["memory"]], 
        embeddings=[vector]
        )


def ensure_chroma_index() -> None:
    """Backfill Chroma from source-of-truth memories without touching manual search."""
    memories = load_memories()
    if not memories:
        return
    embeddings = ensure_embeddings(memories)
    collection = _collection()
    for memory in memories:
        collection.upsert(
            ids=[memory["id"]],
            documents=[memory["memory"]],
            embeddings=[embeddings[memory["id"]]],
        )


def retrieve_memories_chroma(query: str, top_k: int = 3) -> list[dict]:
    if top_k < 1:
        raise ValueError("top_k must be at least 1.")
    ensure_chroma_index()
    collection = _collection()
    if collection.count() == 0:
        return []
    results = collection.query(query_embeddings=[embed_query(query)], n_results=top_k)
    return [
        {"id": memory_id, "memory": memory, "distance": distance}
        for memory_id, memory, distance in zip(results["ids"][0], results["documents"][0], results["distances"][0])
    ]
