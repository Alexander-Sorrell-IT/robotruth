"""Vercel entrypoint.

Vercel's Python/FastAPI runtime scans for a FastAPI instance named `app` at
default locations (app.py / index.py / main.py ...). Our real app lives in the
`robotruth_api` package, so we re-export it here at a default location to make
detection robust regardless of `tool.vercel.entrypoint` resolution.
"""

from robotruth_api.app import app  # noqa: F401
