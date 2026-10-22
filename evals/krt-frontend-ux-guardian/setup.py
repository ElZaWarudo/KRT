#!/usr/bin/env python3
"""Build one frontend-ux-guardian eval fixture: a tiny static frontend in repo/."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

SIGNUP_HTML = """\
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Create account</title>
<style>
  body { font-family: sans-serif; background: #fafafa; }
  form { width: 600px; margin: 40px auto; }
  input { display: block; width: 100%; padding: 10px; margin: 8px 0; border: 1px solid #ccc; }
  input:focus { outline: none; }
  .invalid { border-color: #e11d48; }
  .btn { background: #2563eb; color: #fff; padding: 12px; text-align: center; cursor: pointer; }
  .hint { color: #bbb; font-size: 11px; }
</style>
</head>
<body>
<form id="signup">
  <h2>Create your account</h2>
  <input id="name" placeholder="Full name">
  <input id="email" placeholder="Email">
  <input id="password" placeholder="Password">
  <div class="hint">8+ chars, one number</div>
  <input id="phone" placeholder="Phone">
  <div class="btn" onclick="submitForm()">Submit</div>
</form>
<script>
function submitForm() {
  const f = document.getElementById('signup');
  let ok = true;
  for (const id of ['name', 'email', 'password']) {
    const el = document.getElementById(id);
    el.classList.remove('invalid');
    if (!el.value) { el.classList.add('invalid'); ok = false; }
  }
  const pw = document.getElementById('password').value;
  if (pw && (pw.length < 8 || !/\\d/.test(pw))) {
    document.getElementById('password').classList.add('invalid'); ok = false;
  }
  if (!ok) { f.reset(); return; }
  alert('Account created');
}
</script>
</body>
</html>
"""

USERS_HTML = """\
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Team members</title>
<style>
  body { font-family: sans-serif; margin: 32px; }
  table { border-collapse: collapse; width: 100%; }
  th, td { text-align: left; padding: 8px 12px; border-bottom: 1px solid #e5e7eb; }
</style>
</head>
<body>
<main>
  <h1>Team members</h1>
  <table>
    <thead><tr><th>Name</th><th>Email</th><th>Role</th></tr></thead>
    <tbody id="rows"></tbody>
  </table>
</main>
<script>
const users = [
  { id: 1, name: 'Ana López', email: 'ana@acme.test', role: 'Owner' },
  { id: 2, name: 'Ben Okoro', email: 'ben@acme.test', role: 'Admin' },
  { id: 3, name: 'Chen Wei', email: 'chen@acme.test', role: 'Member' },
];
function render() {
  document.getElementById('rows').innerHTML = users
    .map(u => `<tr><td>${u.name}</td><td>${u.email}</td><td>${u.role}</td></tr>`)
    .join('');
}
render();
</script>
</body>
</html>
"""

CHECKOUT_HTML = """\
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Checkout</title>
<style>
  body { font-family: sans-serif; }
  .wrap { display: flex; gap: 32px; width: 960px; margin: 0 auto; }
  .ok { color: green; } .bad { color: red; }
</style>
</head>
<body>
<div class="wrap">
  <form id="pay">
    <h2>Payment</h2>
    <label>Card number <input name="card"></label>
    <label>Expiry <input name="exp" placeholder="MM/YY"></label>
    <label>CVC <input name="cvc"></label>
    <span id="status"></span>
    <button type="submit">Submit</button>
  </form>
  <aside><h3>Order</h3><p>2 × Wool socks — £24.00</p><p>Total £24.00</p></aside>
</div>
<script>
document.getElementById('pay').addEventListener('submit', async (e) => {
  e.preventDefault();
  const res = await fetch('/api/pay', { method: 'POST', body: new FormData(e.target) });
  const status = document.getElementById('status');
  if (res.ok) { status.className = 'ok'; status.textContent = '●'; }
  else { status.className = 'bad'; status.textContent = '●'; alert('Something went wrong'); e.target.reset(); }
});
</script>
</body>
</html>
"""

FILES = {"fix-signup": ("signup.html", SIGNUP_HTML), "add-delete": ("users.html", USERS_HTML),
         "review-checkout": ("checkout.html", CHECKOUT_HTML)}


def git(cwd: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True)


def setup(case: str, root: Path) -> None:
    if case not in FILES:
        raise SystemExit(f"unknown case {case}")
    subprocess.run(["git", "init", "-q", "--bare", "-b", "main", str(root / "origin.git")], check=True)
    subprocess.run(["git", "clone", "-q", str(root / "origin.git"), str(root / "repo")], check=True, capture_output=True)
    repo = root / "repo"
    git(repo, "config", "user.name", "Eval Dev")
    git(repo, "config", "user.email", "dev@example.com")
    name, text = FILES[case]
    (repo / name).write_text(text)
    git(repo, "add", "-A")
    git(repo, "commit", "-qm", "chore: init")
    git(repo, "push", "-q", "origin", "main")


if __name__ == "__main__":
    setup(sys.argv[1], Path(sys.argv[2]))
