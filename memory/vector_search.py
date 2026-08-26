"""Manual cosine-similarity retrieval: the learning-reference backend."""

import math

from .embeddings import embed_query, ensure_embeddings
from .storage import load_memories


def cosine_similarity(vector_a: list[float], vector_b: list[float]) -> float:
    dot_product = sum(a * b for a, b in zip(vector_a, vector_b))
    magnitude_a = math.sqrt(sum(value * value for value in vector_a))
    magnitude_b = math.sqrt(sum(value * value for value in vector_b))
    if magnitude_a == 0 or magnitude_b == 0:
        return 0.0
    return dot_product / (magnitude_a * magnitude_b)


def retrieve_memories_vector(query: str, top_k: int = 3, threshold: float | None = None) -> list[dict]:
    if top_k < 1:
        raise ValueError("top_k must be at least 1.")
    memories = load_memories()
    if not memories:
        return []
    embeddings = ensure_embeddings(memories)
    query_embedding = embed_query(query)
    results = [{"id": memory["id"], "memory": memory["memory"], "similarity": cosine_similarity(query_embedding, embeddings[memory["id"]])} for memory in memories]
    results.sort(key=lambda item: item["similarity"], reverse=True)
    if threshold is not None:
        results = [item for item in results if item["similarity"] >= threshold]
    return results[:top_k]
