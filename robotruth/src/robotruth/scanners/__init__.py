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
