from __future__ import annotations

import json
from html import escape

from app.services.review_sync_service import build_service


SERVICE = build_service()


def _account_lookup() -> dict[str, dict]:
    return {account["accountId"]: account for account in SERVICE.accounts}


def _verdict_class(verdict: str) -> str:
    return {"healthy": "healthy", "watch": "watch", "critical": "critical"}[verdict]


def _score_bars(account: dict) -> str:
    metrics = [
        ("Access staleness", min(100, round(account["lastAccessDays"] / 1.6))),
        ("Review age", min(100, round(account["reviewAgeDays"] / 1.2))),
        ("Rotation age", min(100, round(account["rotationAgeDays"] / 1.5))),
        ("Evidence freshness", max(0, 100 - min(100, round(account["approvalEvidenceDays"] / 1.2)))),
    ]
    rows = []
    for label, value in metrics:
        tone = "good" if value < 45 else "watch" if value < 75 else "hot"
        if label == "Evidence freshness":
            tone = "good" if value >= 70 else "watch" if value >= 45 else "hot"
        rows.append(
            f"""
            <div class="meter-row">
              <div class="meter-head">
                <span>{escape(label)}</span>
                <span>{round(value)}%</span>
              </div>
              <div class="meter-track"><div class="meter-fill {tone}" style="width: {value:.1f}%"></div></div>
            </div>
            """
        )
    return "".join(rows)


