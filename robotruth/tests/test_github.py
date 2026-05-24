import httpx
import pytest
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
    def handler(req):
        return httpx.Response(404, json={})
    with pytest.raises(LookupError):
        fetch_pr("o", "r", 9, client=httpx.Client(transport=httpx.MockTransport(handler)))
