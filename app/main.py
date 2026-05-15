from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse

from app.render import (
    render_api_summary,
    render_findings_matrix,
    render_methodology,
    render_overview,
    render_review_queue,
)
from app.services.review_sync_service import build_service

app = FastAPI(
    title="CyberArk Access Review Sync",
    version="0.1.0",
    description=(
        "FastAPI integration surface for syncing CyberArk privileged-account metadata into access-review queues, "
        "stale-access findings, and approval-ready evidence payloads."
    ),
)

SERVICE = build_service()


@app.get("/", response_class=HTMLResponse)
def overview() -> str:
    return render_overview()


@app.get("/review-queue", response_class=HTMLResponse)
def review_queue() -> str:
    return render_review_queue()


@app.get("/findings", response_class=HTMLResponse)
def findings() -> str:
    return render_findings_matrix()


@app.get("/methodology", response_class=HTMLResponse)
def methodology() -> str:
    return render_methodology()


@app.get("/api-summary", response_class=HTMLResponse)
def api_summary() -> str:
    return render_api_summary()


@app.get("/api/dashboard/summary")
def dashboard_summary() -> dict:
    return SERVICE.summary()


@app.get("/api/accounts")
def accounts() -> list[dict]:
    return SERVICE.account_catalog()


@app.get("/api/accounts/{account_id}")
def account_detail(account_id: str) -> dict:
    account = SERVICE.account_detail(account_id)
    if account is None:
        raise HTTPException(status_code=404, detail="Account not found")
    return account


@app.get("/api/reviews")
def reviews() -> list[dict]:
    return SERVICE.review_queue()


@app.get("/api/findings")
def findings_api() -> list[dict]:
    return SERVICE.findings()


@app.get("/api/sample")
def sample() -> dict:
    return SERVICE.sample_payload()


if __name__ == "__main__":
    import os

    import uvicorn

    port = int(os.environ.get("PORT", "4961"))
    uvicorn.run("app.main:app", host="127.0.0.1", port=port, reload=False)