def _shell(title: str, subtitle: str, current: str, body: str) -> str:
    summary = SERVICE.summary()
    nav_items = [
        ("/", "Overview", "overview"),
        ("/review-queue", "Review Queue", "queue"),
        ("/findings", "Findings", "findings"),
        ("/methodology", "Methodology", "methodology"),
    ]
    sidebar = "".join(
        f"""<a class="side-link {'active' if key == current else ''}" href="{href}">{escape(label)}</a>"""
        for href, label, key in nav_items
    )
    tabs = "".join(
        f"""<a class="tab-pill {'active' if key == current else ''}" href="{href}">{escape(label)}</a>"""
        for href, label, key in nav_items
    )
    return f"""<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>{escape(title)}</title>
    <style>
      :root {{
        color-scheme: dark;
        --bg: #04070d;
        --panel: rgba(9, 16, 28, 0.9);
        --line: rgba(255,255,255,0.07);
        --text: #f5f7fd;
        --muted: #96a9c6;
        --blue: #74c8ff;
        --indigo: #5d78ff;
        --green: #49d79e;
        --amber: #f6c46a;
        --red: #ff7987;
      }}
      * {{ box-sizing: border-box; }}
      body {{
        margin: 0;
        font-family: Inter, "Segoe UI", system-ui, sans-serif;
        color: var(--text);
        background:
          radial-gradient(circle at top left, rgba(116,200,255,0.14), transparent 24%),
          radial-gradient(circle at top right, rgba(255,121,135,0.08), transparent 16%),
          linear-gradient(180deg, #02050a 0%, #050912 100%);
      }}
      a {{ color: inherit; text-decoration: none; }}
      .shell {{ min-height: 100vh; display: grid; grid-template-columns: 248px minmax(0,1fr); }}
      .sidebar {{
        background: rgba(0,0,0,0.3);
        border-right: 1px solid rgba(255,255,255,0.06);
        backdrop-filter: blur(16px);
        padding: 24px 18px;
        display: flex;
        flex-direction: column;
      }}
      .brand {{
        display: flex; align-items: center; gap: 12px; padding: 8px 10px 18px;
        border-bottom: 1px solid rgba(255,255,255,0.06);
      }}
      .brand-mark {{
        width: 40px; height: 40px; border-radius: 12px; display:grid; place-items:center;
        background: linear-gradient(135deg, #0c97c2, #5d78ff); color:white; font-weight:900;
        box-shadow: 0 0 18px rgba(93,120,255,0.28);
      }}
      .brand strong {{ display:block; font-size:14px; }}
      .brand span {{ display:block; margin-top:4px; color:var(--blue); font-size:10px; letter-spacing:.18em; text-transform:uppercase; }}
      nav {{ margin-top: 18px; }}
      .side-link {{
        display:block; padding:13px 14px; border-radius:14px; color:#8195b4; font-size:12px;
        font-weight:700; text-transform:uppercase; letter-spacing:.12em; transition:all 150ms ease;
      }}
      .side-link.active {{ color:var(--blue); background:rgba(116,200,255,0.08); border:1px solid rgba(116,200,255,0.16); }}
      .side-link:hover {{ color:var(--text); background:rgba(255,255,255,0.04); }}
      .meta {{ margin-top:auto; padding:16px 12px 8px; border-top:1px solid rgba(255,255,255,0.06); }}
      .meta dt {{ color:#687c98; font-size:10px; text-transform:uppercase; letter-spacing:.14em; margin-bottom:4px; }}
      .meta dd {{ margin:0 0 14px; font-size:12px; font-weight:700; }}
      .topbar {{
        height:72px; position:sticky; top:0; z-index:2; display:flex; align-items:center; justify-content:space-between;
        padding:0 34px; background:rgba(0,0,0,0.34); border-bottom:1px solid rgba(255,255,255,0.06); backdrop-filter: blur(16px);
      }}
      .status-chip {{
        display:inline-flex; align-items:center; gap:10px; padding:9px 14px; border-radius:999px;
        border:1px solid rgba(116,200,255,0.14); background:rgba(116,200,255,0.05); color:#b9e1ff;
        font-size:10px; font-weight:800; text-transform:uppercase; letter-spacing:.18em;
      }}
      .status-dot {{ width:8px; height:8px; border-radius:50%; background:var(--blue); box-shadow:0 0 12px rgba(116,200,255,0.84); }}
      .topbar-right {{ display:flex; align-items:center; gap:22px; }}
      .meta-block {{ display:flex; flex-direction:column; align-items:flex-end; }}
      .meta-block span {{ color:#6d809b; font-size:9px; text-transform:uppercase; letter-spacing:.15em; }}
      .meta-block strong {{ margin-top:4px; font-size:11px; text-transform:uppercase; letter-spacing:.12em; }}
      .action-pill {{
        display:inline-flex; align-items:center; padding:12px 16px; border-radius:999px; color:white;
        background:linear-gradient(135deg, #0f8fbf, #5d78ff); box-shadow:0 0 20px rgba(93,120,255,0.24);
        font-size:10px; font-weight:900; letter-spacing:.18em; text-transform:uppercase;
      }}
      .wrap {{ max-width: 1280px; margin:0 auto; padding:34px; }}
      .hero {{
        border:1px solid var(--line); border-radius:28px; padding:28px;
        background: linear-gradient(180deg, rgba(9,16,28,0.96), rgba(6,11,20,0.94));
        box-shadow: 0 26px 60px rgba(0,0,0,0.34);
      }}
      .hero-eyebrow {{ margin-bottom:18px; color:var(--blue); font-size:11px; letter-spacing:.28em; text-transform:uppercase; font-weight:800; }}
      h1 {{ margin:0; font-size:clamp(38px,5vw,70px); line-height:.92; font-family:Georgia, "Times New Roman", serif; letter-spacing:-.04em; }}
      .hero-subtitle {{ margin-top:14px; max-width:860px; color:var(--muted); font-size:19px; line-height:1.55; }}
      .hero-strip {{ display:flex; flex-wrap:wrap; gap:14px; margin-top:24px; }}
      .hero-kpi {{ min-width:180px; padding:14px 16px; border-radius:18px; border:1px solid rgba(255,255,255,0.06); background:rgba(255,255,255,0.03); }}
      .hero-kpi .k {{ color:#6f83a0; font-size:10px; text-transform:uppercase; letter-spacing:.14em; font-weight:800; }}
      .hero-kpi .v {{ margin-top:6px; font-size:28px; font-weight:800; }}
      .hero-callout {{
        margin-top:18px; padding:18px 20px; border-radius:18px; border:1px solid rgba(255,255,255,0.06); background:rgba(2,8,17,0.62);
      }}
      .hero-callout strong {{ display:block; color:var(--amber); font-size:10px; text-transform:uppercase; letter-spacing:.18em; margin-bottom:8px; }}
      .hero-callout p {{ margin:0; color:#dce7fb; font-size:17px; line-height:1.5; }}
      .tab-row {{ display:flex; gap:10px; flex-wrap:wrap; margin-top:20px; }}
      .tab-pill {{
        display:inline-flex; align-items:center; padding:10px 14px; border-radius:999px; border:1px solid rgba(255,255,255,0.08);
        background:rgba(255,255,255,0.03); color:#afc0d8; font-size:11px; font-weight:800; text-transform:uppercase; letter-spacing:.12em;
      }}
      .tab-pill.active {{ color:var(--amber); border-color:rgba(246,196,106,0.18); background:rgba(246,196,106,0.08); }}
      .page-section {{ margin-top:24px; border-radius:26px; border:1px solid var(--line); background:var(--panel); overflow:hidden; box-shadow:0 24px 54px rgba(0,0,0,0.24); }}
      .section-head {{ padding:20px 24px 14px; border-bottom:1px solid rgba(255,255,255,0.05); }}
      .section-head strong {{ display:block; color:var(--blue); font-size:10px; text-transform:uppercase; letter-spacing:.2em; margin-bottom:10px; }}
      .section-head h2 {{ margin:0; font-family:Georgia, "Times New Roman", serif; font-size:24px; letter-spacing:-.03em; }}
      .section-head p {{ margin:10px 0 0; color:var(--muted); font-size:15px; line-height:1.55; }}
      .section-body {{ padding:24px; }}
      .stats-grid {{ display:grid; gap:18px; grid-template-columns:repeat(4,minmax(0,1fr)); }}
      .stat-card {{ border-radius:20px; padding:18px 18px 20px; border:1px solid rgba(255,255,255,0.06); background:linear-gradient(180deg, rgba(255,255,255,0.04), rgba(0,0,0,0.08)); }}
      .stat-card .label {{ color:#71839d; font-size:10px; text-transform:uppercase; letter-spacing:.16em; font-weight:800; }}
      .stat-card .value {{ margin-top:10px; font-size:36px; font-weight:900; }}
      .stat-card .sub {{ margin-top:10px; color:var(--muted); font-size:14px; line-height:1.45; }}
      .insight-grid {{ display:grid; gap:18px; grid-template-columns:1.35fr 1fr; }}
      .panel {{ border-radius:22px; border:1px solid rgba(255,255,255,0.06); background:rgba(4,9,18,0.55); padding:22px; }}
      .panel h3 {{ margin:0 0 16px; font-size:18px; }}
      .panel-grid {{ display:grid; gap:14px; }}
      .metric-card {{ padding:16px; border:1px solid rgba(255,255,255,0.05); border-radius:18px; background:rgba(255,255,255,0.028); }}
      .metric-card .micro {{ color:#6f83a0; font-size:9px; text-transform:uppercase; letter-spacing:.16em; font-weight:800; }}
      .metric-card .title {{ margin-top:8px; font-size:15px; font-weight:800; }}
      .metric-card .desc {{ margin-top:8px; color:var(--muted); font-size:13px; line-height:1.5; }}
      .meter-row + .meter-row {{ margin-top:14px; }}
      .meter-head {{ display:flex; justify-content:space-between; gap:16px; margin-bottom:8px; color:#cfe0f7; font-size:12px; font-weight:700; }}
      .meter-track {{ height:10px; border-radius:999px; background:rgba(255,255,255,0.05); overflow:hidden; }}
      .meter-fill {{ height:100%; border-radius:999px; }}
      .meter-fill.good {{ background:linear-gradient(90deg, #1e7fc7, #49d79e); box-shadow:0 0 18px rgba(73,215,158,0.2); }}
      .meter-fill.watch {{ background:linear-gradient(90deg, #2f82ff, #f6c46a); box-shadow:0 0 18px rgba(246,196,106,0.18); }}
      .meter-fill.hot {{ background:linear-gradient(90deg, #d14d6c, #ff7987); box-shadow:0 0 18px rgba(255,121,135,0.2); }}
      .account-grid {{ display:grid; gap:16px; }}
      .account-card {{ border-radius:22px; border:1px solid rgba(255,255,255,0.06); background:rgba(4,9,18,0.6); overflow:hidden; }}
      .account-top {{ display:grid; grid-template-columns:minmax(0,1fr) auto auto; gap:18px; align-items:center; padding:20px 22px; }}
      .account-card h3 {{ margin:0; font-size:22px; font-weight:800; letter-spacing:-.03em; }}
      .account-card .meta {{ margin-top:8px; color:var(--muted); font-size:13px; }}
      .tag {{ display:inline-flex; align-items:center; justify-content:center; padding:8px 12px; border-radius:999px; font-size:10px; font-weight:900; letter-spacing:.16em; text-transform:uppercase; }}
      .healthy {{ color:var(--green); background:rgba(73,215,158,0.12); border:1px solid rgba(73,215,158,0.14); }}
      .watch {{ color:var(--amber); background:rgba(246,196,106,0.12); border:1px solid rgba(246,196,106,0.14); }}
      .critical {{ color:var(--red); background:rgba(255,121,135,0.12); border:1px solid rgba(255,121,135,0.14); }}
      .score-stack {{ text-align:right; }}
      .score-stack .micro {{ color:#6f83a0; font-size:9px; text-transform:uppercase; letter-spacing:.16em; font-weight:800; }}
      .score-stack .value {{ margin-top:6px; font-size:28px; font-weight:900; }}
      .account-bottom {{ padding:18px 22px 22px; border-top:1px solid rgba(255,255,255,0.05); background:rgba(255,255,255,0.02); }}
      .two-col {{ display:grid; grid-template-columns:1fr 1fr; gap:18px; }}
      .signal-pill {{ display:inline-flex; align-items:center; padding:8px 10px; border-radius:999px; background:rgba(116,200,255,0.09); color:var(--blue); font-size:10px; font-weight:800; letter-spacing:.12em; text-transform:uppercase; }}
      .pill-stack {{ display:flex; flex-wrap:wrap; gap:10px; }}
      .table-shell {{ overflow:hidden; border-radius:22px; border:1px solid rgba(255,255,255,0.06); background:rgba(4,9,18,0.58); }}
      table {{ width:100%; border-collapse:collapse; }}
      th, td {{ padding:16px 18px; text-align:left; vertical-align:top; }}
      thead th {{ color:#7385a0; font-size:10px; text-transform:uppercase; letter-spacing:.18em; font-weight:900; background:rgba(255,255,255,0.035); }}
      tbody tr + tr td {{ border-top:1px solid rgba(255,255,255,0.05); }}
      tbody tr:hover td {{ background:rgba(116,200,255,0.03); }}
      .subtext {{ margin-top:6px; color:var(--muted); font-size:12px; line-height:1.45; }}
      .code-panel {{ border-radius:22px; border:1px solid rgba(255,255,255,0.08); background:rgba(2,6,12,0.92); padding:18px 20px 20px; }}
      .code-head {{ display:flex; align-items:center; justify-content:space-between; padding-bottom:12px; margin-bottom:16px; border-bottom:1px solid rgba(255,255,255,0.08); }}
      .code-head span {{ color:var(--blue); font-size:10px; font-weight:800; text-transform:uppercase; letter-spacing:.18em; }}
      .lights {{ display:flex; gap:7px; }}
      .lights i {{ display:block; width:9px; height:9px; border-radius:50%; }}
      .lights i:nth-child(1) {{ background:rgba(255,121,135,0.7); }}
      .lights i:nth-child(2) {{ background:rgba(246,196,106,0.7); }}
      .lights i:nth-child(3) {{ background:rgba(73,215,158,0.7); }}
      pre {{ margin:0; white-space:pre-wrap; overflow:auto; color:#dce8fb; font-size:13px; line-height:1.6; font-family:"Cascadia Code", Consolas, monospace; }}
      .footer-strip {{ display:flex; justify-content:space-between; gap:16px; margin-top:18px; padding:4px 2px 10px; color:#6d809b; font-size:10px; text-transform:uppercase; letter-spacing:.16em; }}
      .footer-strip strong {{ color:#b8c9de; }}
      @media (max-width:1080px) {{
        .shell {{ grid-template-columns:1fr; }}
        .sidebar {{ display:none; }}
        .stats-grid, .insight-grid, .two-col {{ grid-template-columns:1fr; }}
        .account-top {{ grid-template-columns:1fr; align-items:start; }}
      }}
    </style>
  </head>
  <body>
    <div class="shell">
      <aside class="sidebar">
        <div class="brand">
          <div class="brand-mark">CA</div>
          <div>
            <strong>CyberArk Access Review Sync</strong>
            <span>Instance: VAULT-REVIEW</span>
          </div>
        </div>
        <nav>{sidebar}</nav>
        <dl class="meta">
          <dt>Control lane</dt>
          <dd>Privileged review sync</dd>
          <dt>Urgent accounts</dt>
          <dd>{summary["criticalCount"]} critical / {summary["watchCount"]} watch</dd>
          <dt>Owner gaps</dt>
          <dd>{summary["orphanedOwnerCount"]} accounts</dd>
        </dl>
      </aside>
      <main>
        <header class="topbar">
          <div class="status-chip"><span class="status-dot"></span>Vault review feed live</div>
          <div class="topbar-right">
            <div class="meta-block"><span>Integration lane</span><strong>CyberArk / review ops</strong></div>
            <div class="meta-block"><span>Stale accounts</span><strong>{summary["staleAccountCount"]} in queue</strong></div>
            <a class="action-pill" href="/docs">Open API docs</a>
          </div>
        </header>
        <div class="wrap">
          <section class="hero">
            <div class="hero-eyebrow">CyberArk Access Review Sync</div>
            <h1>{escape(title)}</h1>
            <p class="hero-subtitle">{escape(subtitle)}</p>
            <div class="hero-strip">
              <div class="hero-kpi"><div class="k">Privileged accounts</div><div class="v">{summary["accountCount"]}</div></div>
              <div class="hero-kpi"><div class="k">Urgent review lanes</div><div class="v">{summary["criticalCount"]}</div></div>
              <div class="hero-kpi"><div class="k">Review-ready accounts</div><div class="v">{summary["reviewReadyCount"]}</div></div>
              <div class="hero-kpi"><div class="k">Highest-risk account</div><div class="v" style="font-size:20px">{escape(summary["highestRiskAccount"])}</div></div>
            </div>
            <div class="hero-callout">
              <strong>Lead recommendation</strong>
              <p>{escape(summary["leadRecommendation"])}</p>
            </div>
            <div class="tab-row">{tabs}</div>
          </section>
          {body}
          <div class="footer-strip">
            <span><strong>Discipline:</strong> privileged access review</span>
            <span><strong>Focus:</strong> stale access / ownership / evidence</span>
            <span><strong>Surface:</strong> operator-first / audit-legible</span>
          </div>
        </div>
      </main>
    </div>
  </body>
</html>"""


