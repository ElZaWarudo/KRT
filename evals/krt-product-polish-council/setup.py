#!/usr/bin/env python3
"""Build a tiny expense-claims web app with deliberate polish and workload problems.

Planted problems (do not fix them here; the evals grade whether agents find them):
- Submit: no acknowledgement or pending state, no double-submit guard, 1.5 s fake
  latency, success shown only as a toast that vanishes after 900 ms.
- Failure: every third submit fails; the form is wiped and a generic "Error" banner
  appears at the top of the page, far from the form.
- Delete: removes the claim instantly with no confirmation, undo, or pending state.
- Motion: `transition: all 600ms` with a bouncy cubic-bezier, modal shown with
  display toggling, no focus management, Escape does nothing, no reduced-motion rule.
- Wizard: no step indicator; step 2 needs the cost-centre code that is shown only on
  step 1; step 3 asks the user to confirm the amount without showing it; "Continue"
  and "Proceed" buttons sit side by side with different meanings; Back resets fields.
- Step 1 legitimately has nine fields that finance requires (README says so).
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

README = """# Claims

Internal expense-claims tool for a 40-person consultancy.

- Primary user: consultants filing travel expenses, usually once or twice a month,
  often on a phone between client meetings.
- Primary job: file a claim correctly the first time so finance does not bounce it.
- Success signal: the claim appears in "My claims" with status Submitted.
- Finance requires every field on step 1 (policy FIN-7); they must stay.
- Claims are money: a submitted or deleted claim affects reimbursement.

Open `index.html` in a browser. `api.js` fakes the server.
"""

API_JS = """// Fake server: 1.5 s latency, every third submit fails.
let calls = 0;
export function submitClaim(claim) {
  calls += 1;
  return new Promise((resolve, reject) => {
    setTimeout(() => (calls % 3 === 0 ? reject(new Error('500')) : resolve({ id: Date.now(), ...claim })), 1500);
  });
}
export function deleteClaim(id) {
  return new Promise((resolve) => setTimeout(() => resolve(id), 800));
}
"""

INDEX_HTML = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Claims</title>
<link rel="stylesheet" href="styles.css">
</head>
<body>
<div id="error" class="banner" hidden>Error</div>
<header><h1>Claims</h1><button id="new">New claim</button></header>
<main>
  <h2>My claims</h2>
  <ul id="claims"><li data-id="1">Train Madrid–Valencia · 64.20 EUR · Submitted <button class="del">×</button></li></ul>
</main>
<div id="toast" class="toast"></div>

<div id="modal" class="modal" style="display:none">
  <form id="wizard">
    <section data-step="1">
      <p class="hint">Your cost-centre code is <b id="cc">CC-4471</b>.</p>
      <label>Date <input name="date" type="date"></label>
      <label>Client <input name="client"></label>
      <label>Project <input name="project"></label>
      <label>Category <select name="category"><option>Travel</option><option>Meals</option><option>Lodging</option></select></label>
      <label>Amount <input name="amount" inputmode="decimal"></label>
      <label>Currency <select name="currency"><option>EUR</option><option>USD</option></select></label>
      <label>Payment method <select name="method"><option>Corporate card</option><option>Personal</option></select></label>
      <label>Receipt number <input name="receipt"></label>
      <label>Description <input name="description"></label>
      <button type="button" class="next">Continue</button>
    </section>
    <section data-step="2" hidden>
      <label>Cost-centre code <input name="costCentre"></label>
      <label>Billable to client <input name="billable" type="checkbox"></label>
      <button type="button" class="back">Back</button>
      <button type="button" class="next">Continue</button>
      <button type="button" class="skip">Proceed</button>
    </section>
    <section data-step="3" hidden>
      <label>Type the amount again to confirm <input name="amountConfirm"></label>
      <button type="button" class="back">Back</button>
      <button type="submit">Submit</button>
    </section>
  </form>
</div>
<script type="module" src="app.js"></script>
</body>
</html>
"""

