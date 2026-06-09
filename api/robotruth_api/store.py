from __future__ import annotations
import json
import secrets
import urllib.request
from pathlib import Path
from typing import Protocol


class ReceiptStore(Protocol):
    def put(self, receipt: dict) -> str: ...
    def get(self, rid: str) -> dict | None: ...
    def add_wall(self, entry: dict) -> None: ...
    def wall(self, limit: int = 30) -> list[dict]: ...
    def stats(self) -> dict: ...


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

    def stats(self) -> dict:
        verdicts: dict[str, int] = {}
        flags_total = 0
        scanners: dict[str, int] = {}
        for p in self.root.glob("*.json"):
            if p.name.startswith("_"):
                continue
            try:
                r = json.loads(p.read_text())
                v = r.get("verdict", "")
                if v:
                    verdicts[v] = verdicts.get(v, 0) + 1
                for flag in r.get("undisclosed", []) + r.get("unhonored", []):
                    flags_total += 1
                    label = flag.get("label", "")
                    for s in ("dangerous_primitives", "dependencies", "scope_drift", "security_guard"):
                        if s in label.lower() or s.replace("_", " ") in label.lower():
                            scanners[s] = scanners.get(s, 0) + 1
                            break
            except Exception:
                continue
        wall_count = len(self.wall(50))
        total = sum(verdicts.values())
        return {"total_receipts": total, "wall_count": wall_count,
                "verdict_distribution": verdicts, "scanners_fired": scanners, "flags_total": flags_total}


class UpstashRestStore:
    """Durable receipt store over the Upstash REST API (HTTP, no persistent TCP
    connection) — the serverless-friendly path. Each method is one POST of a
    Redis command as a JSON array; the response is {"result": ...}."""

    def __init__(self, url: str, token: str) -> None:
        self._url = url.rstrip("/")
        self._token = token

    def _cmd(self, *args: object) -> object:
        body = json.dumps([str(a) for a in args]).encode()
        req = urllib.request.Request(
            self._url, data=body,
            headers={"Authorization": f"Bearer {self._token}", "Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read()).get("result")

    def put(self, receipt: dict) -> str:
        rid = _new_id()
        self._cmd("SET", f"receipt:{rid}", json.dumps(receipt))
        return rid

    def get(self, rid: str) -> dict | None:
        if not _is_valid_id(rid):
            return None
        raw = self._cmd("GET", f"receipt:{rid}")
        return json.loads(raw) if isinstance(raw, str) else None

    def add_wall(self, entry: dict) -> None:
        self._cmd("LPUSH", "wall", json.dumps(entry))
        self._cmd("LTRIM", "wall", 0, 49)

    def wall(self, limit: int = 30) -> list[dict]:
        items = self._cmd("LRANGE", "wall", 0, limit - 1)
        if not isinstance(items, list):
            return []
        return [json.loads(x) for x in items]

    def stats(self) -> dict:
        # Iterate every receipt so the numbers are ACCURATE and self-consistent —
        # verdict distribution across ALL receipts (not just the wall) and a real
        # flag total. SCAN, then GET each. Fine at hackathon volume.
        keys: list[str] = []
        cursor = "0"
        for _ in range(50):  # bound the loop; plenty for any realistic key count
            res = self._cmd("SCAN", cursor, "MATCH", "receipt:*", "COUNT", 300)
            if not isinstance(res, list) or len(res) != 2:
                break
            cursor = str(res[0])
            batch = res[1]
            if isinstance(batch, list):
                keys.extend(str(k) for k in batch)
            if cursor == "0":
                break
        verdicts: dict[str, int] = {}
        flags_total = 0
        for k in keys:
            raw = self._cmd("GET", k)
            if not isinstance(raw, str):
                continue
            try:
                r = json.loads(raw)
            except Exception:
                continue
            v = r.get("verdict", "")
            if v:
                verdicts[v] = verdicts.get(v, 0) + 1
            flags_total += len(r.get("undisclosed", [])) + len(r.get("unhonored", []))
        return {"total_receipts": len(keys), "wall_count": len(self.wall(50)),
                "verdict_distribution": verdicts, "scanners_fired": {}, "flags_total": flags_total}


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

    def stats(self) -> dict:
        total = self._r.dbsize()
        wall_entries = self.wall(50)
        wall_count = len(wall_entries)
        verdicts: dict[str, int] = {}
        for entry in wall_entries:
            v = entry.get("verdict", "")
            if v:
                verdicts[v] = verdicts.get(v, 0) + 1
        return {"total_receipts": total, "wall_count": wall_count,
                "verdict_distribution": verdicts, "scanners_fired": {}, "flags_total": 0}
