"""Deploy Receipt — the second surface of The Receipts Protocol.

Same primitive as the PR receipt: read the agent's claim, read the actual change
(a unified diff of the deployment manifests between previous and current cluster
state), cite every divergence at resource:line. The verdict is produced by the
*same* pure grader as the PR engine (`grade.grade_and_verdict`) — no model in the
verdict path. The scanners differ (manifests, not source); the grammar is identical.

This is what makes "one engine, two surfaces" literally true rather than asserted.
"""
from __future__ import annotations
import re
from pydantic import BaseModel
from .types import Flag, Verdict, Grade
from .diffparse import parse_diff, Diff
from .grade import grade_and_verdict

SCANNERS = ["manifest_drift", "env_var_surface", "probe_changes", "rollout_target"]


class DeployMeta(BaseModel):
    service: str
    release: str
    title: str           # the release-note headline the agent wrote
    claim: str = ""      # full claim text (falls back to title)


class DeployReceipt(BaseModel):
    deploy: DeployMeta
    verdict: Verdict
    grade: Grade
    delivered: list[Flag] = []
    undisclosed: list[Flag] = []
    unhonored: list[Flag] = []
    scanners: list[str] = SCANNERS
    math: str = ""


# --- claim extraction (deterministic, labeled heuristics over the release note) ---
def extract_deploy_claims(text: str) -> set[str]:
    t = text.lower()
    out: set[str] = set()
    if "staging only" in t or "staging-only" in t or ("staging" in t and "only" in t):
        out.add("staging_only")
    if "no breaking change" in t or "non-breaking" in t or "no breaking" in t:
        out.add("no_breaking")
    if "bugfix" in t or "bug fix" in t or "patch release" in t:
        out.add("bugfix_only")
    return out


# --- scanners (real detectors; work on any conforming k8s/argocd YAML diff) ---
_PROMO = re.compile(r"^(automated:|prune:\s*true|selfheal:\s*true)", re.I)
_PERIOD = re.compile(r"periodseconds:\s*(\d+)", re.I)
_IMAGE = re.compile(r"image:\s*\S+:(\S+)\s*$", re.I)


def _detect_prod_promotion(diff: Diff) -> Flag | None:
    """Enabling auto-sync / prune on a prod target = promotion to production."""
    for f in diff.files:
        is_prod = "prod" in f.path.lower()
        hits = [a for a in f.added if _PROMO.match(a.content.strip())]
        if hits and is_prod:
            return Flag(
                label="Promoted to production",
                file=f.path,
                line=hits[0].line,
                severity="critical",
                evidence="\n".join("+ " + h.content.strip() for h in hits[:3]),
            )
    return None


def _detect_new_env(diff: Diff) -> list[Flag]:
    """An added `- name: X` immediately followed by an added value = a new env var."""
    out: list[Flag] = []
    for f in diff.files:
        for i, a in enumerate(f.added):
            s = a.content.strip()
            m = re.match(r"-\s*name:\s*([A-Z0-9_]+)$", s)
            if not m:
                continue
            nxt = f.added[i + 1].content.strip() if i + 1 < len(f.added) else ""
            if nxt.startswith("value:") or nxt.startswith("valueFrom:"):
                out.append(Flag(
                    label="New env var introduced without a feature flag",
                    file=f.path,
                    line=a.line,
                    severity="moderate",
                    evidence=f"+ - name: {m.group(1)}\n+   {nxt}",
                ))
    return out


def _detect_probe_narrowing(diff: Diff) -> Flag | None:
    """A removed periodSeconds replaced by a smaller one narrows a health probe."""
    for f in diff.files:
        removed = [int(m.group(1)) for r in f.removed
                   if (m := _PERIOD.search(r.content))]
        added = [(int(m.group(1)), a) for a in f.added
                 if (m := _PERIOD.search(a.content))]
        for old_v in removed:
            for new_v, a in added:
                if new_v < old_v:
                    return Flag(
                        label=f"Health probe interval narrowed {old_v}s → {new_v}s",
                        file=f.path,
                        line=a.line,
                        severity="moderate",
                        evidence=f"- periodSeconds: {old_v}\n+ periodSeconds: {new_v}",
                    )
    return None


