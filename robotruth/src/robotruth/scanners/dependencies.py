from __future__ import annotations
from ..types import Flag
from ..claims import Claim
from ..diffparse import Diff

_DEP_FILES = {"package.json", "requirements.txt", "pyproject.toml", "Pipfile", "go.mod", "Cargo.toml"}
_LOCK_FILES = {"package-lock.json", "yarn.lock", "pnpm-lock.yaml", "poetry.lock", "Pipfile.lock", "Cargo.lock", "go.sum"}


def scan(diff: Diff, claims: list[Claim]) -> list[Flag]:
    out: list[Flag] = []
    for f in diff.files:
        base = f.path.rsplit("/", 1)[-1]
        if base in _DEP_FILES or base in _LOCK_FILES:
            out.append(Flag(
                label="Dependency/lockfile change",
                file=f.path,
                severity="moderate",
                evidence=f"{base} modified",
            ))
    return out
