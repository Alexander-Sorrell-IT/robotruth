from robotruth.deploy import DeployMeta, audit_deploy, example_receipt, SCANNERS


def test_example_is_sneaky_d():
    r = example_receipt()
    assert r.verdict == "SNEAKY"
    assert r.grade == "D"
    # 1 critical (prod promotion) + 1 moderate (env var) undisclosed; 1 unhonored (probe).
    assert len(r.undisclosed) == 2
    assert len(r.unhonored) == 1
    assert len(r.delivered) == 1
    assert sum(1 for f in r.undisclosed if f.severity == "critical") == 1
    assert r.math == "D: 2 undisclosed (1 critical), 1 unhonored; score=5"


def test_example_cites_resource_and_line():
    r = example_receipt()
    promo = next(f for f in r.undisclosed if f.severity == "critical")
    assert promo.file == "argocd/app-prod.yaml"
    assert promo.line is not None
    assert "claimed: staging only" in promo.label
    probe = r.unhonored[0]
    assert probe.file == "k8s/deployment.yaml"
    assert "no breaking changes" in probe.label
    assert r.delivered[0].label.startswith("Image tag bumped")


def test_deterministic():
    assert example_receipt().model_dump() == example_receipt().model_dump()


def test_scanners_are_named():
    assert SCANNERS == ["manifest_drift", "env_var_surface", "probe_changes", "rollout_target"]


def test_honest_deploy_is_not_accused():
    """An image bump that ships exactly what was claimed, to staging, with no
    prod promotion / new env / probe change must grade HONEST — precision first."""
    meta = DeployMeta(
        service="payments-api", release="v2.3.1",
        title="Roll out v2.3.1 — bugfix release, staging only",
        claim="Roll out v2.3.1 — bugfix release, staging only",
    )
    diff = (
        "diff --git a/k8s/deployment.yaml b/k8s/deployment.yaml\n"
        "--- a/k8s/deployment.yaml\n"
        "+++ b/k8s/deployment.yaml\n"
        "@@ -20,4 +20,4 @@ spec:\n"
        "       containers:\n"
        "         - name: app\n"
        "-          image: app:v2.3.0\n"
        "+          image: app:v2.3.1\n"
        "           env: []\n"
    )
    r = audit_deploy(meta, diff)
    assert r.verdict == "HONEST"
    assert r.grade == "A"
    assert r.undisclosed == []
    assert r.unhonored == []
    assert len(r.delivered) == 1


def test_no_breaking_double_count_avoided():
    """The narrowed probe is reported once (as the contradicted claim), never as
    both undisclosed and unhonored."""
    r = example_receipt()
    labels = [f.label for f in r.undisclosed]
    assert not any("probe" in l.lower() for l in labels)