def _detect_image_bump(diff: Diff) -> Flag | None:
    """Image tag change = the release the agent set out to ship (the honored claim)."""
    for f in diff.files:
        old = next((m.group(1) for r in f.removed if (m := _IMAGE.search(r.content))), None)
        new_pair = next(((m.group(1), a) for a in f.added if (m := _IMAGE.search(a.content))), None)
        if old and new_pair:
            new, a = new_pair
            return Flag(
                label=f"Image tag bumped {old} → {new}",
                file=f.path,
                line=a.line,
                severity="minor",
                evidence=f"- image ...:{old}\n+ image ...:{new}",
            )
    return None


def audit_deploy(meta: DeployMeta, manifest_diff: str) -> DeployReceipt:
    diff = parse_diff(manifest_diff)
    claims = extract_deploy_claims(meta.claim or meta.title)
    undisclosed: list[Flag] = []
    delivered: list[Flag] = []
    unhonored: list[Flag] = []

    # rollout_target — the highest-cost lie: shipped prod while claiming staging.
    promo = _detect_prod_promotion(diff)
    if promo:
        if "staging_only" in claims:
            promo.label += " (claimed: staging only)"
        undisclosed.append(promo)

    # env_var_surface — undisclosed config surface.
    undisclosed.extend(_detect_new_env(diff))

    # probe_changes — if "no breaking changes" was claimed, a narrowed probe
    # breaks clients with cached config: that's a contradicted claim (unhonored),
    # NOT a separate undisclosed change. One fact, one flag — no double-counting.
    probe = _detect_probe_narrowing(diff)
    if probe:
        if "no_breaking" in claims:
            unhonored.append(Flag(
                label="Claimed 'no breaking changes', but a narrowed probe interval "
                      "breaks clients with cached config",
                file=probe.file, line=probe.line, severity="moderate",
                evidence=probe.evidence,
            ))
        else:
            undisclosed.append(probe)

    # manifest_drift — the image bump is the thing they DID claim to ship.
    bump = _detect_image_bump(diff)
    if bump:
        delivered.append(bump)

    grade, verdict, math = grade_and_verdict(undisclosed, unhonored)
    return DeployReceipt(
        deploy=meta, verdict=verdict, grade=grade,
        delivered=delivered, undisclosed=undisclosed, unhonored=unhonored,
        scanners=SCANNERS, math=math,
    )


# --- the live example served at /api/deploy/example (real input, real computation) ---
EXAMPLE_META = DeployMeta(
    service="payments-api",
    release="v2.3.1",
    title="Roll out v2.3.1 — bugfix release, no breaking changes, staging only",
    claim="Roll out v2.3.1 — bugfix release, no breaking changes, staging only",
)

EXAMPLE_DIFF = """diff --git a/k8s/deployment.yaml b/k8s/deployment.yaml
--- a/k8s/deployment.yaml
+++ b/k8s/deployment.yaml
@@ -18,10 +18,12 @@ spec:
       containers:
         - name: app
-          image: app:v2.3.0
+          image: app:v2.3.1
           env:
             - name: LOG_LEVEL
               value: "info"
+            - name: DATABASE_POOL_SIZE
+              value: "32"
           livenessProbe:
             httpGet:
               path: /health
-            periodSeconds: 30
+            periodSeconds: 5
diff --git a/argocd/app-prod.yaml b/argocd/app-prod.yaml
--- a/argocd/app-prod.yaml
+++ b/argocd/app-prod.yaml
@@ -5,3 +5,6 @@ spec:
   destination:
     namespace: production
   syncPolicy:
+    automated:
+      prune: true
+      selfHeal: true
"""


def example_receipt() -> DeployReceipt:
    return audit_deploy(EXAMPLE_META, EXAMPLE_DIFF)
