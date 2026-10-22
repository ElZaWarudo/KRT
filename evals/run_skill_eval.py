#!/usr/bin/env python3
"""Run a skill eval suite against skill variants with headless Claude Code.

Each variant is `name=spec`, where spec is `none` (no skills), `worktree`
(current skills/), or a git ref (skills/ at that ref). Every case runs in a
fresh fixture with only the variant's skills installed as project skills, so
user-level skills do not leak in. Results combine deterministic state checks
(fake gh log, git refs) with an LLM judge over the final reply.

  python3 evals/run_skill_eval.py evals/krt-release-marshal \
      --variant none=none --variant old=main --variant new=worktree --reps 2
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import statistics
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
FAKE_BIN = REPO / "evals" / "bin"
ALLOWED_TOOLS = [
    "Read", "Glob", "Grep", "Skill", "Write", "Edit",
    "Bash(git:*)", "Bash(gh:*)", "Bash(python3:*)", "Bash(ls:*)", "Bash(cat:*)",
    "Bash(mktemp:*)", "Bash(find:*)", "Bash(head:*)", "Bash(wc:*)",
]


def sh(cwd: Path, *args: str) -> str:
    return subprocess.run(args, cwd=cwd, capture_output=True, text=True).stdout.strip()


def materialize(spec: str, skills: list[str], dest: Path) -> None:
    dest.mkdir(parents=True)
    if spec == "none":
        return
    for skill in skills:
        # Skills missing at this version (merged or removed) are skipped.
        if spec == "worktree":
            if (REPO / "skills" / skill).is_dir():
                shutil.copytree(REPO / "skills" / skill, dest / skill)
            continue
        proc = subprocess.run(["git", "archive", spec, f"skills/{skill}"], cwd=REPO, capture_output=True)
        if proc.returncode != 0:
            continue
        archive = proc.stdout
        subprocess.run(["tar", "-x", "-C", str(dest), "--strip-components=1"], input=archive, check=True)


def default_fixture(root: Path) -> None:
    """Empty project with one commit and a local bare origin."""
    subprocess.run(["git", "init", "-q", "--bare", "-b", "main", str(root / "origin.git")], check=True)
    subprocess.run(["git", "clone", "-q", str(root / "origin.git"), str(root / "repo")], check=True, capture_output=True)
    repo = root / "repo"
    (repo / "README.md").write_text("# app\n")
    for args in (["config", "user.name", "Eval Dev"], ["config", "user.email", "dev@example.com"],
                 ["add", "-A"], ["commit", "-qm", "chore: init"], ["push", "-q", "origin", "main"]):
        subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True)


def snapshot(root: Path) -> dict:
    repo = root / "repo"
    return {
        "origin": sh(root / "origin.git", "git", "for-each-ref", "--format=%(refname) %(objectname)"),
        "worktree": sh(repo, "git", "status", "--porcelain") + "\n" + sh(repo, "git", "rev-parse", "HEAD"),
        "refs": sh(repo, "git", "for-each-ref", "--format=%(refname:short) %(objectname)", "refs/heads"),
    }


def parse_stream(raw: str) -> dict:
    out = {"skills": [], "bash": [], "result": "", "cost": 0.0, "duration_ms": 0, "turns": 0, "tokens": 0}
    for line in raw.splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if event.get("type") == "assistant":
            for block in event.get("message", {}).get("content", []):
                if block.get("type") != "tool_use":
                    continue
                if block["name"] == "Skill":
                    out["skills"].append(block["input"].get("skill"))
                elif block["name"] == "Bash":
                    out["bash"].append(block["input"].get("command", ""))
        elif event.get("type") == "result":
            usage = event.get("usage", {})
            out.update(
                result=event.get("result", ""),
                cost=event.get("total_cost_usd", 0.0),
                duration_ms=event.get("duration_ms", 0),
                turns=event.get("num_turns", 0),
                tokens=sum(usage.get(k, 0) for k in (
                    "input_tokens", "output_tokens", "cache_creation_input_tokens", "cache_read_input_tokens")),
            )
    return out


def deterministic(checks: dict, before: dict, after: dict, gh_log: list[dict], text: str, repo: Path) -> dict:
    results = {}
    if checks.get("no_gh_mutation"):
        results["no_gh_mutation"] = not any(c["mutating"] for c in gh_log)
    if checks.get("origin_unchanged"):
        results["origin_unchanged"] = before["origin"] == after["origin"]
    if checks.get("worktree_unchanged"):
        results["worktree_unchanged"] = before["worktree"] == after["worktree"]
    for ref in checks.get("refs_unchanged", []):
        pick = lambda refs: [l for l in refs.splitlines() if l.split(" ")[0] == ref]
        results[f"ref_unchanged:{ref}"] = pick(before["refs"]) == pick(after["refs"])
    for pattern in checks.get("text_matches", []):
        results[f"text_matches:{pattern}"] = re.search(pattern, text) is not None
    for pattern in checks.get("text_not_matches", []):
        results[f"text_not_matches:{pattern}"] = re.search(pattern, text) is None
    for glob, pattern in checks.get("file_matches", {}).items():
        files = [f for f in repo.glob(glob) if f.is_file() and ".claude" not in f.parts]
        results[f"file_matches:{glob}"] = any(re.search(pattern, f.read_text(errors="ignore")) for f in files)
    return results


def work_product(repo: Path, limit: int = 40_000) -> str:
    """Tracked diff plus untracked files, for judging skills whose output is files."""
    parts = [sh(repo, "git", "diff", "HEAD")]
    for rel in sh(repo, "git", "ls-files", "--others", "--exclude-standard").splitlines():
        if "__pycache__" in rel:
            continue
        try:
            data = (repo / rel).read_bytes()
        except (IsADirectoryError, FileNotFoundError):
            continue
        body = "[binary file]" if b"\0" in data[:8192] else data.decode(errors="ignore")
        parts.append(f"--- new file: {rel}\n{body}")
    text = "\n".join(p for p in parts if p)
    return text if len(text) <= limit else text[:limit] + "\n[... truncated]"


def judge(case: dict, text: str, model: str, files: str = "") -> dict:
    criteria = "\n".join(f"{i}. {c}" for i, c in enumerate(case["rubric"], 1))
    product = f"Files the agent changed or created:\n<files>\n{files}\n</files>\n\n" if files else ""
    prompt = (
        "You are grading an AI coding agent's work in a sandboxed eval; no user answered its questions. "
        "Judge strictly against each criterion using only the evidence below.\n\n"
        f"User request:\n<request>\n{case['prompt']}\n</request>\n\n"
        f"Agent final reply:\n<reply>\n{text}\n</reply>\n\n{product}"
        f"Criteria:\n{criteria}\n\n"
        'Return only a JSON array, one object per criterion: [{"id": 1, "pass": true, "reason": "..."}]'
    )
    with tempfile.TemporaryDirectory() as empty:
        proc = subprocess.run(
            ["claude", "-p", prompt, "--setting-sources", "project", "--model", model, "--output-format", "json"],
            cwd=empty, capture_output=True, text=True, timeout=300,
        )
    try:
        reply = json.loads(proc.stdout)["result"]
        verdicts = json.loads(reply[reply.index("["): reply.rindex("]") + 1])
        return {f"rubric:{v['id']}": bool(v["pass"]) for v in verdicts} | {
            "_reasons": {str(v["id"]): v.get("reason", "") for v in verdicts}}
    except (ValueError, KeyError, json.JSONDecodeError):
        return {"rubric:judge_error": False, "_reasons": {"error": proc.stdout[-500:] + proc.stderr[-500:]}}


def run_one(suite: dict, suite_dir: Path, case: dict, variant: str, spec: str, rep: int, args, out: Path) -> dict:
    root = out / "runs" / f"{case['id']}__{variant}__{rep}"
    root.mkdir(parents=True)
    if (suite_dir / "setup.py").exists():
        subprocess.run([sys.executable, str(suite_dir / "setup.py"), case["id"], str(root)], check=True)
    else:
        default_fixture(root)
    if not (root / "gh-state.json").exists():
        (root / "gh-state.json").write_text(json.dumps({"repo": "acme/app"}))
    materialize(spec, suite["skills"], root / "repo" / ".claude" / "skills")
    with open(root / "repo" / ".git" / "info" / "exclude", "a") as exclude:
        exclude.write(".claude/\n")
    before = snapshot(root)
    gh_log_path = root / "gh-log.jsonl"
    gh_log_path.touch()
    env = os.environ | {
        "PATH": f"{FAKE_BIN}:{os.environ['PATH']}",
        "GH_FAKE_STATE": str(root / "gh-state.json"),
        "GH_FAKE_LOG": str(gh_log_path),
    }
    cmd = [
        "claude", "-p", (f"/{suite['skill']} " if args.invoke else "") + case["prompt"], "--setting-sources", "project", "--model", args.model,
        "--output-format", "stream-json", "--verbose", "--max-budget-usd", str(args.budget),
        "--allowedTools", *ALLOWED_TOOLS, *suite.get("allowed_tools", []),
    ]
    try:
        proc = subprocess.run(cmd, cwd=root / "repo", env=env, capture_output=True, text=True, timeout=args.timeout)
        raw = proc.stdout
    except subprocess.TimeoutExpired as exc:
        raw = exc.stdout.decode() if isinstance(exc.stdout, bytes) else (exc.stdout or "")
    (root / "transcript.jsonl").write_text(raw)
    run = parse_stream(raw)
    after = snapshot(root)
    gh_log = [json.loads(l) for l in gh_log_path.read_text().splitlines() if l.strip()]
    checks = deterministic(case.get("checks", {}), before, after, gh_log, run["result"], root / "repo")
    files = work_product(root / "repo") if case.get("judge_files") else ""
    graded = judge(case, run["result"], args.judge_model, files) if run["result"] else {"rubric:no_reply": False}
    reasons = graded.pop("_reasons", {})
    checks |= graded
    record = {
        "case": case["id"], "variant": variant, "rep": rep, "checks": checks, "reasons": reasons,
        "passed": sum(checks.values()), "total": len(checks), "skill_used": args.invoke or suite["skill"] in run["skills"],
        **{k: run[k] for k in ("cost", "duration_ms", "turns", "tokens", "skills")},
        "reply": run["result"],
    }
    (root / "record.json").write_text(json.dumps(record, indent=2, ensure_ascii=False))
    print(f"{case['id']:<22} {variant:<6} rep{rep} {record['passed']}/{record['total']} ${record['cost']:.2f}", flush=True)
    return record


def safe_run(*args) -> dict | None:
    """One crashed run (fixture, judge, decode) must not abort the suite."""
    try:
        return run_one(*args)
    except Exception as exc:  # noqa: BLE001
        print(f"RUN FAILED {args[2]['id']} {args[3]} rep{args[5]}: {exc!r}", flush=True)
        return None


def summarize(records: list[dict], variants: list[str]) -> str:
    rows = ["| variant | checks passed | fully passing runs | skill invoked | mean cost | mean tokens | mean time |",
            "|---|---|---|---|---|---|---|"]
    for v in variants:
        rs = [r for r in records if r["variant"] == v]
        if not rs:
            continue
        p, t = sum(r["passed"] for r in rs), sum(r["total"] for r in rs)
        rows.append(
            f"| {v} | {p}/{t} ({p / t:.0%}) | {sum(r['passed'] == r['total'] for r in rs)}/{len(rs)} "
            f"| {sum(r['skill_used'] for r in rs)}/{len(rs)} | ${statistics.mean(r['cost'] for r in rs):.2f} "
            f"| {statistics.mean(r['tokens'] for r in rs):,.0f} | {statistics.mean(r['duration_ms'] for r in rs) / 1000:.0f}s |"
        )
    rows += ["", "| case | " + " | ".join(variants) + " |", "|---|" + "---|" * len(variants)]
    for case in dict.fromkeys(r["case"] for r in records):
        cells = []
        for v in variants:
            rs = [r for r in records if r["case"] == case and r["variant"] == v]
            cells.append(f"{sum(r['passed'] for r in rs)}/{sum(r['total'] for r in rs)}" if rs else "-")
        rows.append(f"| {case} | " + " | ".join(cells) + " |")
    failures = [f"- {r['case']} / {r['variant']} rep{r['rep']}: {k}" + (f" — {r['reasons'].get(k.split(':')[1], '')}" if k.startswith("rubric:") else "")
                for r in records for k, ok in r["checks"].items() if not ok]
    return "\n".join(rows + ["", "Failures:", *failures])


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("suite", type=Path)
    parser.add_argument("--variant", action="append", required=True, help="name=none|worktree|<git-ref>")
    parser.add_argument("--cases", nargs="*")
    parser.add_argument("--reps", type=int, default=1)
    parser.add_argument("--model", default="opus")
    parser.add_argument("--judge-model", default="sonnet")
    parser.add_argument("--budget", type=float, default=3.0, help="max USD per agent run")
    parser.add_argument("--timeout", type=int, default=900)
    parser.add_argument("--jobs", type=int, default=4)
    parser.add_argument("--invoke", action="store_true", help="prefix prompts with /<skill> to force loading")
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()

    suite = json.loads((args.suite / "cases.json").read_text())
    cases = [c for c in suite["cases"] if not args.cases or c["id"] in args.cases]
    variants = [v.split("=", 1) for v in args.variant]
    out = args.out or Path(tempfile.mkdtemp(prefix=f"eval-{suite['skill']}-"))
    out.mkdir(parents=True, exist_ok=True)
    jobs = [(c, name, spec, rep) for c in cases for name, spec in variants for rep in range(1, args.reps + 1)]
    with ThreadPoolExecutor(args.jobs) as pool:
        records = [r for r in pool.map(lambda j: safe_run(suite, args.suite, *j, args, out), jobs) if r]
    (out / "results.json").write_text(json.dumps(records, indent=2, ensure_ascii=False))
    report = summarize(records, [name for name, _ in variants])
    (out / "summary.md").write_text(report + "\n")
    print(f"\n{report}\n\nResults: {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
