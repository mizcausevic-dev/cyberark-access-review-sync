from __future__ import annotations

import sys
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.services.review_sync_service import build_service


OUT_DIR = ROOT / "screenshots"
OUT_DIR.mkdir(exist_ok=True)

WIDTH = 1600
HEIGHT = 980


def shell(title: str, subtitle: str, body: str, active: str) -> str:
    nav = [
        ("OVERVIEW", "overview"),
        ("REVIEW QUEUE", "queue"),
        ("FINDINGS", "findings"),
        ("AUDIT LOG", "audit"),
    ]
    nav_rows = []
    y = 164
    for label, key in nav:
        if key == active:
            nav_rows.append(
                f"<rect x='26' y='{y}' width='208' height='42' rx='14' fill='rgba(116,200,255,0.08)' stroke='rgba(116,200,255,0.16)'/>"
                f"<text x='42' y='{y + 26}' fill='#74c8ff' font-size='12' font-family='Segoe UI' letter-spacing='2'>{label}</text>"
            )
        else:
            nav_rows.append(f"<text x='42' y='{y + 26}' fill='#7f92ae' font-size='12' font-family='Segoe UI' letter-spacing='2'>{label}</text>")
        y += 46
    return f"""<svg xmlns='http://www.w3.org/2000/svg' width='{WIDTH}' height='{HEIGHT}' viewBox='0 0 {WIDTH} {HEIGHT}'>
  <defs>
    <linearGradient id='bg' x1='0' x2='0' y1='0' y2='1'>
      <stop offset='0%' stop-color='#02050a'/>
      <stop offset='100%' stop-color='#07101b'/>
    </linearGradient>
    <linearGradient id='hero' x1='0' x2='1' y1='0' y2='1'>
      <stop offset='0%' stop-color='#09101c'/>
      <stop offset='100%' stop-color='#07101b'/>
    </linearGradient>
    <linearGradient id='blue' x1='0' x2='1' y1='0' y2='0'>
      <stop offset='0%' stop-color='#0f8fbf'/>
      <stop offset='100%' stop-color='#5d78ff'/>
    </linearGradient>
  </defs>
  <rect width='{WIDTH}' height='{HEIGHT}' fill='url(#bg)'/>
  <rect x='0' y='0' width='260' height='{HEIGHT}' fill='rgba(0,0,0,0.32)'/>
  <rect x='22' y='26' width='216' height='64' rx='20' fill='rgba(255,255,255,0.03)' stroke='rgba(255,255,255,0.08)'/>
  <rect x='36' y='38' width='40' height='40' rx='12' fill='url(#blue)'/>
  <text x='56' y='63' text-anchor='middle' fill='#ffffff' font-size='16' font-family='Segoe UI' font-weight='700'>CA</text>
  <text x='90' y='58' fill='#f6f8fe' font-size='15' font-family='Segoe UI' font-weight='700'>CyberArk Access Review Sync</text>
  <text x='90' y='76' fill='#74c8ff' font-size='10' font-family='Segoe UI' letter-spacing='3'>INSTANCE: VAULT-REVIEW</text>
  <text x='36' y='142' fill='#74c8ff' font-size='11' font-family='Segoe UI' letter-spacing='4'>ACTIVE VIEWS</text>
  {''.join(nav_rows)}
  <rect x='260' y='0' width='{WIDTH - 260}' height='72' fill='rgba(0,0,0,0.34)'/>
  <rect x='260' y='72' width='{WIDTH - 260}' height='1' fill='rgba(255,255,255,0.08)'/>
  <rect x='294' y='20' width='220' height='30' rx='15' fill='rgba(116,200,255,0.05)' stroke='rgba(116,200,255,0.14)'/>
  <circle cx='314' cy='35' r='5' fill='#74c8ff'/>
  <text x='330' y='39' fill='#b9e1ff' font-size='10' font-family='Segoe UI' letter-spacing='3'>VAULT REVIEW FEED LIVE</text>
  <rect x='1290' y='16' width='250' height='38' rx='19' fill='url(#blue)'/>
  <text x='1415' y='39' fill='#ffffff' text-anchor='middle' font-size='10' font-family='Segoe UI' font-weight='700' letter-spacing='3'>OPEN API DOCS</text>
  <rect x='294' y='104' width='1240' height='248' rx='28' fill='url(#hero)' stroke='rgba(120,163,214,0.18)'/>
  <text x='332' y='146' fill='#74c8ff' font-size='11' font-family='Segoe UI' letter-spacing='5'>CYBERARK ACCESS REVIEW SYNC</text>
  <text x='332' y='212' fill='#f6f8fe' font-size='44' font-family='Georgia' font-weight='700'>{escape(title)}</text>
  <text x='332' y='248' fill='#96a9c6' font-size='21' font-family='Segoe UI'>{escape(subtitle)}</text>
  {body}
</svg>"""


