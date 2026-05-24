from robotruth.scanners import run_scanners, ALL_SCANNERS
from robotruth.diffparse import Diff

def test_registry_nonempty_and_runs_empty_diff():
    assert len(ALL_SCANNERS) >= 4
    assert run_scanners(Diff(files=[]), []) == []
