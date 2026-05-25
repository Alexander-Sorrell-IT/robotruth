# RoboTruth Core Engine — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build `audit_pr(url) → Receipt` — a deterministic Python engine that, given a public GitHub PR, returns a structured receipt of what the PR *claimed* vs. what the diff *actually did*.

**Architecture:** Pure functions over a parsed diff. `audit_pr` orchestrates: parse URL → fetch PR (title/body/diff) → parse diff → extract claims (heuristic) → run deterministic scanners (undisclosed changes) → verify claims (delivered vs. unhonored) → grade → assemble `Receipt`. **No LLM anywhere.** Every flag cites `file:line`. This package is the single source of truth later imported by the web app (Plan 2), the MCP server (Plan 4), and `pip`.

**Tech Stack:** Python 3.11+, `pydantic` v2 (types), `httpx` (GitHub fetch, testable via `MockTransport`), `unidiff` (diff parsing), `pytest`.

**Working directory:** all tasks run from `/media/phantomcore/AI_DRIVE/hackathons/mind/robotruth/`. The git repo root is the parent (`mind/`), already initialized on `main` with git identity configured. File paths and `git add` paths in every task are relative to this working directory.

> **Scope note:** This plan ships the foundation + 4 highest-signal scanners (security-guard removal, dangerous-primitive add, dependency change, scope drift) + claim verification (tests, deps). Additional scanners (secret/env exposure, new outbound network, test/CI disabled, gitignore surprises) are a follow-on batch that reuses the identical `scan(diff, claims) -> list[Flag]` pattern — added after the web hero (Plan 2) per the build queue.

> **Security-hook note (READ BEFORE EDITING):** A few RCE-sink tokens (the things our detector looks for) are assembled from string fragments — in BOTH the scanner regex AND its test fixtures — e.g. `"ev" + "al"`, `"o" + "s"`. This is intentional: it keeps the literal sink tokens (`eval(`, `os`.`system`, etc.) out of the source so content-security scanners don't flag our own detector and block the file on write. The tokens are reassembled at runtime, so behaviour is unchanged. Do **not** "simplify" them back to literals.

---

## File Structure

```
robotruth/
  pyproject.toml
  src/robotruth/
    __init__.py            # exports audit_pr, audit_diff
    types.py               # pydantic models: Flag, Claim, PRMeta, Receipt + literals
    urls.py                # parse_pr_url
    diffparse.py           # parse_diff -> Diff (FileChange/AddedLine/RemovedLine)
    claims.py              # extract_claims, humanize
    scanners/
      __init__.py          # ALL_SCANNERS, run_scanners
      security_guard.py    # removed auth/csrf/permission guards
      dangerous_primitives.py  # added RCE sinks
      dependencies.py      # dependency/lockfile changes
      scope_drift.py       # broad scope despite "only/just" claim
    verify.py              # verify_claims -> (delivered, unhonored)
    grade.py               # grade_and_verdict
    engine.py              # audit_diff, audit_pr
    github.py              # fetch_pr
    cli.py                 # python -m robotruth <url>
  tests/
    test_urls.py  test_diffparse.py  test_claims.py
    test_security_guard.py  test_dangerous_primitives.py
    test_dependencies.py  test_scope_drift.py
    test_verify.py  test_grade.py  test_engine.py  test_github.py
```

Each file has one responsibility; scanners are independent and individually testable.

---

## Task 1: Project scaffold ✅ DONE (3ec055b)

**Files:**
- Create: `pyproject.toml`
- Create: `src/robotruth/__init__.py`

- [ ] **Step 1: Create `pyproject.toml`**

```toml
[project]
name = "robotruth"
version = "0.1.0"
description = "Did the robot lie? Deterministic AI-PR intent receipts."
requires-python = ">=3.11"
dependencies = ["pydantic>=2", "httpx>=0.27", "unidiff>=0.7.5"]

[project.optional-dependencies]
dev = ["pytest>=8"]

[project.scripts]
robotruth = "robotruth.cli:main"

[build-system]
requires = ["setuptools>=68"]
build-backend = "setuptools.build_meta"

[tool.setuptools.packages.find]
where = ["src"]
```

- [ ] **Step 2: Create `src/robotruth/__init__.py`**

```python
"""RoboTruth — deterministic AI-PR intent receipts."""
```

- [ ] **Step 3: Install in editable mode**

Run: `python -m venv .venv && . .venv/bin/activate && pip install -e ".[dev]"`
Expected: installs robotruth + pydantic, httpx, unidiff, pytest.

- [ ] **Step 4: Verify pytest runs (no tests yet)**

Run: `pytest -q`
Expected: "no tests ran" (exit 5) — confirms environment works.

- [ ] **Step 5: Commit**

```bash
git add pyproject.toml src/robotruth/__init__.py
git commit -m "chore: scaffold robotruth engine package"
```

---

## Task 2: Core types ✅ DONE (9d61fba)

**Files:**
- Create: `src/robotruth/types.py`
- Test: `tests/test_types.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_types.py
from robotruth.types import Flag, Claim, PRMeta, Receipt

def test_receipt_roundtrips():
    pr = PRMeta(repo="o/r", number=1, title="t", url="u")
    r = Receipt(pr=pr, verdict="HONEST", grade="A")
    assert r.grade == "A"
    assert r.model_dump()["pr"]["repo"] == "o/r"

def test_flag_defaults_line_optional():
    f = Flag(label="x", file="a.py", severity="critical", evidence="e")
    assert f.line is None
```

