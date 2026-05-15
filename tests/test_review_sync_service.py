from __future__ import annotations

import unittest

from fastapi.testclient import TestClient

from app.main import app
from app.services.review_sync_service import build_service


class CyberArkAccessReviewSyncTests(unittest.TestCase):
    def test_summary_shape(self) -> None:
        summary = build_service().summary()
        self.assertGreaterEqual(summary["accountCount"], 6)
        self.assertGreaterEqual(summary["safeCount"], 5)
        self.assertIn("leadRecommendation", summary)

    def test_review_queue_has_high_risk_first(self) -> None:
        queue = build_service().review_queue()
        self.assertGreaterEqual(queue[0]["riskScore"], queue[-1]["riskScore"])
        self.assertIn(queue[0]["verdict"], {"watch", "critical"})

    def test_account_lookup_api(self) -> None:
        client = TestClient(app)
        response = client.get("/api/accounts/acct-prod-oracle-finance")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["name"], "FIN-ORACLE-ROOT")


if __name__ == "__main__":
    unittest.main()
