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
