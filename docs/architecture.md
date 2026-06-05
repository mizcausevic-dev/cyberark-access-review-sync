# Architecture

`cyberark-access-review-sync` is a Python and FastAPI service for turning **CyberArk privileged-account metadata into a reviewable operations surface**.

It focuses on the access-governance questions that usually arrive too late:

- which privileged accounts have gone stale
- which records are overdue for review
- which accounts are missing current approval evidence
- which high-risk accounts still lack clean ownership or manager verification

## Core model

The service works from a seeded inventory in [app/data/sample_review_data.json](../app/data/sample_review_data.json).

Each account carries:

- account identity, safe, platform, and target system
- owner and review group
- environment and privilege tier
- last access age
- password rotation age
- review age
- approval evidence age
- ticket state and manager verification
- dual-approval expectations

## Evaluation flow

The review-sync service in [app/services/review_sync_service.py](../app/services/review_sync_service.py) computes:

1. risk score
2. verdict: `healthy`, `watch`, or `critical`
3. stale-access flag
4. owner-gap flag
5. review-ready flag
6. top concern
7. next action
8. approval-ready payload for downstream systems

The score deliberately mixes stale use, weak ownership, overdue reviews, and thin approval evidence so the queue feels operational instead of ceremonial.

## UI surfaces

The HTML proof layer in [app/render.py](../app/render.py) exposes:

- `/`
  Overview of account pressure, owner gaps, stale use, and top review lanes.
- `/review-queue`
  Prioritized queue of accounts that should be forced through review first.
- `/findings`
  Compact matrix for stale access, review age, evidence age, and approval readiness.
- `/methodology`
  Explains how the sync scores accounts and why.
- `/api-summary`
  Shows how the JSON outputs can flow into broader access governance systems.

## API layer

The FastAPI app in [app/main.py](../app/main.py) exposes both operator-facing views and machine-consumable endpoints so the same record can feed dashboards, review platforms, or audit workflows.

## Validation

The repo includes:

- unit tests in [tests/test_review_sync_service.py](../tests/test_review_sync_service.py)
- smoke checks in [scripts/smoke_check.py](../scripts/smoke_check.py)
- proof asset generation in [scripts/render_readme_assets.py](../scripts/render_readme_assets.py)
- GitHub Actions CI in [.github/workflows/ci.yml](../.github/workflows/ci.yml)
