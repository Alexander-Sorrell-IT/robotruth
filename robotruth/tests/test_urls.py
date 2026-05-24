import pytest
from robotruth.urls import parse_pr_url

def test_parses_standard_pr_url():
    assert parse_pr_url("https://github.com/facebook/react/pull/28471") == ("facebook", "react", 28471)

def test_parses_with_trailing_path_and_whitespace():
    assert parse_pr_url("  https://github.com/o/r/pull/5/files  ") == ("o", "r", 5)

def test_rejects_non_pr_url():
    with pytest.raises(ValueError):
        parse_pr_url("https://github.com/o/r/issues/5")
