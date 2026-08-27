"""Rank-fusion retrieval over lexical BM25 and semantic vector search."""

from .bm25 import retrieve_memories_bm25
from .vector_search import retrieve_memories_vector

RRF_K = 60
CANDIDATE_MULTIPLIER = 3


def retrieve_memories_hybrid(query: str, top_k: int = 3) -> list[dict]:
    if top_k < 1:
        raise ValueError("top_k must be at least 1.")
    candidate_k = max(top_k, top_k * CANDIDATE_MULTIPLIER)
    lexical = retrieve_memories_bm25(query, candidate_k)
    semantic = retrieve_memories_vector(query, candidate_k)
    combined = {}
    for rank, result in enumerate(lexical, 1):
        item = combined.setdefault(result["id"], {"id": result["id"], "memory": result["memory"], "bm25_rank": None, "vector_rank": None, "bm25_score": None, "similarity": None, "hybrid_score": 0.0})
        item["bm25_rank"] = rank
        item["bm25_score"] = result["score"]
        item["hybrid_score"] += 1 / (RRF_K + rank)
    for rank, result in enumerate(semantic, 1):
        item = combined.setdefault(result["id"], {"id": result["id"], "memory": result["memory"], "bm25_rank": None, "vector_rank": None, "bm25_score": None, "similarity": None, "hybrid_score": 0.0})
        item["vector_rank"] = rank
        item["similarity"] = result["similarity"]
        item["hybrid_score"] += 1 / (RRF_K + rank)
    return sorted(combined.values(), key=lambda item: item["hybrid_score"], reverse=True)[:top_k]