def stat_card(x: int, y: int, label: str, value: str, sub: str) -> str:
    return f"""
  <rect x='{x}' y='{y}' width='280' height='132' rx='20' fill='rgba(255,255,255,0.04)' stroke='rgba(255,255,255,0.06)'/>
  <text x='{x + 22}' y='{y + 28}' fill='#71839d' font-size='10' font-family='Segoe UI' letter-spacing='3'>{escape(label.upper())}</text>
  <text x='{x + 22}' y='{y + 72}' fill='#f6f8fe' font-size='38' font-family='Segoe UI' font-weight='700'>{escape(value)}</text>
  <text x='{x + 22}' y='{y + 102}' fill='#96a9c6' font-size='14' font-family='Segoe UI'>{escape(sub)}</text>
    """


def overview_svg() -> str:
    service = build_service()
    summary = service.summary()
    catalog = service.account_catalog()
    velocity = service.sync_velocity()
    max_reviews = max(item["reviews"] for item in velocity)
    chart = []
    x = 376
    for item in velocity:
        height = max(20, round((item["reviews"] / max_reviews) * 108))
        top = 704 - height
        chart.append(
            f"""
  <rect x='{x}' y='{top}' width='70' height='{height}' rx='16' fill='url(#blue)' opacity='0.92'/>
  <text x='{x + 35}' y='730' text-anchor='middle' fill='#f6f8fe' font-size='14' font-family='Segoe UI' font-weight='700'>{item["reviews"]}</text>
  <text x='{x + 35}' y='752' text-anchor='middle' fill='#96a9c6' font-size='10' font-family='Segoe UI' letter-spacing='2'>{item["day"].upper()}</text>
            """
        )
        x += 88
    body = [
        stat_card(332, 274, "Privileged accounts", str(summary["accountCount"]), "Accounts currently modeled for review sync."),
        stat_card(628, 274, "Urgent review lanes", str(summary["criticalCount"]), "Accounts that should be forced through review now."),
        stat_card(924, 274, "Review-ready", str(summary["reviewReadyCount"]), "Accounts with enough evidence to move cleanly."),
        stat_card(1220, 274, "Owner gaps", str(summary["orphanedOwnerCount"]), "Weakly owned or unassigned records."),
        f"""
  <rect x='332' y='380' width='1240' height='94' rx='20' fill='rgba(2,8,17,0.62)' stroke='rgba(255,255,255,0.06)'/>
  <text x='356' y='410' fill='#f6c46a' font-size='10' font-family='Segoe UI' letter-spacing='3'>LEAD RECOMMENDATION</text>
  <text x='356' y='446' fill='#dce7fb' font-size='18' font-family='Segoe UI'>{escape(summary['leadRecommendation'])}</text>
  <rect x='332' y='500' width='604' height='356' rx='22' fill='rgba(4,9,18,0.55)' stroke='rgba(255,255,255,0.06)'/>
  <text x='356' y='534' fill='#74c8ff' font-size='10' font-family='Segoe UI' letter-spacing='3'>SYNC VELOCITY</text>
  <text x='356' y='566' fill='#f6f8fe' font-size='20' font-family='Georgia' font-weight='700'>How much review motion the lane is carrying this week.</text>
  {''.join(chart)}
  <text x='356' y='816' fill='#96a9c6' font-size='12' font-family='Segoe UI'>Average evidence age: {summary['averageApprovalEvidenceAge']} days</text>
  <text x='356' y='838' fill='#96a9c6' font-size='12' font-family='Segoe UI'>Queue pressure: {summary['criticalCount']} critical / {summary['watchCount']} watch</text>
  <rect x='960' y='500' width='612' height='356' rx='22' fill='rgba(4,9,18,0.55)' stroke='rgba(255,255,255,0.06)'/>
  <text x='984' y='534' fill='#74c8ff' font-size='10' font-family='Segoe UI' letter-spacing='3'>TOP REVIEW BOARD</text>
  <text x='984' y='566' fill='#f6f8fe' font-size='20' font-family='Georgia' font-weight='700'>The accounts that deserve attention first.</text>
        """,
    ]
    y = 604
    for row in catalog[:2]:
        verdict_fill = {"healthy": "#49d79e", "watch": "#f6c46a", "critical": "#ff7987"}[row["verdict"]]
        body.append(
            f"""
  <rect x='984' y='{y}' width='564' height='104' rx='18' fill='rgba(255,255,255,0.03)' stroke='rgba(255,255,255,0.05)'/>
  <text x='1010' y='{y + 30}' fill='#f6f8fe' font-size='20' font-family='Segoe UI' font-weight='700'>{escape(row["name"])}</text>
  <text x='1010' y='{y + 52}' fill='#96a9c6' font-size='12' font-family='Segoe UI'>{escape(row["owner"])} · {escape(row["safe"])} · {escape(row["platform"])}</text>
  <text x='1010' y='{y + 74}' fill='#cfe0f7' font-size='12' font-family='Segoe UI'>{escape(row["topConcern"])}</text>
  <text x='1496' y='{y + 30}' text-anchor='end' fill='{verdict_fill}' font-size='10' font-family='Segoe UI' font-weight='700' letter-spacing='2'>{escape(row["verdict"].upper())}</text>
  <text x='1496' y='{y + 68}' text-anchor='end' fill='#f6f8fe' font-size='28' font-family='Segoe UI' font-weight='700'>{row["riskScore"]}</text>
            """
        )
        y += 122
    return shell(
        "Control-plane summary for privileged-review posture.",
        "Server count, critical lanes, sync throughput, and operator recommendations at a glance.",
        "".join(body),
        "overview",
    )