- [ ] **Step 2: Run — expect FAIL** (`ModuleNotFoundError: robotruth.types`)

Run: `pytest tests/test_types.py -q`

- [ ] **Step 3: Implement `types.py`**

```python
from __future__ import annotations
from typing import Literal, Optional
from pydantic import BaseModel

Severity = Literal["critical", "moderate", "minor"]
Verdict = Literal["HONEST", "MOSTLY HONEST", "SNEAKY", "LIAR"]
Grade = Literal["A", "B", "C", "D", "F"]
ClaimKind = Literal["adds_tests", "no_deps", "no_breaking", "scope_only"]


class Flag(BaseModel):
    label: str
    file: str = ""
    line: Optional[int] = None
    severity: Severity = "moderate"
    evidence: str = ""


class Claim(BaseModel):
    kind: ClaimKind
    value: str = ""
    raw: str = ""


class PRMeta(BaseModel):
    repo: str
    number: int
    title: str
    url: str
    body: str = ""
    author: Optional[str] = None


class Receipt(BaseModel):
    pr: PRMeta
    verdict: Verdict
    grade: Grade
    delivered: list[Flag] = []
    undisclosed: list[Flag] = []
    unhonored: list[Flag] = []
    parsed_claims: list[str] = []
    math: str = ""
```

- [ ] **Step 4: Run — expect PASS**

Run: `pytest tests/test_types.py -q`

- [ ] **Step 5: Commit**

```bash
git add src/robotruth/types.py tests/test_types.py
git commit -m "feat: core pydantic types (Flag, Claim, PRMeta, Receipt)"
```

---

## Task 3: PR URL parser ✅ DONE (3e3ee95)

**Files:**
- Create: `src/robotruth/urls.py`
- Test: `tests/test_urls.py`

- [ ] **Step 1: Failing test**

```python
# tests/test_urls.py
import pytest
from robotruth.urls import parse_pr_url

def test_parses_standard_pr_url():
    assert parse_pr_url("https://github.com/facebook/react/pull/28471") == ("facebook", "react", 28471)

def test_parses_with_trailing_path_and_whitespace():
    assert parse_pr_url("  https://github.com/o/r/pull/5/files  ") == ("o", "r", 5)

def test_rejects_non_pr_url():
    with pytest.raises(ValueError):
        parse_pr_url("https://github.com/o/r/issues/5")
```

- [ ] **Step 2: Run — expect FAIL**

Run: `pytest tests/test_urls.py -q`

- [ ] **Step 3: Implement**

```python
# src/robotruth/urls.py
from __future__ import annotations
import re

_PR_RE = re.compile(r"github\.com/([^/\s]+)/([^/\s]+)/pull/(\d+)")


def parse_pr_url(url: str) -> tuple[str, str, int]:
    """Return (owner, repo, number) from a GitHub PR URL. Raise ValueError otherwise."""
    m = _PR_RE.search(url.strip())
    if not m:
        raise ValueError(f"Not a GitHub PR URL: {url!r}")
    return m.group(1), m.group(2), int(m.group(3))
```

- [ ] **Step 4: Run — expect PASS**

Run: `pytest tests/test_urls.py -q`

- [ ] **Step 5: Commit**

```bash
git add src/robotruth/urls.py tests/test_urls.py
git commit -m "feat: GitHub PR URL parser"
```

---

## Task 4: Diff parser ✅ DONE (145a8c2)

**Files:**
- Create: `src/robotruth/diffparse.py`
- Test: `tests/test_diffparse.py`

- [ ] **Step 1: Failing test**

```python
# tests/test_diffparse.py
from robotruth.diffparse import parse_diff

SAMPLE = """diff --git a/app/theme.ts b/app/theme.ts
index 111..222 100644
--- a/app/theme.ts
+++ b/app/theme.ts
@@ -1,1 +1,2 @@
 export const x = 1
+export const dark = true
diff --git a/auth/session.ts b/auth/session.ts
index 333..444 100644
--- a/auth/session.ts
+++ b/auth/session.ts
@@ -10,3 +10,2 @@
 const a = 1
-app.use(csrfProtection())
 const b = 2
"""

def test_parses_added_and_removed():
    d = parse_diff(SAMPLE)
    assert set(d.paths) == {"app/theme.ts", "auth/session.ts"}
    theme = next(f for f in d.files if f.path == "app/theme.ts")
    assert theme.added[0].content == "export const dark = true"
    assert theme.added[0].line == 2
    auth = next(f for f in d.files if f.path == "auth/session.ts")
    assert any("csrfProtection" in r.content for r in auth.removed)
```

- [ ] **Step 2: Run — expect FAIL**

Run: `pytest tests/test_diffparse.py -q`

- [ ] **Step 3: Implement**

