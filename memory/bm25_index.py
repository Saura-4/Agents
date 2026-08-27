"""Persistent, eagerly maintained BM25 corpus and cached runtime model."""

import json
from rank_bm25 import BM25Okapi

from .storage import DATA_DIR, load_memories

BM25_INDEX_FILE = DATA_DIR / "memory_bm25_index.json"

_bm25: BM25Okapi | None = None
_records: list[dict] = []


def tokenize(text: str) -> list[str]:
    return text.lower().split()


def _snapshot(memories: list[dict]) -> dict:
    return {
        "version": 1,
        "records": [
            {"id": m["id"], "memory": m["memory"], "tokens": tokenize(m["memory"])}
            for m in memories
        ],
    }


def _is_current(snapshot: dict, memories: list[dict]) -> bool:
    records = snapshot.get("records", [])
    return [(r.get("id"), r.get("memory")) for r in records] == [
        (m["id"], m["memory"]) for m in memories
    ]


def _write(snapshot: dict) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with BM25_INDEX_FILE.open("w", encoding="utf-8") as file:
        json.dump(snapshot, file, indent=2, ensure_ascii=False)


def ensure_bm25_index(memories: list[dict] | None = None) -> BM25Okapi | None:
    """Load the persisted corpus, repairing it when absent or stale."""
    global _bm25, _records
    memories = load_memories() if memories is None else memories
    snapshot = None
    if BM25_INDEX_FILE.exists():
        try:
            with BM25_INDEX_FILE.open("r", encoding="utf-8") as file:
                snapshot = json.load(file)
        except (OSError, ValueError, TypeError):
            snapshot = None
    if snapshot is None or not _is_current(snapshot, memories):
        snapshot = _snapshot(memories)
        _write(snapshot)
    _records = snapshot["records"]
    _bm25 = BM25Okapi([record["tokens"] for record in _records]) if _records else None
    return _bm25


def update_bm25_index(memory: dict) -> None:
    """Eagerly refresh the corpus after a memory is inserted."""
    ensure_bm25_index(load_memories())


def get_bm25_index() -> tuple[BM25Okapi | None, list[dict]]:
    global _bm25
    if _bm25 is None and not _records:
        ensure_bm25_index()
    return _bm25, _records
