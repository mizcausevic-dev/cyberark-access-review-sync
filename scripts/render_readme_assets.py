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


def shell(title: str, subtitle: str, body: str) -> str:
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
  <rect x='26' y='164' width='208' height='42' rx='14' fill='rgba(116,200,255,0.08)' stroke='rgba(116,200,255,0.16)'/>
  <text x='42' y='190' fill='#74c8ff' font-size='12' font-family='Segoe UI' letter-spacing='2'>OVERVIEW</text>
  <text x='42' y='236' fill='#7f92ae' font-size='12' font-family='Segoe UI' letter-spacing='2'>REVIEW QUEUE</text>
  <text x='42' y='282' fill='#7f92ae' font-size='12' font-family='Segoe UI' letter-spacing='2'>FINDINGS</text>
  <text x='42' y='328' fill='#7f92ae' font-size='12' font-family='Segoe UI' letter-spacing='2'>METHODOLOGY</text>
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
    body = [
        stat_card(332, 274, "Privileged accounts", str(summary["accountCount"]), "Accounts currently modeled for review sync."),
        stat_card(628, 274, "Urgent review lanes", str(summary["criticalCount"]), "Accounts that should be forced through review now."),
        stat_card(924, 274, "Review-ready", str(summary["reviewReadyCount"]), "Accounts with enough evidence to move cleanly."),
        stat_card(1220, 274, "Owner gaps", str(summary["orphanedOwnerCount"]), "Weakly owned or unassigned records."),
        f"""
  <rect x='332' y='380' width='1240' height='94' rx='20' fill='rgba(2,8,17,0.62)' stroke='rgba(255,255,255,0.06)'/>
  <text x='356' y='410' fill='#f6c46a' font-size='10' font-family='Segoe UI' letter-spacing='3'>LEAD RECOMMENDATION</text>
  <text x='356' y='446' fill='#dce7fb' font-size='18' font-family='Segoe UI'>{escape(summary['leadRecommendation'])}</text>
  <rect x='332' y='500' width='1240' height='388' rx='22' fill='rgba(4,9,18,0.55)' stroke='rgba(255,255,255,0.06)'/>
  <text x='356' y='534' fill='#f6f8fe' font-size='20' font-family='Segoe UI' font-weight='700'>Top review board</text>
        """,
    ]
    y = 568
    for row in catalog[:3]:
        verdict_fill = {"healthy": "#49d79e", "watch": "#f6c46a", "critical": "#ff7987"}[row["verdict"]]
        body.append(
            f"""
  <rect x='356' y='{y}' width='1192' height='86' rx='18' fill='rgba(255,255,255,0.03)' stroke='rgba(255,255,255,0.05)'/>
  <text x='382' y='{y + 30}' fill='#f6f8fe' font-size='20' font-family='Segoe UI' font-weight='700'>{escape(row["name"])}</text>
  <text x='382' y='{y + 52}' fill='#96a9c6' font-size='12' font-family='Segoe UI'>{escape(row["owner"])} · {escape(row["safe"])} · {escape(row["platform"])}</text>
  <text x='382' y='{y + 72}' fill='#cfe0f7' font-size='12' font-family='Segoe UI'>{row["lastAccessDays"]}d since use · {row["reviewAgeDays"]}d review age · evidence {row["approvalEvidenceDays"]}d</text>
  <rect x='1210' y='{y + 18}' width='96' height='28' rx='14' fill='rgba(255,255,255,0.04)' stroke='rgba(255,255,255,0.06)'/>
  <text x='1258' y='{y + 37}' text-anchor='middle' fill='{verdict_fill}' font-size='10' font-family='Segoe UI' font-weight='700' letter-spacing='2'>{escape(row["verdict"].upper())}</text>
  <text x='1398' y='{y + 30}' fill='#6f83a0' font-size='10' font-family='Segoe UI' letter-spacing='2'>RISK</text>
  <text x='1514' y='{y + 36}' text-anchor='end' fill='#f6f8fe' font-size='28' font-family='Segoe UI' font-weight='700'>{row["riskScore"]}</text>
            """
        )
        y += 102
    return shell("Review sync overview", "Syncing CyberArk privileged-account metadata into access-review queues, stale-access findings, and approval-ready evidence payloads.", "".join(body))


