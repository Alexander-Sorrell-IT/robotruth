from __future__ import annotations
import json
import secrets
from pathlib import Path
from typing import Protocol


class ReceiptStore(Protocol):
    def put(self, receipt: dict) -> str: ...
    def get(self, rid: str) -> dict | None: ...
    def add_wall(self, entry: dict) -> None: ...
    def wall(self, limit: int = 30) -> list[dict]: ...


def _new_id() -> str:
    return secrets.token_urlsafe(6)


def _is_valid_id(rid: str) -> bool:
    # Ids come from token_urlsafe: only [A-Za-z0-9_-]. Reject anything else so a
    # crafted id can never escape the store root (defense-in-depth alongside the
    # HTTP route's path converter, which already blocks slashes).
    return bool(rid) and all(c.isalnum() or c in "-_" for c in rid)


class FileStore:
    def __init__(self, root: Path | str) -> None:
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def put(self, receipt: dict) -> str:
        rid = _new_id()
        (self.root / f"{rid}.json").write_text(json.dumps(receipt))
        return rid

    def get(self, rid: str) -> dict | None:
        if not _is_valid_id(rid):
            return None
        p = self.root / f"{rid}.json"
        if not p.exists():
            return None
        return json.loads(p.read_text())

    def add_wall(self, entry: dict) -> None:
        p = self.root / "_wall.json"
        items = json.loads(p.read_text()) if p.exists() else []
        items.insert(0, entry)
        p.write_text(json.dumps(items[:50]))

    def wall(self, limit: int = 30) -> list[dict]:
        p = self.root / "_wall.json"
        return json.loads(p.read_text())[:limit] if p.exists() else []


class RedisStore:
    def __init__(self, url: str) -> None:
        import redis
        self._r = redis.from_url(url, decode_responses=True)

    def put(self, receipt: dict) -> str:
        rid = _new_id()
        self._r.set(f"receipt:{rid}", json.dumps(receipt))
        return rid

    def get(self, rid: str) -> dict | None:
        raw = self._r.get(f"receipt:{rid}")
        return json.loads(raw) if raw else None

    def add_wall(self, entry: dict) -> None:
        self._r.lpush("wall", json.dumps(entry))
        self._r.ltrim("wall", 0, 49)

    def wall(self, limit: int = 30) -> list[dict]:
        return [json.loads(x) for x in self._r.lrange("wall", 0, limit - 1)]
