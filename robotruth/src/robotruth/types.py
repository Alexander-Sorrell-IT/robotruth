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