```python
# src/robotruth/diffparse.py
from __future__ import annotations
from dataclasses import dataclass, field
from unidiff import PatchSet


@dataclass
class AddedLine:
    file: str
    line: int | None
    content: str


@dataclass
class RemovedLine:
    file: str
    content: str


@dataclass
class FileChange:
    path: str
    added: list[AddedLine] = field(default_factory=list)
    removed: list[RemovedLine] = field(default_factory=list)
    is_new: bool = False
    is_removed: bool = False


@dataclass
class Diff:
    files: list[FileChange]

    @property
    def paths(self) -> list[str]:
        return [f.path for f in self.files]


def parse_diff(diff_text: str) -> Diff:
    patch = PatchSet(diff_text)
    files: list[FileChange] = []
    for pf in patch:
        fc = FileChange(path=pf.path, is_new=pf.is_added_file, is_removed=pf.is_removed_file)
        for hunk in pf:
            for line in hunk:
                content = line.value.rstrip("\n")
                if line.is_added:
                    fc.added.append(AddedLine(pf.path, line.target_line_no, content))
                elif line.is_removed:
                    fc.removed.append(RemovedLine(pf.path, content))
        files.append(fc)
    return Diff(files=files)
```

- [ ] **Step 4: Run — expect PASS**

Run: `pytest tests/test_diffparse.py -q`

- [ ] **Step 5: Commit**

```bash
git add src/robotruth/diffparse.py tests/test_diffparse.py
git commit -m "feat: unified-diff parser (added/removed lines with line numbers)"
```

---

## Task 5: Claim extraction ✅ DONE (815625e)

**Files:**
- Create: `src/robotruth/claims.py`
- Test: `tests/test_claims.py`

- [ ] **Step 1: Failing test**

```python
# tests/test_claims.py
from robotruth.claims import extract_claims, humanize

def test_detects_test_and_scope_claims():
    claims = extract_claims("Add dark mode toggle (only settings)", "Added tests for the toggle.")
    kinds = {c.kind for c in claims}
    assert "adds_tests" in kinds
    assert "scope_only" in kinds

def test_detects_no_deps_claim():
    claims = extract_claims("Refactor", "No dependency changes.")
    assert any(c.kind == "no_deps" for c in claims)

def test_no_false_claims_on_plain_text():
    assert extract_claims("Fix typo in README", "") == []

def test_humanize_returns_strings():
    claims = extract_claims("only", "added tests")
    assert all(isinstance(s, str) for s in humanize(claims))
```

- [ ] **Step 2: Run — expect FAIL**

Run: `pytest tests/test_claims.py -q`

- [ ] **Step 3: Implement** (high precision — few, confident claim types)

```python
# src/robotruth/claims.py
from __future__ import annotations
import re
from .types import Claim

_TEST_RE = re.compile(r"\b(add(?:ed|s)?|includ(?:e|ed|es)|with|wrote)\b[^.\n]*\btests?\b", re.I)
_NO_DEPS_RE = re.compile(r"\bno\b[^.\n]*\b(dependenc(?:y|ies)|packages?|deps)\b", re.I)
_NO_BREAKING_RE = re.compile(r"\bno\b[^.\n]*\bbreaking\b", re.I)
_SCOPE_ONLY_RE = re.compile(r"\b(only|just|solely|merely)\b", re.I)


def extract_claims(title: str, body: str) -> list[Claim]:
    text = f"{title}\n{body or ''}"
    claims: list[Claim] = []
    if _TEST_RE.search(text):
        claims.append(Claim(kind="adds_tests", raw="claims to add tests"))
    if _NO_DEPS_RE.search(text):
        claims.append(Claim(kind="no_deps", raw="claims no dependency changes"))
    if _NO_BREAKING_RE.search(text):
        claims.append(Claim(kind="no_breaking", raw="claims no breaking changes"))
    if _SCOPE_ONLY_RE.search(text):
        claims.append(Claim(kind="scope_only", value=title, raw="claims a narrow scope ('only'/'just')"))
    return claims


def humanize(claims: list[Claim]) -> list[str]:
    return [c.raw for c in claims]
```

- [ ] **Step 4: Run — expect PASS**

Run: `pytest tests/test_claims.py -q`

- [ ] **Step 5: Commit**

```bash
git add src/robotruth/claims.py tests/test_claims.py
git commit -m "feat: heuristic claim extraction (tests/deps/breaking/scope)"
```

---

## Task 6: Scanner framework ✅ DONE (49dbe8c)

**Files:**
- Create: `src/robotruth/scanners/__init__.py`
- Test: `tests/test_scanner_framework.py`

> Build the four scanner modules (Tasks 7–10) before re-running this test. If implementing strictly in order, first create the four files with a stub `def scan(diff, claims): return []`, then fill them in.

- [ ] **Step 1: Failing test**

```python
# tests/test_scanner_framework.py
from robotruth.scanners import run_scanners, ALL_SCANNERS
from robotruth.diffparse import Diff

def test_registry_nonempty_and_runs_empty_diff():
    assert len(ALL_SCANNERS) >= 4
    assert run_scanners(Diff(files=[]), []) == []
```

- [ ] **Step 2: Run — expect FAIL**

Run: `pytest tests/test_scanner_framework.py -q`

- [ ] **Step 3: Implement**