def queue_svg() -> str:
    queue = build_service().review_queue()
    body = [
        """
  <rect x='332' y='392' width='1240' height='496' rx='24' fill='rgba(10,18,33,0.88)' stroke='rgba(120,163,214,0.16)'/>
  <text x='356' y='426' fill='#74c8ff' font-size='10' font-family='Segoe UI' letter-spacing='3'>REVIEW QUEUE</text>
  <text x='356' y='462' fill='#f6f8fe' font-size='24' font-family='Georgia' font-weight='700'>Accounts that should be forced through review first.</text>
  <text x='356' y='492' fill='#96a9c6' font-size='15' font-family='Segoe UI'>Stale, weakly owned, or evidence-thin privileged accounts rise here.</text>
        """
    ]
    y = 530
    for row in queue:
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
    return shell("Review queue", "The privileged accounts most likely to need urgent review, ownership cleanup, or evidence refresh.", "".join(body))


def findings_svg() -> str:
    rows = []
    y = 560
    for item in build_service().findings()[:6]:
        verdict_fill = {"healthy": "#49d79e", "watch": "#f6c46a", "critical": "#ff7987"}[item["verdict"]]
        rows.append(
            f"""
  <rect x='356' y='{y}' width='1192' height='54' fill='{"rgba(255,255,255,0.02)" if (y // 54) % 2 else "rgba(0,0,0,0.06)"}'/>
  <text x='382' y='{y + 22}' fill='#f6f8fe' font-size='14' font-family='Segoe UI' font-weight='700'>{escape(item["name"])}</text>
  <text x='382' y='{y + 40}' fill='#96a9c6' font-size='11' font-family='Segoe UI'>{escape(item["owner"])}</text>
  <text x='842' y='{y + 32}' fill='#f6f8fe' font-size='12' font-family='Segoe UI'>{item["lastAccessDays"]}d</text>
  <text x='972' y='{y + 32}' fill='#f6f8fe' font-size='12' font-family='Segoe UI'>{item["reviewAgeDays"]}d</text>
  <text x='1108' y='{y + 32}' fill='#f6f8fe' font-size='12' font-family='Segoe UI'>{item["approvalEvidenceDays"]}d</text>
  <text x='1266' y='{y + 32}' fill='#f6f8fe' font-size='12' font-family='Segoe UI'>{'Yes' if item["hasOpenTicket"] else 'No'}</text>
  <text x='1408' y='{y + 32}' fill='{verdict_fill}' font-size='10' font-family='Segoe UI' font-weight='700' letter-spacing='2'>{escape(item["verdict"].upper())}</text>
            """
        )
        y += 54
    body = f"""
  <rect x='332' y='392' width='1240' height='496' rx='24' fill='rgba(10,18,33,0.88)' stroke='rgba(120,163,214,0.16)'/>
  <text x='356' y='426' fill='#74c8ff' font-size='10' font-family='Segoe UI' letter-spacing='3'>FINDINGS MATRIX</text>
  <text x='356' y='462' fill='#f6f8fe' font-size='24' font-family='Georgia' font-weight='700'>The compact evidence table for review operations.</text>
  <text x='356' y='492' fill='#96a9c6' font-size='15' font-family='Segoe UI'>Fastest way to scan stale access, overdue reviews, and whether the record is still approvable.</text>
  <rect x='356' y='520' width='1192' height='46' fill='rgba(255,255,255,0.04)'/>
  <text x='382' y='548' fill='#7385a0' font-size='10' font-family='Segoe UI' font-weight='700' letter-spacing='3'>ACCOUNT</text>
  <text x='828' y='548' fill='#7385a0' font-size='10' font-family='Segoe UI' font-weight='700' letter-spacing='3'>LAST ACCESS</text>
  <text x='954' y='548' fill='#7385a0' font-size='10' font-family='Segoe UI' font-weight='700' letter-spacing='3'>REVIEW AGE</text>
  <text x='1088' y='548' fill='#7385a0' font-size='10' font-family='Segoe UI' font-weight='700' letter-spacing='3'>EVIDENCE AGE</text>
  <text x='1246' y='548' fill='#7385a0' font-size='10' font-family='Segoe UI' font-weight='700' letter-spacing='3'>TICKET</text>
  <text x='1386' y='548' fill='#7385a0' font-size='10' font-family='Segoe UI' font-weight='700' letter-spacing='3'>VERDICT</text>
  {"".join(rows)}
    """
    return shell("Findings matrix", "Compact view of stale access, evidence age, and approval readiness across privileged accounts.", body)