def queue_svg() -> str:
    queue = build_service().review_queue()
    body = [
        """
  <rect x='332' y='392' width='1240' height='496' rx='24' fill='rgba(10,18,33,0.88)' stroke='rgba(120,163,214,0.16)'/>
  <text x='356' y='426' fill='#74c8ff' font-size='10' font-family='Segoe UI' letter-spacing='3'>REVIEW QUEUE</text>
  <text x='356' y='462' fill='#f6f8fe' font-size='24' font-family='Georgia' font-weight='700'>The servers most likely to need containment or human review first.</text>
  <text x='356' y='492' fill='#96a9c6' font-size='15' font-family='Segoe UI'>Stale, weakly owned, or evidence-thin privileged accounts rise here.</text>
        """
    ]
    y = 530
    for row in queue[:3]:
        body.append(
            f"""
  <rect x='356' y='{y}' width='1192' height='104' rx='18' fill='rgba(4,9,18,0.58)' stroke='rgba(255,255,255,0.05)'/>
  <text x='384' y='{y + 32}' fill='#f6f8fe' font-size='22' font-family='Segoe UI' font-weight='700'>{escape(row["name"])}</text>
  <text x='384' y='{y + 54}' fill='#96a9c6' font-size='12' font-family='Segoe UI'>{escape(row["owner"])} · {escape(row["safe"])} · {escape(row["reviewGroup"])}</text>
  <text x='384' y='{y + 82}' fill='#cfe0f7' font-size='12' font-family='Segoe UI'>{escape(row["topConcern"])}</text>
  <text x='1332' y='{y + 30}' fill='#6f83a0' font-size='10' font-family='Segoe UI' letter-spacing='2'>RISK SCORE</text>
  <text x='1514' y='{y + 36}' text-anchor='end' fill='#f6f8fe' font-size='28' font-family='Segoe UI' font-weight='700'>{row["riskScore"]}</text>
            """
        )
        y += 122
    return shell(
        "Review queue for destructive-access exposure.",
        "The servers most likely to need containment or human review first.",
        "".join(body),
        "queue",
    )