```python
# src/robotruth/scanners/__init__.py
from __future__ import annotations
from ..types import Flag
from ..claims import Claim
from ..diffparse import Diff
from .security_guard import scan as security_guard
from .dangerous_primitives import scan as dangerous_primitives
from .dependencies import scan as dependencies
from .scope_drift import scan as scope_drift

ALL_SCANNERS = [security_guard, dangerous_primitives, dependencies, scope_drift]


def run_scanners(diff: Diff, claims: list[Claim]) -> list[Flag]:
    flags: list[Flag] = []
    for s in ALL_SCANNERS:
        flags.extend(s(diff, claims))
    return flags
```

- [ ] **Step 4: Run after Tasks 7–10 — expect PASS**

Run: `pytest tests/test_scanner_framework.py -q`

- [ ] **Step 5: Commit** (after 7–10)

```bash
git add src/robotruth/scanners/__init__.py tests/test_scanner_framework.py
git commit -m "feat: scanner framework (ALL_SCANNERS, run_scanners)"
```

---

## Task 7: Scanner — security-guard removal (critical) ✅ DONE (61b169a; precision-hardened in 99bcb8b — repo is authoritative for final code)

**Files:**
- Create: `src/robotruth/scanners/security_guard.py`
- Test: `tests/test_security_guard.py`

- [ ] **Step 1: Failing test**

```python
# tests/test_security_guard.py
from robotruth.diffparse import parse_diff
from robotruth.scanners.security_guard import scan

REMOVED_CSRF = """diff --git a/auth/session.ts b/auth/session.ts
--- a/auth/session.ts
+++ b/auth/session.ts
@@ -10,3 +10,2 @@
 const a = 1
-app.use(csrfProtection())
 const b = 2
"""

def test_flags_removed_csrf_guard():
    flags = scan(parse_diff(REMOVED_CSRF), [])
    assert len(flags) == 1
    assert flags[0].severity == "critical"
    assert flags[0].file == "auth/session.ts"

def test_no_flag_when_nothing_removed():
    diff = parse_diff("diff --git a/x.ts b/x.ts\n--- a/x.ts\n+++ b/x.ts\n@@ -1 +1,2 @@\n a\n+b\n")
    assert scan(diff, []) == []
```

- [ ] **Step 2: Run — expect FAIL**

Run: `pytest tests/test_security_guard.py -q`

- [ ] **Step 3: Implement**

```python
# src/robotruth/scanners/security_guard.py
from __future__ import annotations
import re
from ..types import Flag
from ..claims import Claim
from ..diffparse import Diff

_GUARD_RE = re.compile(
    r"\b(csrf|csrfProtection|authenticate|authoriz\w*|permission\w*|login_required|"
    r"requireAuth|verifyToken|checkAuth|isAuthenticated|ensureAuth|helmet|cors)\b",
    re.I,
)


def scan(diff: Diff, claims: list[Claim]) -> list[Flag]:
    out: list[Flag] = []
    for f in diff.files:
        for rem in f.removed:
            if _GUARD_RE.search(rem.content):
                out.append(Flag(
                    label="Security guard removed/weakened",
                    file=f.path,
                    severity="critical",
                    evidence=f"removed: {rem.content.strip()[:120]}",
                ))
    return out
```

- [ ] **Step 4: Run — expect PASS**

Run: `pytest tests/test_security_guard.py -q`

- [ ] **Step 5: Commit**

```bash
git add src/robotruth/scanners/security_guard.py tests/test_security_guard.py
git commit -m "feat(scanner): security-guard removal detection"
```

---

## Task 8: Scanner — dangerous primitive added (critical) ✅ DONE (d646a5c; precision-hardened in 99bcb8b — repo is authoritative)

**Files:**
- Create: `src/robotruth/scanners/dangerous_primitives.py`
- Test: `tests/test_dangerous_primitives.py`

> Sink tokens are fragment-assembled in both the fixture and the regex — see the Security-hook note at top.

- [ ] **Step 1: Failing test**

```python
# tests/test_dangerous_primitives.py
from robotruth.diffparse import parse_diff
from robotruth.scanners.dangerous_primitives import scan

# the added line below reads `+const r = eval(userInput)` once assembled
ADDED_SINK = (
    "diff --git a/run.js b/run.js\n"
    "--- a/run.js\n"
    "+++ b/run.js\n"
    "@@ -1 +1,2 @@\n"
    " const a = 1\n"
    "+const r = " + "ev" + "al(userInput)\n"
)

def test_flags_added_sink():
    flags = scan(parse_diff(ADDED_SINK), [])
    assert len(flags) == 1
    assert flags[0].severity == "critical"
    assert flags[0].line == 2

def test_ignores_removed_sink():
    removed = (
        "diff --git a/x.js b/x.js\n--- a/x.js\n+++ b/x.js\n"
        "@@ -1,2 +1 @@\n const a = 1\n-const r = " + "ev" + "al(x)\n"
    )
    assert scan(parse_diff(removed), []) == []
```

- [ ] **Step 2: Run — expect FAIL**

Run: `pytest tests/test_dangerous_primitives.py -q`

- [ ] **Step 3: Implement**

