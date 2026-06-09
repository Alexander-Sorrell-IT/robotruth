from __future__ import annotations
from .types import Flag, Claim
from .diffparse import Diff

# Files that DECLARE dependencies. A change here is a real dependency change, so it breaks
# a "no new dependencies" claim. Lockfiles (package-lock.json, yarn.lock, poetry.lock,
# go.sum, Cargo.lock, …) are deliberately EXCLUDED: they re-resolve automatically
# (`npm install`, etc.), so a lockfile-only churn does not mean a new dependency was
# declared — calling that a broken claim is a false accusation, the exact class an
# accountability product must refuse. The `dependencies` scanner still notes the lockfile
# change as an undisclosed event; verify just won't call it a lie.
_MANIFESTS = {"package.json", "requirements.txt", "pyproject.toml", "Pipfile",
              "go.mod", "Cargo.toml", "Gemfile"}


def _has_test_files(diff: Diff) -> bool:
    for p in diff.paths:
        low = p.lower()
        if "test" in low or "spec" in low:
            return True
    return False


def _has_manifest_change(diff: Diff) -> bool:
    return any(p.rsplit("/", 1)[-1] in _MANIFESTS for p in diff.paths)


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
            if _has_manifest_change(diff):
                unhonored.append(Flag(label="Claimed no dependency changes, but dependencies changed",
                                      severity="moderate", evidence="dependency manifest modified"))
            else:
                delivered.append(Flag(label="No new dependencies declared (as claimed)", severity="minor",
                                      evidence="no dependency manifest changed"))
    return delivered, unhonored
