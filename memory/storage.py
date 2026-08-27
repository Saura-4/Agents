"""The JSON source of truth for long-term memories."""

import json
from pathlib import Path
from uuid import uuid4

PROJECT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_DIR / "data"
MEMORY_FILE = DATA_DIR / "memory.json"


def _read_json(path: Path, default):
    if not path.exists():
        return default
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def _write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, ensure_ascii=False)


def _normalise_memories(raw_memories: list) -> list[dict]:
    """Convert the old list-of-strings format to stable-ID records."""
    memories = []
    for item in raw_memories:
        if isinstance(item, str):
            memories.append({"id": str(uuid4()), "memory": item})
        elif isinstance(item, dict) and "memory" in item:
            memories.append({"id": str(item.get("id") or uuid4()), "memory": str(item["memory"])})
        else:
            raise ValueError("Each memory must be a string or an object with a 'memory' field.")
    return memories


def load_memories() -> list[dict]:
    """Load memory records from the source-of-truth file."""
    raw_memories = _read_json(MEMORY_FILE, [])
    memories = _normalise_memories(raw_memories)
    if memories != raw_memories:
        _write_json(MEMORY_FILE, memories)
    return memories


def save_memory(memory: str) -> dict:
    if not memory or not memory.strip():
        raise ValueError("Memory cannot be empty.")
    memories = load_memories()
    record = {"id": str(uuid4()), "memory": memory.strip()}
    memories.append(record)
    _write_json(MEMORY_FILE, memories)
    return record


def get_last_memories(n: int = 5) -> list[dict]:
    if n < 1:
        raise ValueError("n must be at least 1.")
    return load_memories()[-n:]