STYLES_CSS = """* { box-sizing: border-box; }
body { font: 15px system-ui, sans-serif; margin: 0; }
header { display: flex; justify-content: space-between; padding: 16px; }
button { transition: all 600ms cubic-bezier(.68,-0.55,.27,1.55); }
button:hover { transform: scale(1.15); }
.banner { background: #c00; color: #fff; padding: 8px 16px; }
.modal { position: fixed; inset: 0; background: rgba(0,0,0,.4); }
.modal form { background: #fff; margin: 10vh auto; max-width: 420px; padding: 24px; animation: drop 700ms cubic-bezier(.68,-0.55,.27,1.55); }
@keyframes drop { from { transform: translateY(-100vh) rotate(-8deg); } }
label { display: block; margin: 8px 0; }
.toast { position: fixed; bottom: 16px; right: 16px; opacity: 0; transition: all 600ms; }
.toast.show { opacity: 1; }
li { transition: all 600ms; }
"""

APP_JS = """import { submitClaim, deleteClaim } from './api.js';

const modal = document.getElementById('modal');
const form = document.getElementById('wizard');
const list = document.getElementById('claims');
let step = 1;

function show(n) {
  step = n;
  form.querySelectorAll('section').forEach((s) => { s.hidden = Number(s.dataset.step) !== n; });
}

document.getElementById('new').onclick = () => { modal.style.display = 'block'; show(1); };
form.addEventListener('click', (e) => {
  if (e.target.classList.contains('next')) show(step + 1);
  if (e.target.classList.contains('skip')) show(3);
  if (e.target.classList.contains('back')) { form.reset(); show(step - 1); }
});

form.addEventListener('submit', async (e) => {
  e.preventDefault();
  const claim = Object.fromEntries(new FormData(form));
  try {
    const saved = await submitClaim(claim);
    modal.style.display = 'none';
    list.insertAdjacentHTML('afterbegin', `<li data-id="${saved.id}">${claim.description} · ${claim.amount} ${claim.currency} · Submitted <button class="del">×</button></li>`);
    toast('Saved');
  } catch {
    form.reset();
    document.getElementById('error').hidden = false;
  }
});

list.addEventListener('click', (e) => {
  if (!e.target.classList.contains('del')) return;
  const li = e.target.closest('li');
  li.remove();
  deleteClaim(li.dataset.id);
});

function toast(text) {
  const t = document.getElementById('toast');
  t.textContent = text;
  t.classList.add('show');
  setTimeout(() => t.classList.remove('show'), 900);
}
"""

WIZARD_V2_NOTE = """# Wizard v2 (ships next release)

- Added a step indicator ("Step 2 of 3").
- Step 2 now pre-fills the cost-centre code.
- Step 3 shows a summary of the claim instead of asking to retype the amount.
- Renamed "Proceed" to "Skip billing details".

Nobody has run a usability test or measured anything yet.
"""


def git(cwd: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True)


def build(root: Path, extra: dict[str, str] | None = None) -> Path:
    origin, repo = root / "origin.git", root / "repo"
    subprocess.run(["git", "init", "-q", "--bare", "-b", "main", str(origin)], check=True)
    subprocess.run(["git", "clone", "-q", str(origin), str(repo)], check=True, capture_output=True)
    git(repo, "config", "user.name", "Eval Dev")
    git(repo, "config", "user.email", "dev@example.com")
    files = {"README.md": README, "api.js": API_JS, "index.html": INDEX_HTML, "styles.css": STYLES_CSS, "app.js": APP_JS}
    files.update(extra or {})
    for rel, text in files.items():
        (repo / rel).parent.mkdir(parents=True, exist_ok=True)
        (repo / rel).write_text(text)
    git(repo, "add", "-A")
    git(repo, "commit", "-qm", "feat: claims app")
    git(repo, "push", "-q", "origin", "main")
    return repo


def main() -> None:
    case, root = sys.argv[1], Path(sys.argv[2])
    extra = {"docs/wizard-v2.md": WIZARD_V2_NOTE} if case == "measured-claim" else None
    build(root, extra)


if __name__ == "__main__":
    main()
