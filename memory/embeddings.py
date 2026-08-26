"""Gemini embedding operations and the persisted manual-search index."""

import json
from .storage import DATA_DIR

EMBEDDING_MODEL = "gemini-embedding-001"
EMBEDDINGS_FILE = DATA_DIR / "memory_embeddings.json"


def _load_embeddings() -> dict[str, list[float]]:
    if not EMBEDDINGS_FILE.exists():
        return {}
    with EMBEDDINGS_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


def _save_embeddings(embeddings: dict[str, list[float]]) -> None:
    EMBEDDINGS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with EMBEDDINGS_FILE.open("w", encoding="utf-8") as file:
        json.dump(embeddings, file)


def _embed(text: str, task_type: str) -> list[float]:
    from google.genai import types # type: ignore
    from clients import client

    response = client.models.embed_content(model=EMBEDDING_MODEL, contents=text, config=types.EmbedContentConfig(task_type=task_type))
    return list(response.embeddings[0].values)


def embed_document(text: str) -> list[float]:
    return _embed(text, "RETRIEVAL_DOCUMENT")


def embed_query(text: str) -> list[float]:
    return _embed(text, "RETRIEVAL_QUERY")


def store_embedding(memory_id: str, text: str) -> list[float]:
    embeddings = _load_embeddings()
    vector = embed_document(text)
    embeddings[memory_id] = vector
    _save_embeddings(embeddings)
    return vector


def ensure_embeddings(memories: list[dict]) -> dict[str, list[float]]:
    embeddings = _load_embeddings()
    changed = False
    for memory in memories:
        if memory["id"] not in embeddings:
            embeddings[memory["id"]] = embed_document(memory["memory"])
            changed = True
    if changed:
        _save_embeddings(embeddings)
    return embeddings