def findings_svg() -> str:
    rows = []
    y = 548
    for item in build_service().findings()[:4]:
        verdict_fill = {"healthy": "#49d79e", "watch": "#f6c46a", "critical": "#ff7987"}[item["verdict"]]
        rows.append(
            f"""
  <rect x='356' y='{y}' width='1192' height='112' rx='18' fill='rgba(255,255,255,0.03)' stroke='rgba(255,255,255,0.05)'/>
  <text x='382' y='{y + 30}' fill='#f6f8fe' font-size='20' font-family='Segoe UI' font-weight='700'>{escape(item["name"])}</text>
  <text x='382' y='{y + 52}' fill='#96a9c6' font-size='12' font-family='Segoe UI'>{escape(item["owner"])} · {escape(item["safe"])} · {escape(item["privilegeTier"])}</text>
  <text x='382' y='{y + 78}' fill='#cfe0f7' font-size='12' font-family='Segoe UI'>Last access {item["lastAccessDays"]}d · review age {item["reviewAgeDays"]}d · evidence age {item["approvalEvidenceDays"]}d</text>
  <text x='1496' y='{y + 34}' text-anchor='end' fill='{verdict_fill}' font-size='10' font-family='Segoe UI' font-weight='700' letter-spacing='2'>{escape(item["verdict"].upper())}</text>
  <text x='1496' y='{y + 78}' text-anchor='end' fill='#f6f8fe' font-size='14' font-family='Segoe UI'>Ticket: {'Yes' if item["hasOpenTicket"] else 'No'} · Manager: {'Yes' if item["managerVerified"] else 'No'}</text>
            """
        )
        y += 130
    body = f"""
  <rect x='332' y='392' width='1240' height='496' rx='24' fill='rgba(10,18,33,0.88)' stroke='rgba(120,163,214,0.16)'/>
  <text x='356' y='426' fill='#74c8ff' font-size='10' font-family='Segoe UI' letter-spacing='3'>FINDINGS MATRIX</text>
  <text x='356' y='462' fill='#f6f8fe' font-size='24' font-family='Georgia' font-weight='700'>The records most likely to break certification quality if they stay invisible.</text>
  <text x='356' y='492' fill='#96a9c6' font-size='15' font-family='Segoe UI'>Stale access, manager gaps, and evidence weakness stay together on the same review surface.</text>
  {''.join(rows)}
    """
    return shell(
        "Findings matrix for stale-access and evidence pressure.",
        "The records most likely to break certification quality if they stay invisible.",
        body,
        "findings",
    )


def audit_svg() -> str:
    logs = build_service().audit_log()
    rows = []
    y = 548
    for item in logs[:4]:
        result = "#49d79e" if item["result"] == "Success" else "#ff7987"
        rows.append(
            f"""
  <rect x='356' y='{y}' width='1192' height='74' rx='14' fill='rgba(255,255,255,0.03)' stroke='rgba(255,255,255,0.05)'/>
  <text x='382' y='{y + 28}' fill='#6f83a0' font-size='11' font-family='Courier New'>{escape(item["timestamp"])}</text>
  <text x='552' y='{y + 28}' fill='#74c8ff' font-size='11' font-family='Courier New' font-weight='700'>{escape(item["action"])}</text>
  <text x='778' y='{y + 28}' fill='#f6f8fe' font-size='12' font-family='Segoe UI' font-weight='700'>{escape(item["resource"])}</text>
  <text x='778' y='{y + 48}' fill='#96a9c6' font-size='12' font-family='Segoe UI'>{escape(item["detail"])}</text>
  <text x='1496' y='{y + 34}' text-anchor='end' fill='{result}' font-size='12' font-family='Segoe UI' font-weight='700'>{escape(item["result"].upper())}</text>
            """
        )
        y += 92
    body = f"""
  <rect x='332' y='392' width='1240' height='496' rx='24' fill='rgba(10,18,33,0.88)' stroke='rgba(120,163,214,0.16)'/>
  <text x='356' y='426' fill='#74c8ff' font-size='10' font-family='Segoe UI' letter-spacing='3'>AUDIT EVIDENCE</text>
  <text x='356' y='462' fill='#f6f8fe' font-size='24' font-family='Georgia' font-weight='700'>A replayable log of sync actions, queue promotions, and evidence gaps.</text>
  <text x='356' y='492' fill='#96a9c6' font-size='15' font-family='Segoe UI'>The useful part is not just emitting events. It is making them legible to reviewers and auditors.</text>
  {''.join(rows)}
    """
    return shell(
        "Audit evidence for privileged-review synchronization.",
        "A replayable log of sync actions, queue promotions, evidence gaps, and review outcomes.",
        body,
        "audit",
    )


def main() -> None:
    (OUT_DIR / "01-overview.svg").write_text(overview_svg(), encoding="utf-8")
    (OUT_DIR / "02-review-queue.svg").write_text(queue_svg(), encoding="utf-8")
    (OUT_DIR / "03-findings-matrix.svg").write_text(findings_svg(), encoding="utf-8")
    (OUT_DIR / "04-audit-log.svg").write_text(audit_svg(), encoding="utf-8")
    print("rendered screenshots")


if __name__ == "__main__":
    main()