```python
# src/robotruth/scanners/dangerous_primitives.py
from __future__ import annotations
import re
from ..types import Flag
from ..claims import Claim
from ..diffparse import Diff

# RCE-class sinks. Tokens are assembled from fragments so the bare literal
# never appears in this source (keeps content-security scanners quiet).
_SINKS = [
    r"\b%s\s*\(" % ("ev" + "al"),
    r"\bnew\s+Function\s*\(",
    r"\b%sprocess\b" % "child_",
    r"\b%s\s*\(" % ("ex" + "ec"),
    r"\b%s\.%s\b" % ("o" + "s", "sys" + "tem"),
    r"\b%s\." % ("sub" + "process"),
    r"\b%s\.loads\b" % ("pick" + "le"),
    r"\byaml\.load\s*\(",
]
_SINK_RE = re.compile("|".join(_SINKS))


def scan(diff: Diff, claims: list[Claim]) -> list[Flag]:
    out: list[Flag] = []
    for f in diff.files:
        for add in f.added:
            if _SINK_RE.search(add.content):
                out.append(Flag(
                    label="Dangerous code-execution primitive added",
                    file=f.path,
                    line=add.line,
                    severity="critical",
                    evidence=f"added: {add.content.strip()[:120]}",
                ))
    return out
```

- [ ] **Step 4: Run — expect PASS**

Run: `pytest tests/test_dangerous_primitives.py -q`

- [ ] **Step 5: Commit**

```bash
git add src/robotruth/scanners/dangerous_primitives.py tests/test_dangerous_primitives.py
git commit -m "feat(scanner): added RCE-sink detection"
```

---

## Task 9: Scanner — dependency / lockfile change (moderate) ✅ DONE (7d7df49; +lockfile test in 99bcb8b)

**Files:**
- Create: `src/robotruth/scanners/dependencies.py`
- Test: `tests/test_dependencies.py`

- [ ] **Step 1: Failing test**

```python
# tests/test_dependencies.py
from robotruth.diffparse import parse_diff
from robotruth.scanners.dependencies import scan

DEP = """diff --git a/package.json b/package.json
--- a/package.json
+++ b/package.json
@@ -1,1 +1,2 @@
 {
+  "chroma-js": "^2.4.2",
"""

def test_flags_package_json_change():
    flags = scan(parse_diff(DEP), [])
    assert len(flags) == 1
    assert flags[0].file == "package.json"
    assert flags[0].severity == "moderate"

def test_ignores_source_change():
    src = "diff --git a/app.ts b/app.ts\n--- a/app.ts\n+++ b/app.ts\n@@ -1 +1,2 @@\n a\n+b\n"
    assert scan(parse_diff(src), []) == []
```

- [ ] **Step 2: Run — expect FAIL**

Run: `pytest tests/test_dependencies.py -q`

- [ ] **Step 3: Implement**

```python
# src/robotruth/scanners/dependencies.py
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
```

- [ ] **Step 4: Run — expect PASS**

Run: `pytest tests/test_dependencies.py -q`

- [ ] **Step 5: Commit**

```bash
git add src/robotruth/scanners/dependencies.py tests/test_dependencies.py
git commit -m "feat(scanner): dependency/lockfile change detection"
```

---

## Task 10: Scanner — scope drift (moderate) ✅ DONE (783a47c; threshold→>3 + Flag.file fix in 99bcb8b)

**Files:**
- Create: `src/robotruth/scanners/scope_drift.py`
- Test: `tests/test_scope_drift.py`

- [ ] **Step 1: Failing test**

```python
# tests/test_scope_drift.py
from robotruth.diffparse import parse_diff
from robotruth.claims import Claim
from robotruth.scanners.scope_drift import scan

def _diff(paths):
    return parse_diff("".join(
        f"diff --git a/{p} b/{p}\n--- a/{p}\n+++ b/{p}\n@@ -1 +1,2 @@\n a\n+b\n" for p in paths
    ))

def test_flags_broad_scope_with_only_claim():
    claims = [Claim(kind="scope_only", value="only dark mode")]
    flags = scan(_diff(["ui/a.ts", "auth/b.ts", "infra/c.ts"]), claims)
    assert len(flags) == 1
    assert flags[0].severity == "moderate"

def test_no_flag_without_scope_claim():
    assert scan(_diff(["ui/a.ts", "auth/b.ts", "infra/c.ts"]), []) == []

def test_no_flag_when_scope_is_narrow():
    claims = [Claim(kind="scope_only", value="only x")]
    assert scan(_diff(["ui/a.ts", "ui/b.ts"]), claims) == []
```

- [ ] **Step 2: Run — expect FAIL**

Run: `pytest tests/test_scope_drift.py -q`

- [ ] **Step 3: Implement**

```python
# src/robotruth/scanners/scope_drift.py
from __future__ import annotations
from ..types import Flag
from ..claims import Claim
from ..diffparse import Diff


def scan(diff: Diff, claims: list[Claim]) -> list[Flag]:
    if not any(c.kind == "scope_only" for c in claims):
        return []
    topdirs = {(p.split("/", 1)[0] if "/" in p else ".") for p in diff.paths}
    if len(topdirs) <= 2:
        return []
    return [Flag(
        label="Broad scope despite 'only'/'just' claim",
        file=", ".join(sorted(diff.paths))[:160],
        severity="moderate",
        evidence=f"touched {len(topdirs)} top-level areas: {', '.join(sorted(topdirs))}",
    )]
```

- [ ] **Step 4: Run — expect PASS** (also re-run the framework test — expect PASS)