def render_overview() -> str:
    summary = SERVICE.summary()
    catalog = SERVICE.account_catalog()
    raw = _account_lookup()
    cards = []
    for row in catalog[:4]:
        account = raw[row["accountId"]]
        flags = []
        if row["staleAccess"]:
            flags.append('<span class="signal-pill">Stale access</span>')
        if row["ownerGap"]:
            flags.append('<span class="signal-pill">Owner gap</span>')
        if not row["reviewReady"]:
            flags.append('<span class="signal-pill">Missing review evidence</span>')
        cards.append(
            f"""
            <div class="account-card">
              <div class="account-top">
                <div>
                  <h3>{escape(row["name"])}</h3>
                  <div class="meta">{escape(row["owner"])} · {escape(row["safe"])} · {escape(row["platform"])} · {escape(row["privilegeTier"])}</div>
                </div>
                <span class="tag {_verdict_class(row["verdict"])}">{escape(row["verdict"])}</span>
                <div class="score-stack">
                  <div class="micro">Risk score</div>
                  <div class="value">{row["riskScore"]}</div>
                </div>
              </div>
              <div class="account-bottom">
                <div class="two-col">
                  <div>{_score_bars(account)}</div>
                  <div class="panel-grid">
                    <div class="metric-card">
                      <div class="micro">Top concern</div>
                      <div class="title">{escape(row["topConcern"])}</div>
                      <div class="desc">{escape(row["nextAction"])}</div>
                    </div>
                    <div class="metric-card">
                      <div class="micro">Review signals</div>
                      <div class="pill-stack">{"".join(flags) or '<span class="signal-pill">Review-ready</span>'}</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            """
        )
    body = f"""
      <section class="page-section">
        <div class="section-head">
          <strong>Review overview</strong>
          <h2>Privileged accounts that should not drift through the next cycle silently.</h2>
          <p>This surface is for the practical work of deciding which CyberArk accounts belong in the urgent queue, which ones are review-ready, and which ones are still missing evidence or ownership.</p>
        </div>
        <div class="section-body">
          <div class="stats-grid">
            <div class="stat-card">
              <div class="label">Safes in scope</div>
              <div class="value">{summary["safeCount"]}</div>
              <div class="sub">Distinct safes carrying the current review surface.</div>
            </div>
            <div class="stat-card">
              <div class="label">Stale accounts</div>
              <div class="value">{summary["staleAccountCount"]}</div>
              <div class="sub">Privileged accounts with access patterns that no longer justify passive renewal.</div>
            </div>
            <div class="stat-card">
              <div class="label">Owner gaps</div>
              <div class="value">{summary["orphanedOwnerCount"]}</div>
              <div class="sub">Accounts missing clean manager verification or assigned ownership.</div>
            </div>
            <div class="stat-card">
              <div class="label">Average risk</div>
              <div class="value">{summary["averageRiskScore"]}</div>
              <div class="sub">Combined pressure from stale use, old reviews, weak evidence, and ownership ambiguity.</div>
            </div>
          </div>
          <div class="insight-grid" style="margin-top:20px;">
            <div class="panel">
              <h3>What the sync is looking for</h3>
              <div class="panel-grid">
                <div class="metric-card">
                  <div class="micro">Stale access</div>
                  <div class="title">Not every quiet account is harmless.</div>
                  <div class="desc">Long-unused privileged accounts can survive quarter after quarter if nobody forces them into the review queue with evidence attached.</div>
                </div>
                <div class="metric-card">
                  <div class="micro">Approval evidence</div>
                  <div class="title">Review-ready should mean defensible.</div>
                  <div class="desc">The system keeps ticket state, manager verification, and approval age close together so operators can see whether the record is actually approvable.</div>
                </div>
              </div>
            </div>
            <div class="panel">
              <h3>Operator notes</h3>
              <div class="panel-grid">
                <div class="metric-card">
                  <div class="micro">Highest risk lane</div>
                  <div class="title">{escape(summary["highestRiskAccount"])}</div>
                  <div class="desc">The most dangerous accounts are usually the ones that combine stale use with weak evidence and thin ownership.</div>
                </div>
                <div class="metric-card">
                  <div class="micro">Approval backlog</div>
                  <div class="title">{summary["reviewReadyCount"]} accounts are review-ready.</div>
                  <div class="desc">Everything else still needs evidence refresh, ownership cleanup, or a live ticket before it can move cleanly through the next review.</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>
      <section class="page-section">
        <div class="section-head">
          <strong>Account board</strong>
          <h2>The sync keeps the riskiest privileged accounts visible.</h2>
          <p>Every row is meant to answer the question that matters most in access review: does this account still deserve the privilege it is carrying?</p>
        </div>
        <div class="section-body">
          <div class="account-grid">{"".join(cards)}</div>
        </div>
      </section>
    """
    return _shell(
        "Review sync overview",
        "Syncing CyberArk privileged-account metadata into access-review queues, stale-access findings, and approval-ready evidence payloads.",
        "overview",
        body,
    )


