from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from statistics import mean


DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "sample_review_data.json"


@dataclass
class CyberArkReviewSyncService:
    accounts: list[dict]

    def summary(self) -> dict:
        evaluations = self._evaluations()
        critical = sum(1 for item in evaluations if item["verdict"] == "critical")
        watch = sum(1 for item in evaluations if item["verdict"] == "watch")
        review_ready = sum(1 for item in evaluations if item["reviewReady"])
        stale = sum(1 for item in evaluations if item["staleAccess"])
        orphaned = sum(1 for item in evaluations if item["ownerGap"])
        hottest = max(self.account_catalog(), key=lambda item: item["riskScore"])
        return {
            "accountCount": len(self.accounts),
            "safeCount": len({account["safe"] for account in self.accounts}),
            "criticalCount": critical,
            "watchCount": watch,
            "reviewReadyCount": review_ready,
            "staleAccountCount": stale,
            "orphanedOwnerCount": orphaned,
            "averageRiskScore": round(mean(item["riskScore"] for item in evaluations), 1),
            "averageApprovalEvidenceAge": round(mean(item["approvalEvidenceDays"] for item in self.accounts), 1),
            "highestRiskAccount": hottest["name"],
            "leadRecommendation": self._lead_recommendation(evaluations),
        }

    def account_catalog(self) -> list[dict]:
        evaluations = {item["accountId"]: item for item in self._evaluations()}
        rows: list[dict] = []
        for account in self.accounts:
            evaluation = evaluations[account["accountId"]]
            rows.append(
                {
                    "accountId": account["accountId"],
                    "name": account["name"],
                    "platform": account["platform"],
                    "safe": account["safe"],
                    "environment": account["environment"],
                    "owner": account["owner"],
                    "reviewGroup": account["reviewGroup"],
                    "privilegeTier": account["privilegeTier"],
                    "lastAccessDays": account["lastAccessDays"],
                    "rotationAgeDays": account["rotationAgeDays"],
                    "reviewAgeDays": account["reviewAgeDays"],
                    "approvalEvidenceDays": account["approvalEvidenceDays"],
                    "riskScore": evaluation["riskScore"],
                    "verdict": evaluation["verdict"],
                    "reviewReady": evaluation["reviewReady"],
                    "staleAccess": evaluation["staleAccess"],
                    "ownerGap": evaluation["ownerGap"],
                    "topConcern": evaluation["topConcern"],
                    "nextAction": evaluation["nextAction"],
                }
            )
        return sorted(rows, key=lambda row: (row["riskScore"], row["reviewAgeDays"]), reverse=True)

    def account_detail(self, account_id: str) -> dict | None:
        account = next((item for item in self.accounts if item["accountId"] == account_id), None)
        if account is None:
            return None
        evaluation = self._evaluate_account(account)
        return {
            **account,
            "evaluation": evaluation,
            "approvalPayload": self._approval_payload(account, evaluation),
        }

    def review_queue(self) -> list[dict]:
        queue: list[dict] = []
        for account in self.accounts:
            evaluation = self._evaluate_account(account)
            if evaluation["verdict"] == "healthy":
                continue
            queue.append(
                {
                    "accountId": account["accountId"],
                    "name": account["name"],
                    "owner": account["owner"],
                    "reviewGroup": account["reviewGroup"],
                    "safe": account["safe"],
                    "platform": account["platform"],
                    "privilegeTier": account["privilegeTier"],
                    "riskScore": evaluation["riskScore"],
                    "verdict": evaluation["verdict"],
                    "reviewReady": evaluation["reviewReady"],
                    "staleAccess": evaluation["staleAccess"],
                    "ownerGap": evaluation["ownerGap"],
                    "topConcern": evaluation["topConcern"],
                    "nextAction": evaluation["nextAction"],
                }
            )
        return sorted(queue, key=lambda item: (item["riskScore"], item["staleAccess"], item["ownerGap"]), reverse=True)

    def findings(self) -> list[dict]:
        rows: list[dict] = []
        for account in self.accounts:
            evaluation = self._evaluate_account(account)
            rows.append(
                {
                    "accountId": account["accountId"],
                    "name": account["name"],
                    "owner": account["owner"],
                    "safe": account["safe"],
                    "privilegeTier": account["privilegeTier"],
                    "lastAccessDays": account["lastAccessDays"],
                    "reviewAgeDays": account["reviewAgeDays"],
                    "approvalEvidenceDays": account["approvalEvidenceDays"],
                    "hasOpenTicket": account["hasOpenTicket"],
                    "managerVerified": account["managerVerified"],
                    "verdict": evaluation["verdict"],
                    "reviewReady": evaluation["reviewReady"],
                }
            )
        return sorted(rows, key=lambda row: (row["reviewAgeDays"], row["approvalEvidenceDays"]), reverse=True)

    def sample_payload(self) -> dict:
        catalog = self.account_catalog()
        return {
            "dashboard": self.summary(),
            "highestRiskAccount": catalog[0],
            "reviewQueue": self.review_queue(),
            "findings": self.findings()[:4],
        }

    def sync_velocity(self) -> list[dict]:
        return [
            {"day": "Mon", "reviews": 5, "findings": 2},
            {"day": "Tue", "reviews": 9, "findings": 3},
            {"day": "Wed", "reviews": 7, "findings": 2},
            {"day": "Thu", "reviews": 13, "findings": 4},
            {"day": "Fri", "reviews": 18, "findings": 5},
            {"day": "Sat", "reviews": 11, "findings": 3},
            {"day": "Sun", "reviews": 8, "findings": 2},
        ]

    def audit_log(self) -> list[dict]:
        highest = self.account_catalog()[0]
        return [
            {
                "timestamp": "2026-05-14 09:30:12",
                "action": "SYNC_STARTED",
                "actor": "SYSTEM",
                "resource": "CyberArk Vault primary lane",
                "result": "Success",
                "detail": "Scheduled privileged-account metadata synchronization started.",
            },
            {
                "timestamp": "2026-05-14 09:32:48",
                "action": "METADATA_EXTRACTED",
                "actor": "SYSTEM",
                "resource": f"{len(self.accounts)} privileged accounts",
                "result": "Success",
                "detail": "Safe memberships, owner fields, and evidence ages extracted for review scoring.",
            },
            {
                "timestamp": "2026-05-14 09:36:01",
                "action": "QUEUE_PRIORITIZED",
                "actor": "SYSTEM",
                "resource": highest["name"],
                "result": "Success",
                "detail": "Highest-risk account promoted into the urgent review lane.",
            },
            {
                "timestamp": "2026-05-14 09:37:25",
                "action": "EVIDENCE_GAP_FLAGGED",
                "actor": "SYSTEM",
                "resource": "Approval evidence backlog",
                "result": "Success",
                "detail": "Accounts with missing or stale evidence bundles queued for certification refresh.",
            },
            {
                "timestamp": "2026-05-14 09:41:10",
                "action": "REVIEW_PACKET_EMITTED",
                "actor": "SYSTEM",
                "resource": "Approval-ready payload export",
                "result": "Success",
                "detail": "Structured evidence packet emitted for downstream governance workflows.",
            },
            {
                "timestamp": "2026-05-14 09:42:59",
                "action": "MANAGER_ATTESTATION_PENDING",
                "actor": "Review Ops",
                "resource": "Owner-verification lane",
                "result": "Failure",
                "detail": "A subset of accounts still lacks manager verification despite matching review windows.",
            },
        ]

    def configuration_posture(self) -> dict:
        return {
            "cyberark": {
                "apiBaseUrl": "https://vault-review.internal/api",
                "authType": "CyberArk Identity + certificate",
                "verifySsl": True,
                "sessionControl": "Dual-control enforced for critical safes",
            },
            "syncSettings": {
                "intervalMinutes": 30,
                "batchSize": 250,
                "autoRemediation": False,
                "evidenceRefreshThresholdDays": 45,
            },
            "targetSystems": [
                {"name": "ServiceNow review queue", "type": "workflow", "enabled": True},
                {"name": "Identity governance ledger", "type": "evidence pipeline", "enabled": True},
                {"name": "Quarterly certification export", "type": "governance handoff", "enabled": True},
                {"name": "Emergency revocation lane", "type": "control plane", "enabled": False},
            ],
        }

    def _evaluations(self) -> list[dict]:
        return [self._evaluate_account(account) for account in self.accounts]

    def _evaluate_account(self, account: dict) -> dict:
        risk_score = 16
        if account["privilegeTier"] == "critical":
            risk_score += 18
        elif account["privilegeTier"] == "high":
            risk_score += 10
        else:
            risk_score += 4

        if account["lastAccessDays"] > 120:
            risk_score += 18
        elif account["lastAccessDays"] > 60:
            risk_score += 10
        elif account["lastAccessDays"] > 30:
            risk_score += 5

        if account["reviewAgeDays"] > 90:
            risk_score += 16
        elif account["reviewAgeDays"] > 45:
            risk_score += 9

        if account["approvalEvidenceDays"] == 0:
            risk_score += 16
        elif account["approvalEvidenceDays"] > 90:
            risk_score += 10
        elif account["approvalEvidenceDays"] > 45:
            risk_score += 5

        if account["rotationAgeDays"] > 120:
            risk_score += 12
        elif account["rotationAgeDays"] > 60:
            risk_score += 6

        if account["owner"] == "Unassigned":
            risk_score += 14
        if not account["managerVerified"]:
            risk_score += 10
        if account["requiresDualApproval"] and not account["hasOpenTicket"]:
            risk_score += 10

        risk_score = min(100, risk_score)
        stale_access = account["lastAccessDays"] > 60
        owner_gap = account["owner"] == "Unassigned" or not account["managerVerified"]
        review_ready = account["hasOpenTicket"] and account["managerVerified"] and account["approvalEvidenceDays"] <= 45

        if risk_score >= 80:
            verdict = "critical"
            next_action = "Move the account into urgent review, collect approval evidence, and validate whether the entitlement still belongs in the vault."
        elif risk_score >= 55:
            verdict = "watch"
            next_action = "Refresh ownership and approval evidence before the next review window closes."
        else:
            verdict = "healthy"
            next_action = "Keep the account in the normal review cadence and preserve the current approval chain."

        return {
            "accountId": account["accountId"],
            "riskScore": risk_score,
            "verdict": verdict,
            "reviewReady": review_ready,
            "staleAccess": stale_access,
            "ownerGap": owner_gap,
            "topConcern": self._top_concern(account, stale_access, owner_gap),
            "nextAction": next_action,
        }

    def _top_concern(self, account: dict, stale_access: bool, owner_gap: bool) -> str:
        if owner_gap and stale_access:
            return "The account is both stale and weakly owned, which makes it a bad candidate for passive renewal."
        if account["approvalEvidenceDays"] == 0:
            return "Approval evidence is missing, so the next access review would fail to prove why this account still exists."
        if account["reviewAgeDays"] > 90:
            return "The review window is overdue for a privileged account that should already be in motion."
        if account["requiresDualApproval"] and not account["hasOpenTicket"]:
            return "The account still requires dual approval, but there is no open ticket proving that the latest access is expected."
        if stale_access:
            return "The account has not been touched recently enough to justify its current privilege posture."
        return "The account is still reviewable, but evidence and ownership should stay visible."

    def _lead_recommendation(self, evaluations: list[dict]) -> str:
        critical = [item for item in evaluations if item["verdict"] == "critical"]
        if critical:
            return "Force the stalest critical accounts into an urgent review queue before they silently roll into the next cycle without evidence."
        watch = [item for item in evaluations if item["verdict"] == "watch"]
        if watch:
            return "Prioritize approval evidence and manager verification refreshes so the review queue stays approval-ready."
        return "The current account surface is healthy enough to stay in the standard review cadence."

    def _approval_payload(self, account: dict, evaluation: dict) -> dict:
        return {
            "accountId": account["accountId"],
            "safe": account["safe"],
            "targetSystem": account["targetSystem"],
            "reviewGroup": account["reviewGroup"],
            "owner": account["owner"],
            "riskScore": evaluation["riskScore"],
            "verdict": evaluation["verdict"],
            "requiredEvidence": [
                "manager attestation",
                "ticket reference",
                "last access justification",
            ],
            "dualApprovalRequired": account["requiresDualApproval"],
        }


def build_service() -> CyberArkReviewSyncService:
    with DATA_PATH.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    return CyberArkReviewSyncService(accounts=payload["accounts"])