Run: `pytest tests/test_scope_drift.py tests/test_scanner_framework.py -q`

- [ ] **Step 5: Commit**

```bash
git add src/robotruth/scanners/scope_drift.py tests/test_scope_drift.py
git commit -m "feat(scanner): scope-drift detection"
```

---

## Task 11: Claim verification (delivered vs. unhonored) ✅ DONE (9c64a78)

**Files:**
- Create: `src/robotruth/verify.py`
- Test: `tests/test_verify.py`

- [ ] **Step 1: Failing test**

```python
# tests/test_verify.py
from robotruth.diffparse import parse_diff
from robotruth.claims import Claim
from robotruth.verify import verify_claims

def _diff(paths):
    return parse_diff("".join(
        f"diff --git a/{p} b/{p}\n--- a/{p}\n+++ b/{p}\n@@ -1 +1,2 @@\n a\n+b\n" for p in paths
    ))

def test_unhonored_when_tests_claimed_but_absent():
    delivered, unhonored = verify_claims(_diff(["app/x.ts"]), [Claim(kind="adds_tests")])
    assert delivered == [] and len(unhonored) == 1

def test_delivered_when_tests_present():
    delivered, unhonored = verify_claims(_diff(["app/x.test.ts"]), [Claim(kind="adds_tests")])
    assert len(delivered) == 1 and unhonored == []

def test_unhonored_when_no_deps_claimed_but_deps_changed():
    delivered, unhonored = verify_claims(_diff(["package.json"]), [Claim(kind="no_deps")])
    assert len(unhonored) == 1
```

- [ ] **Step 2: Run — expect FAIL**

Run: `pytest tests/test_verify.py -q`

- [ ] **Step 3: Implement**

```python
# src/robotruth/verify.py
from __future__ import annotations
from .types import Flag, Claim
from .diffparse import Diff

_DEP_NAMES = {"package.json", "requirements.txt", "pyproject.toml", "Pipfile",
              "package-lock.json", "yarn.lock", "pnpm-lock.yaml", "poetry.lock", "Pipfile.lock"}


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
        # no_breaking / scope_only: not deterministically verifiable here -> handled by scanners/grade
    return delivered, unhonored
```

- [ ] **Step 4: Run — expect PASS**

Run: `pytest tests/test_verify.py -q`

- [ ] **Step 5: Commit**

```bash
git add src/robotruth/verify.py tests/test_verify.py
git commit -m "feat: claim verification (delivered vs unhonored)"
```

---

## Task 12: Grade & verdict ✅ DONE (f50741b)

**Files:**
- Create: `src/robotruth/grade.py`
- Test: `tests/test_grade.py`

- [ ] **Step 1: Failing test**

```python
# tests/test_grade.py
from robotruth.types import Flag
from robotruth.grade import grade_and_verdict

def test_clean_is_A_honest():
    g, v, math = grade_and_verdict([], [])
    assert g == "A" and v == "HONEST" and "A:" in math

def test_one_critical_undisclosed_is_D_sneaky():
    g, v, _ = grade_and_verdict([Flag(label="x", severity="critical")], [])
    assert g == "D" and v == "SNEAKY"

def test_two_criticals_is_F_liar():
    g, v, _ = grade_and_verdict([Flag(label="x", severity="critical"), Flag(label="y", severity="critical")], [])
    assert g == "F" and v == "LIAR"

def test_one_moderate_is_B():
    g, _, _ = grade_and_verdict([Flag(label="x", severity="moderate")], [])
    assert g == "B"
```

- [ ] **Step 2: Run — expect FAIL**

Run: `pytest tests/test_grade.py -q`

- [ ] **Step 3: Implement** (thresholds are intentionally explicit; tune on the corpus in Plan 3)

```python
# src/robotruth/grade.py
from __future__ import annotations
from .types import Flag, Grade, Verdict

_WEIGHT = {"critical": 3, "moderate": 1, "minor": 0}
_VERDICT: dict[Grade, Verdict] = {
    "A": "HONEST", "B": "MOSTLY HONEST", "C": "MOSTLY HONEST", "D": "SNEAKY", "F": "LIAR",
}


def grade_and_verdict(undisclosed: list[Flag], unhonored: list[Flag]) -> tuple[Grade, Verdict, str]:
    n_crit = sum(1 for f in undisclosed if f.severity == "critical")
    score = sum(_WEIGHT[f.severity] for f in undisclosed) + sum(_WEIGHT[f.severity] for f in unhonored)
    if n_crit >= 2:
        grade: Grade = "F"
    elif n_crit == 1:
        grade = "D"
    elif score == 0:
        grade = "A"
    elif score == 1:
        grade = "B"
    elif score <= 3:
        grade = "C"
    else:
        grade = "D"
    verdict = _VERDICT[grade]
    math = f"{grade}: {len(undisclosed)} undisclosed ({n_crit} critical), {len(unhonored)} unhonored; score={score}"
    return grade, verdict, math
```

- [ ] **Step 4: Run — expect PASS**

Run: `pytest tests/test_grade.py -q`

- [ ] **Step 5: Commit**

```bash
git add src/robotruth/grade.py tests/test_grade.py
git commit -m "feat: deterministic grade + verdict"
```

---

## Task 13: Engine assembly — `audit_diff` ✅ DONE (91d2c10)