def render_review_queue() -> str:
    queue = SERVICE.review_queue()
    cards = []
    for row in queue:
        flags = []
        if row["staleAccess"]:
            flags.append('<span class="signal-pill">Stale access</span>')
        if row["ownerGap"]:
            flags.append('<span class="signal-pill">Owner gap</span>')
        if not row["reviewReady"]:
            flags.append('<span class="signal-pill">Evidence refresh</span>')
        cards.append(
            f"""
            <div class="account-card">
              <div class="account-top">
                <div>
                  <h3>{escape(row["name"])}</h3>
                  <div class="meta">{escape(row["owner"])} · {escape(row["safe"])} · {escape(row["platform"])} · {escape(row["reviewGroup"])}</div>
                </div>
                <span class="tag {_verdict_class(row["verdict"])}">{escape(row["verdict"])}</span>
                <div class="score-stack">
                  <div class="micro">Risk score</div>
                  <div class="value">{row["riskScore"]}</div>
                </div>
              </div>
              <div class="account-bottom">
                <div class="two-col">
                  <div class="metric-card">
                    <div class="micro">Review problem</div>
                    <div class="title">{escape(row["topConcern"])}</div>
                    <div class="desc">{escape(row["nextAction"])}</div>
                  </div>
                  <div class="metric-card">
                    <div class="micro">Queue signals</div>
                    <div class="pill-stack">{"".join(flags) or '<span class="signal-pill">Ready</span>'}</div>
                  </div>
                </div>
              </div>
            </div>
            """
        )
    body = f"""
      <section class="page-section">
        <div class="section-head">
          <strong>Review queue</strong>
          <h2>Accounts that should be forced through review first.</h2>
          <p>The queue prioritizes stale, weakly owned, or evidence-thin privileged accounts before they roll into another approval cycle without a clean decision.</p>
        </div>
        <div class="section-body">
          <div class="account-grid">{"".join(cards)}</div>
        </div>
      </section>
    """
    return _shell(
        "Review queue",
        "The privileged accounts most likely to need urgent review, ownership cleanup, or evidence refresh.",
        "queue",
        body,
    )


