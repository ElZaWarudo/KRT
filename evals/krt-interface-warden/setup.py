#!/usr/bin/env python3
"""Build one interface-warden eval fixture: a tiny static frontend in repo/."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

CARD_CSS = """\
* { box-sizing: border-box; }
body { margin: 0; font-family: Inter, system-ui, sans-serif; background: #f4f6fb; color: #1f2937; }
.layout { display: grid; grid-template-columns: 240px 1fr; min-height: 100vh; }
.sidebar { background: #111827; color: #e5e7eb; padding: 24px; }
.sidebar a { display: block; color: inherit; padding: 8px 0; text-decoration: none; }
main { padding: 32px; }
.hero { background: linear-gradient(135deg, #6366f1, #ec4899); color: white; border-radius: 20px; padding: 32px; margin-bottom: 24px; }
.grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 24px; margin-bottom: 24px; }
.card { background: white; border: 1px solid #e5e7eb; border-radius: 16px; box-shadow: 0 10px 25px rgba(0,0,0,.08); padding: 24px; }
.card .icon { width: 40px; height: 40px; border-radius: 12px; background: #eef2ff; display: grid; place-items: center; }
.card h3 { font-size: 14px; font-weight: 600; color: #6b7280; margin: 12px 0 4px; }
.card .value { font-size: 28px; font-weight: 600; }
.card .delta { font-size: 12px; color: #10b981; }
.badge { padding: 2px 10px; border-radius: 999px; font-size: 12px; background: #e0e7ff; }
table { width: 100%; border-collapse: collapse; }
td, th { text-align: left; padding: 12px; border-bottom: 1px solid #f1f5f9; }
"""

RETURNS_HTML = """\
<!doctype html>
<html lang="en">
<head><meta charset="utf-8"><title>Returns</title><link rel="stylesheet" href="styles.css"></head>
<body>
<div class="layout">
  <nav class="sidebar"><strong>ReturnDesk</strong>
    <a href="#">Dashboard</a><a href="#">Returns</a><a href="#">Inspections</a><a href="#">Refunds</a><a href="#">Settings</a>
  </nav>
  <main>
    <section class="hero"><h1>Welcome back, Sarah 👋</h1><p>Here's what's happening at the Leeds returns warehouse today.</p></section>
    <div class="grid">
      <div class="card"><div class="icon">📦</div><h3>Returns received today</h3><div class="value">184</div><div class="delta">+12%</div></div>
      <div class="card"><div class="icon">⏳</div><h3>Awaiting inspection</h3><div class="value">63</div><div class="delta">+4%</div></div>
      <div class="card"><div class="icon">💷</div><h3>Refunds issued</h3><div class="value">£8,420</div><div class="delta">+2%</div></div>
      <div class="card"><div class="icon">⚠️</div><h3>Over 48h SLA</h3><div class="value">17</div><div class="delta">+9%</div></div>
    </div>
    <div class="grid" style="grid-template-columns: 2fr 1fr;">
      <div class="card">
        <h2>Recent returns</h2>
        <table>
          <tr><th>RMA</th><th>Item</th><th>Reason</th><th>Status</th></tr>
          <tr><td>RMA-4102</td><td>Trail running shoe, 42</td><td>Too small</td><td><span class="badge">Awaiting inspection</span></td></tr>
          <tr><td>RMA-4101</td><td>Down jacket, M</td><td>Damaged seam</td><td><span class="badge">Over SLA</span></td></tr>
          <tr><td>RMA-4099</td><td>Headlamp</td><td>Not as described</td><td><span class="badge">Refunded</span></td></tr>
          <tr><td>RMA-4098</td><td>Tent footprint</td><td>Changed mind</td><td><span class="badge">Restocked</span></td></tr>
        </table>
      </div>
      <div class="card">
        <h2>Quick actions</h2>
        <div class="card"><div class="icon">🔍</div><h3>Start inspection</h3></div>
        <div class="card"><div class="icon">🧾</div><h3>Issue refund</h3></div>
        <div class="card"><div class="icon">📊</div><h3>Export report</h3></div>
      </div>
    </div>
  </main>
</div>
</body>
</html>
"""

INVOICES_HTML = """\
<!doctype html>
<html lang="en">
<head><meta charset="utf-8"><title>Invoices</title><link rel="stylesheet" href="styles.css"></head>
<body>
<div class="layout">
  <nav class="sidebar"><strong>Ledgerly</strong><a href="#">Invoices</a><a href="#">Payments</a><a href="#">Clients</a></nav>
  <main>
    <div class="card">
      <h1>Accounts receivable</h1>
      <div class="grid" style="grid-template-columns: repeat(3, 1fr);">
        <div class="card"><div class="icon">💰</div><h3>Outstanding</h3><div class="value">€184,300</div></div>
        <div class="card"><div class="icon">⏰</div><h3>Overdue</h3><div class="value">€41,950</div></div>
        <div class="card"><div class="icon">✅</div><h3>Paid this month</h3><div class="value">€96,120</div></div>
      </div>
      <div class="card">
        <div class="card"><label>Client <input placeholder="Search client"></label> <label>Status <select><option>All</option><option>Overdue</option></select></label></div>
        <button>Reconcile selected</button>
        <table>
          <tr><th></th><th>Invoice</th><th>Client</th><th>Issued</th><th>Due</th><th>Amount</th><th>Matched payment</th><th>Status</th></tr>
          <tr><td><input type="checkbox"></td><td>INV-2291</td><td>Nordhaus GmbH</td><td>02 Sep</td><td>02 Oct</td><td>€12,400.00</td><td>BANK-77812</td><td><span class="badge">Overdue</span></td></tr>
          <tr><td><input type="checkbox"></td><td>INV-2290</td><td>Lumen Labs</td><td>01 Sep</td><td>01 Oct</td><td>€3,180.50</td><td>—</td><td><span class="badge">Overdue</span></td></tr>
          <tr><td><input type="checkbox"></td><td>INV-2288</td><td>Casa Verde SL</td><td>28 Aug</td><td>27 Sep</td><td>€22,000.00</td><td>BANK-77790</td><td><span class="badge">Paid</span></td></tr>
          <tr><td><input type="checkbox"></td><td>INV-2287</td><td>Brightwater Ltd</td><td>25 Aug</td><td>24 Oct</td><td>€7,560.00</td><td>—</td><td><span class="badge">Open</span></td></tr>
          <tr><td><input type="checkbox"></td><td>INV-2285</td><td>Nordhaus GmbH</td><td>20 Aug</td><td>19 Oct</td><td>€1,240.00</td><td>BANK-77701</td><td><span class="badge">Partially paid</span></td></tr>
        </table>
      </div>
    </div>
  </main>
</div>
</body>
</html>
"""

CLAIM = {
    "claim": "CLM-88213", "policy": "HOME-55-10294", "type": "Water damage (escape of water)",
    "claimant": {"name": "Priya Raman", "phone": "+44 7700 900412", "address": "14 Alder Row, Bristol BS6 5QT"},
    "reported": "2026-10-03", "incident": "2026-10-01",
    "amount_claimed": 14250.0, "policy_limit": 50000.0, "excess": 500.0,
    "fraud_score": 0.12, "status": "Awaiting adjuster decision",
    "recommendation": {"by": "Loss adjuster T. Okafor", "action": "Approve with deduction", "amount": 11900.0,
                       "reason": "Kitchen units pre-existing wear; flooring and plaster covered in full."},
    "line_items": [
        {"item": "Kitchen flooring replacement", "claimed": 5200.0, "assessed": 5200.0},
        {"item": "Plaster and redecoration", "claimed": 3800.0, "assessed": 3800.0},
        {"item": "Kitchen base units", "claimed": 4100.0, "assessed": 1750.0},
        {"item": "Dehumidifier hire", "claimed": 1150.0, "assessed": 1150.0},
    ],
    "history": [
        {"at": "2026-10-03 09:12", "who": "Priya Raman", "event": "Claim reported online"},
        {"at": "2026-10-03 11:40", "who": "System", "event": "Policy cover verified"},
        {"at": "2026-10-06 14:05", "who": "T. Okafor", "event": "Site visit completed, 23 photos uploaded"},
        {"at": "2026-10-09 10:30", "who": "T. Okafor", "event": "Recommendation submitted"},
    ],
    "documents": ["Plumber invoice.pdf", "Site photos (23)", "Kitchen fitter quote.pdf"],
}


def git(cwd: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True)


def setup(case: str, root: Path) -> None:
    subprocess.run(["git", "init", "-q", "--bare", "-b", "main", str(root / "origin.git")], check=True)
    subprocess.run(["git", "clone", "-q", str(root / "origin.git"), str(root / "repo")], check=True, capture_output=True)
    repo = root / "repo"
    git(repo, "config", "user.name", "Eval Dev")
    git(repo, "config", "user.email", "dev@example.com")
    (repo / "styles.css").write_text(CARD_CSS)
    if case in ("redesign-returns", "critique-returns"):
        (repo / "index.html").write_text(RETURNS_HTML)
    elif case == "audit-invoices":
        (repo / "index.html").write_text(INVOICES_HTML)
    elif case == "build-claim":
        (repo / "styles.css").unlink()
        (repo / "claim.json").write_text(json.dumps(CLAIM, indent=2))
    else:
        raise SystemExit(f"unknown case {case}")
    git(repo, "add", "-A")
    git(repo, "commit", "-qm", "chore: init")
    git(repo, "push", "-q", "origin", "main")


if __name__ == "__main__":
    setup(sys.argv[1], Path(sys.argv[2]))
