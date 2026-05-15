from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from fastapi.testclient import TestClient

from app.main import app


def main() -> None:
    client = TestClient(app)
    routes = [
        "/",
        "/review-queue",
        "/findings",
        "/audit-log",
        "/settings",
        "/methodology",
        "/api-summary",
        "/api/dashboard/summary",
        "/api/sample",
    ]
    for route in routes:
        response = client.get(route)
        if response.status_code != 200:
            raise SystemExit(f"{route} failed with {response.status_code}")
    print("smoke check passed")


if __name__ == "__main__":
    main()