def render_findings_matrix() -> str:
    rows = "".join(
        f"""
        <tr>
          <td><strong>{escape(item["name"])}</strong><div class="subtext">{escape(item["owner"])} · {escape(item["safe"])}</div></td>
          <td>{item["lastAccessDays"]}d</td>
          <td>{item["reviewAgeDays"]}d</td>
          <td>{item["approvalEvidenceDays"]}d</td>
          <td>{'Yes' if item["hasOpenTicket"] else 'No'}</td>
          <td>{'Yes' if item["managerVerified"] else 'No'}</td>
          <td><span class="tag {_verdict_class(item["verdict"])}">{escape(item["verdict"])}</span></td>
        </tr>
        """
        for item in SERVICE.findings()
    )
    body = f"""
      <section class="page-section">
        <div class="section-head">
          <strong>Findings matrix</strong>
          <h2>The compact evidence table for review operations.</h2>
          <p>This matrix is the fast way to scan stale access, overdue reviews, weak approval evidence, and whether the account has enough ticket and manager state to move forward.</p>
        </div>
        <div class="section-body">
          <div class="table-shell">
            <table>
              <thead>
                <tr>
                  <th>Account</th>
                  <th>Last access</th>
                  <th>Review age</th>
                  <th>Evidence age</th>
                  <th>Open ticket</th>
                  <th>Manager verified</th>
                  <th>Verdict</th>
                </tr>
              </thead>
              <tbody>{rows}</tbody>
            </table>
          </div>
        </div>
      </section>
    """
    return _shell(
        "Findings matrix",
        "Compact view of stale access, evidence age, and approval readiness across privileged accounts.",
        "findings",
        body,
    )