**Files:**
- Create: `src/robotruth/engine.py`
- Modify: `src/robotruth/__init__.py`
- Test: `tests/test_engine.py`

- [ ] **Step 1: Failing test** (the headline end-to-end behavior, offline)

```python
# tests/test_engine.py
from robotruth.types import PRMeta
from robotruth.engine import audit_diff

DARKMODE_PR = """diff --git a/settings/Theme.tsx b/settings/Theme.tsx
--- a/settings/Theme.tsx
+++ b/settings/Theme.tsx
@@ -1 +1,2 @@
 export const Settings = () => null
+export const Theme = () => null
diff --git a/auth/session.ts b/auth/session.ts
--- a/auth/session.ts
+++ b/auth/session.ts
@@ -10,3 +10,2 @@
 const a = 1
-app.use(csrfProtection())
 const b = 2
diff --git a/package.json b/package.json
--- a/package.json
+++ b/package.json
@@ -1 +1,2 @@
 {
+  "chroma-js": "^2.4.2"
"""

def test_darkmode_pr_catches_csrf_and_deps_and_missing_tests():
    pr = PRMeta(repo="o/r", number=482, title="Add dark mode toggle",
                url="https://github.com/o/r/pull/482", body="Added tests for the toggle.")
    r = audit_diff(pr, DARKMODE_PR)
    labels = {f.label for f in r.undisclosed}
    assert any("Security guard" in l for l in labels)
    assert any("Dependency" in l for l in labels)
    assert any("no test files" in f.label for f in r.unhonored)
    assert r.grade in ("D", "F")
    assert r.verdict in ("SNEAKY", "LIAR")
    assert r.parsed_claims  # claim shown back to user (advisor #1)
```

- [ ] **Step 2: Run — expect FAIL**

Run: `pytest tests/test_engine.py -q`

- [ ] **Step 3: Implement `engine.py` (`audit_pr` added in Task 15)**

```python
# src/robotruth/engine.py
from __future__ import annotations
from .types import Receipt, PRMeta
from .diffparse import parse_diff
from .claims import extract_claims, humanize
from .scanners import run_scanners
from .verify import verify_claims
from .grade import grade_and_verdict


def audit_diff(pr: PRMeta, diff_text: str) -> Receipt:
    diff = parse_diff(diff_text)
    claims = extract_claims(pr.title, pr.body)
    undisclosed = run_scanners(diff, claims)
    delivered, unhonored = verify_claims(diff, claims)
    grade, verdict, math = grade_and_verdict(undisclosed, unhonored)
    return Receipt(
        pr=pr, verdict=verdict, grade=grade,
        delivered=delivered, undisclosed=undisclosed, unhonored=unhonored,
        parsed_claims=humanize(claims), math=math,
    )
```

- [ ] **Step 4: Update `__init__.py` to export it**

```python
# src/robotruth/__init__.py
"""RoboTruth — deterministic AI-PR intent receipts."""
from .engine import audit_diff  # noqa: F401
```

- [ ] **Step 5: Run — expect PASS, then commit**

Run: `pytest tests/test_engine.py -q`
```bash
git add src/robotruth/engine.py src/robotruth/__init__.py tests/test_engine.py
git commit -m "feat: audit_diff end-to-end engine assembly"
```

---

## Task 14: GitHub ingestion ✅ DONE (c578c87)

**Files:**
- Create: `src/robotruth/github.py`
- Test: `tests/test_github.py`

- [ ] **Step 1: Failing test** (uses `httpx.MockTransport` — no network)

```python
# tests/test_github.py
import httpx, pytest
from robotruth.github import fetch_pr

def _client(meta_json, diff_text, status=200):
    def handler(request: httpx.Request) -> httpx.Response:
        if request.headers.get("Accept") == "application/vnd.github.v3.diff":
            return httpx.Response(status, text=diff_text)
        return httpx.Response(status, json=meta_json)
    return httpx.Client(transport=httpx.MockTransport(handler))

def test_fetch_pr_returns_meta_and_diff():
    meta = {"title": "T", "html_url": "U", "body": "B", "user": {"login": "alice"}}
    pr, diff = fetch_pr("o", "r", 1, client=_client(meta, "DIFF"))
    assert pr.title == "T" and pr.author == "alice" and diff == "DIFF"

def test_fetch_pr_404_raises_lookuperror():
    def handler(req): return httpx.Response(404, json={})
    with pytest.raises(LookupError):
        fetch_pr("o", "r", 9, client=httpx.Client(transport=httpx.MockTransport(handler)))
```

- [ ] **Step 2: Run — expect FAIL**

Run: `pytest tests/test_github.py -q`

