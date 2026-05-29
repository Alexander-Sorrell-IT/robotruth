from __future__ import annotations
from .types import Flag, Claim
from .diffparse import Diff

_DEP_NAMES = {"package.json", "requirements.txt", "pyproject.toml", "Pipfile",
              "package-lock.json", "yarn.lock", "pnpm-lock.yaml", "poetry.lock", "Pipfile.lock",
              "go.mod", "go.sum", "Cargo.toml", "Cargo.lock"}


def _has_test_files(diff: Diff) -> bool:
    for p in diff.paths:
        low = p.lower()
        if "test" in low or "spec" in low:
            return True
    return False


def _has_dep_change(diff: Diff) -> bool:
    return any(p.rsplit("/", 1)[-1] in _DEP_NAMES for p in diff.paths)


def verify_claims(diff: Diff, claims: list[Claim]) -> tuple[list[Flag], list[Flag]]:
    delivered: list[Flag] = []
    unhonored: list[Flag] = []
    for c in claims:
        if c.kind == "adds_tests":
            if _has_test_files(diff):
                delivered.append(Flag(label="Added tests (as claimed)", severity="minor",
                                      evidence="test/spec files present in diff"))
            else:
                unhonored.append(Flag(label="Claimed to add tests, but no test files changed",
                                      severity="moderate", evidence="no test/spec files in diff"))
        elif c.kind == "no_deps":
            if _has_dep_change(diff):
                unhonored.append(Flag(label="Claimed no dependency changes, but dependencies changed",
                                      severity="moderate", evidence="dependency/lockfile modified"))
            else:
                delivered.append(Flag(label="No dependency changes (as claimed)", severity="minor",
                                      evidence="no dependency files changed"))
    return delivered, unhonored
