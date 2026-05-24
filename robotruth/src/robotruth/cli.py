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