def methodology_svg() -> str:
    body = """
  <rect x='332' y='392' width='1240' height='496' rx='24' fill='rgba(10,18,33,0.88)' stroke='rgba(120,163,214,0.16)'/>
  <text x='356' y='426' fill='#74c8ff' font-size='10' font-family='Segoe UI' letter-spacing='3'>METHODOLOGY</text>
  <text x='356' y='462' fill='#f6f8fe' font-size='24' font-family='Georgia' font-weight='700'>How the sync decides what belongs in the urgent lane.</text>
  <text x='356' y='492' fill='#96a9c6' font-size='15' font-family='Segoe UI'>Stale access, weak ownership, and approval evidence all stay in one score.</text>
  <rect x='356' y='526' width='520' height='104' rx='18' fill='rgba(255,255,255,0.03)' stroke='rgba(255,255,255,0.05)'/>
  <text x='382' y='554' fill='#74c8ff' font-size='10' font-family='Segoe UI' letter-spacing='3'>ACCESS STALENESS</text>
  <text x='382' y='586' fill='#f6f8fe' font-size='16' font-family='Segoe UI' font-weight='700'>Quiet privileged accounts deserve suspicion, not autopilot.</text>
  <text x='382' y='614' fill='#96a9c6' font-size='13' font-family='Segoe UI'>Long-unused accounts should be forced back into the review conversation.</text>
  <rect x='356' y='646' width='520' height='104' rx='18' fill='rgba(255,255,255,0.03)' stroke='rgba(255,255,255,0.05)'/>
  <text x='382' y='674' fill='#74c8ff' font-size='10' font-family='Segoe UI' letter-spacing='3'>OWNERSHIP QUALITY</text>
  <text x='382' y='706' fill='#f6f8fe' font-size='16' font-family='Segoe UI' font-weight='700'>Weakly owned privilege should rise quickly.</text>
  <text x='382' y='734' fill='#96a9c6' font-size='13' font-family='Segoe UI'>Unassigned or manager-unverified accounts become institutional debt fast.</text>
  <rect x='900' y='526' width='648' height='256' rx='22' fill='rgba(2,6,12,0.92)' stroke='rgba(255,255,255,0.08)'/>
  <text x='928' y='556' fill='#74c8ff' font-size='10' font-family='Segoe UI' letter-spacing='3'>REVIEW SYNC ENGINE</text>
  <text x='928' y='598' fill='#dce8fb' font-size='13' font-family='Courier New'>if last_access_days &gt; 120: risk += 18</text>
  <text x='928' y='626' fill='#dce8fb' font-size='13' font-family='Courier New'>if approval_evidence_days == 0: risk += 16</text>
  <text x='928' y='654' fill='#dce8fb' font-size='13' font-family='Courier New'>if owner == \"Unassigned\": risk += 14</text>
  <text x='928' y='682' fill='#dce8fb' font-size='13' font-family='Courier New'>if dual_approval and not ticket: risk += 10</text>
  <text x='928' y='752' fill='#96a9c6' font-size='12' font-family='Segoe UI'>Operator-first. Audit-legible. Integration-friendly.</text>
    """
    return shell("How the sync decides what belongs in the urgent lane.", "Stale access, weak ownership, and approval evidence all stay in one score.", body)


def main() -> None:
    (OUT_DIR / "01-overview.svg").write_text(overview_svg(), encoding="utf-8")
    (OUT_DIR / "02-review-queue.svg").write_text(queue_svg(), encoding="utf-8")
    (OUT_DIR / "03-findings-matrix.svg").write_text(findings_svg(), encoding="utf-8")
    (OUT_DIR / "04-methodology.svg").write_text(methodology_svg(), encoding="utf-8")
    print("rendered screenshots")


if __name__ == "__main__":
    main()