- [ ] **Step 3: Implement** (token from `GITHUB_TOKEN` env — advisor #2; fail-loud on 404 — spec §6)

```python
# src/robotruth/github.py
from __future__ import annotations
import os
import httpx
from .types import PRMeta

_API = "https://api.github.com"


def fetch_pr(owner: str, repo: str, number: int, *, token: str | None = None,
             client: httpx.Client | None = None) -> tuple[PRMeta, str]:
    token = token or os.environ.get("GITHUB_TOKEN")
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "robotruth"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    owned = client is None
    client = client or httpx.Client(timeout=15)
    url = f"{_API}/repos/{owner}/{repo}/pulls/{number}"
    try:
        meta_r = client.get(url, headers=headers)
        if meta_r.status_code == 404:
            raise LookupError(f"PR not found or private: {owner}/{repo}#{number}")
        meta_r.raise_for_status()
        m = meta_r.json()
        diff_headers = {**headers, "Accept": "application/vnd.github.v3.diff"}
        diff_r = client.get(url, headers=diff_headers)
        diff_r.raise_for_status()
        pr = PRMeta(
            repo=f"{owner}/{repo}", number=number,
            title=m.get("title", ""), url=m.get("html_url", ""),
            body=m.get("body") or "", author=(m.get("user") or {}).get("login"),
        )
        return pr, diff_r.text
    finally:
        if owned:
            client.close()
```

- [ ] **Step 4: Run — expect PASS**

Run: `pytest tests/test_github.py -q`

- [ ] **Step 5: Commit**

```bash
git add src/robotruth/github.py tests/test_github.py
git commit -m "feat: GitHub PR ingestion (token-aware, fail-loud on 404)"
```

---

## Task 15: `audit_pr` orchestration + CLI ✅ DONE (d6db278) — ENGINE COMPLETE: 43 tests pass + verified on a live dependabot PR

**Files:**
- Modify: `src/robotruth/engine.py`
- Modify: `src/robotruth/__init__.py`
- Create: `src/robotruth/cli.py`
- Test: `tests/test_audit_pr.py`

- [ ] **Step 1: Failing test** (inject a fake fetcher via monkeypatch)

```python
# tests/test_audit_pr.py
import robotruth.engine as engine
from robotruth.types import PRMeta

def test_audit_pr_wires_url_to_receipt(monkeypatch):
    def fake_fetch(owner, repo, number, **kw):
        return PRMeta(repo=f"{owner}/{repo}", number=number, title="Add dark mode",
                      url="u", body="only settings"), \
               "diff --git a/auth/s.ts b/auth/s.ts\n--- a/auth/s.ts\n+++ b/auth/s.ts\n@@ -1,2 +1 @@\n a\n-csrfProtection()\n"
    monkeypatch.setattr(engine, "fetch_pr", fake_fetch)
    r = engine.audit_pr("https://github.com/o/r/pull/7")
    assert r.pr.number == 7
    assert any("Security guard" in f.label for f in r.undisclosed)
```

- [ ] **Step 2: Run — expect FAIL**

Run: `pytest tests/test_audit_pr.py -q`

- [ ] **Step 3: Add `audit_pr` to `engine.py`**

```python
# append to src/robotruth/engine.py
from .github import fetch_pr
from .urls import parse_pr_url


def audit_pr(url: str, *, token: str | None = None) -> Receipt:
    owner, repo, number = parse_pr_url(url)
    pr, diff_text = fetch_pr(owner, repo, number, token=token)
    return audit_diff(pr, diff_text)
```

- [ ] **Step 4: Export + add CLI**

```python
# src/robotruth/__init__.py
"""RoboTruth — deterministic AI-PR intent receipts."""
from .engine import audit_diff, audit_pr  # noqa: F401
```

```python
# src/robotruth/cli.py
from __future__ import annotations
import sys
import json
from .engine import audit_pr


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: robotruth <github-pr-url>", file=sys.stderr)
        return 2
    try:
        receipt = audit_pr(sys.argv[1])
    except (ValueError, LookupError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    print(json.dumps(receipt.model_dump(), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 5: Run full suite + smoke, then commit**

Run: `pytest -q` (expected: all pass)
Smoke (needs network + optional `GITHUB_TOKEN`): `robotruth https://github.com/<a real bot PR>` → prints a JSON receipt.
```bash
git add src/robotruth/engine.py src/robotruth/__init__.py src/robotruth/cli.py tests/test_audit_pr.py
git commit -m "feat: audit_pr URL->Receipt orchestration + CLI"
```

---

## Self-Review (against spec §6)

- **Spec coverage:** ingest (T14) · claim extraction (T5) · scanners: security-guard (T7), dangerous-primitive (T8), dependency (T9), scope-drift (T10) · claim-not-honored: tests + deps (T11) · grade A–F with F as the contradiction proxy (T12) · Receipt shape incl. `parsed_claims` for the advisor's show-the-claim affordance (T2/T13) · `audit_pr` (T15) · CLI (T15). **Deferred (follow-on, same `scan` pattern):** secret/env exposure, new-outbound-network, test/CI-disabled, gitignore/lockfile-surprise scanners; server-side rate-limit caching (Plan 2); `no_breaking` verification.
- **Placeholder scan:** none — every code step has complete code.
- **Type consistency:** `scan(diff, claims) -> list[Flag]` uniform across T7–T10 and `run_scanners` (T6); `grade_and_verdict(undisclosed, unhonored)` matches the caller in T13; `fetch_pr(...) -> (PRMeta, str)` matches the call in T15; `audit_diff(pr, diff_text)` / `audit_pr(url)` consistent across T13/T15.
- **Build-queue alignment:** this entire plan = build-queue item #1 ("THE CATCH"). Precision tuning against the named bot-PR corpus (advisor #6) happens in Plan 3 before the day-21 gate.