def render_methodology() -> str:
    payload = json.dumps(SERVICE.sample_payload(), indent=2)
    body = f"""
      <section class="page-section">
        <div class="section-head">
          <strong>Methodology</strong>
          <h2>How the sync decides what belongs in the urgent lane.</h2>
          <p>The score is deliberately built from stale access, review age, evidence freshness, rotation age, and ownership quality so the queue feels operational instead of arbitrary.</p>
        </div>
        <div class="section-body">
          <div class="insight-grid">
            <div class="panel">
              <h3>Scoring factors</h3>
              <div class="panel-grid">
                <div class="metric-card">
                  <div class="micro">Access staleness</div>
                  <div class="title">Quiet privileged accounts deserve suspicion, not autopilot.</div>
                  <div class="desc">Accounts that have gone untouched for long enough should be forced back into the review conversation.</div>
                </div>
                <div class="metric-card">
                  <div class="micro">Evidence freshness</div>
                  <div class="title">No evidence means no clean approval story.</div>
                  <div class="desc">Ticket presence, approval evidence age, and manager verification stay close together so operators can tell whether the record is real or just technically present.</div>
                </div>
                <div class="metric-card">
                  <div class="micro">Ownership quality</div>
                  <div class="title">Unassigned or weakly owned access should rise quickly.</div>
                  <div class="desc">A privileged account with unclear ownership is exactly the kind of thing that survives long enough to become institutional debt.</div>
                </div>
              </div>
            </div>
            <div class="panel">
              <div class="code-panel">
                <div class="code-head"><span>/api/sample</span><div class="lights"><i></i><i></i><i></i></div></div>
                <pre><code>{escape(payload)}</code></pre>
              </div>
            </div>
          </div>
        </div>
      </section>
    """
    return _shell(
        "Methodology",
        "How the sync turns account metadata into review priority and approval-readiness signals.",
        "methodology",
        body,
    )


