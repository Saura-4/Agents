from rank_bm25 import BM25Okapi

from .bm25_index import get_bm25_index, tokenize


def build_bm25_index(memories):
    corpus = [
        tokenize(memory["memory"])
        for memory in memories
    ]

    return BM25Okapi(corpus) if corpus else None


def retrieve_memories_bm25(query: str, top_k: int = 3):
    bm25, records = get_bm25_index()
    if bm25 is None:
        return []

    query_tokens = tokenize(query)

    scores = bm25.get_scores(query_tokens)

    ranked = []

    for memory, score in zip(records, scores):
        ranked.append(
            {
                "id": memory["id"],
                "memory": memory["memory"],
                "score": float(score),
            }
        )

    ranked.sort(
        key=lambda item: item["score"],
        reverse=True,
    )
    for rank, item in enumerate(ranked, 1):
        item["rank"] = rank

    return ranked[:top_k]