def render_api_summary() -> str:
    payload = json.dumps(SERVICE.sample_payload(), indent=2)
    body = f"""
      <section class="page-section">
        <div class="section-head">
          <strong>API summary</strong>
          <h2>Structured outputs for review systems and audit workflows.</h2>
          <p>The payload is designed to plug into review queues, approval workflows, or governance evidence pipelines without losing the operator-readable explanation layer.</p>
        </div>
        <div class="section-body">
          <div class="insight-grid">
            <div class="panel">
              <h3>Why the payload matters</h3>
              <div class="panel-grid">
                <div class="metric-card">
                  <div class="micro">Review queues</div>
                  <div class="title">Push the stalest, weakest accounts to the top.</div>
                  <div class="desc">Risk score, stale-access flags, and owner gaps make it obvious which items need human attention first.</div>
                </div>
                <div class="metric-card">
                  <div class="micro">Evidence pipelines</div>
                  <div class="title">Keep privileged access defensible.</div>
                  <div class="desc">Approval payloads can move into audit or governance systems without losing the context around why the account still exists.</div>
                </div>
                <div class="metric-card">
                  <div class="micro">Quarterly certification</div>
                  <div class="title">Make the next review cycle cleaner than the last one.</div>
                  <div class="desc">The point is not just finding dirty records. It is making them easier to resolve before the next certification crunch.</div>
                </div>
              </div>
            </div>
            <div class="panel">
              <div class="code-panel">
                <div class="code-head"><span>/api/sample</span><div class="lights"><i></i><i></i><i></i></div></div>
                <pre><code>{escape(payload)}</code></pre>
              </div>
            </div>
          </div>
        </div>
      </section>
    """
    return _shell(
        "API summary",
        "The sync emits structured account-review decisions that can plug into broader access governance workflows.",
        "methodology",
        body,
    )
