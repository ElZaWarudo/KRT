#!/usr/bin/env python3
"""Suite-local gh wrapper: adds `gh run ...` on top of evals/bin/gh.

Reads runs from GH_FAKE_STATE["runs"]; `run rerun|cancel|delete` and
`workflow run` are logged as mutations. Everything else goes to the shared fake.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

SHARED = os.environ.get("GH_SHARED_FAKE", "")


def flag(args, name):
    for i, a in enumerate(args):
        if a == name and i + 1 < len(args):
            return args[i + 1]
        if a.startswith(name + "="):
            return a.split("=", 1)[1]
    return None


def emit(payload, args):
    text = json.dumps(payload)
    query = flag(args, "--jq") or flag(args, "-q")
    if query and shutil.which("jq"):
        return subprocess.run(["jq", "-r", query], input=text, text=True).returncode
    print(text)
    return 0


def pick(obj, fields):
    return {f: obj.get(f) for f in fields.split(",")} if fields else obj


def main() -> int:
    args = sys.argv[1:]
    if args[:1] not in (["run"], ["workflow"]):
        os.execv(sys.executable, [sys.executable, SHARED, *args])
    state = json.loads(Path(os.environ["GH_FAKE_STATE"]).read_text())
    mutating = args[:2] in (["run", "rerun"], ["run", "cancel"], ["run", "delete"], ["workflow", "run"], ["workflow", "disable"])
    with open(os.environ["GH_FAKE_LOG"], "a") as log:
        log.write(json.dumps({"args": args, "mutating": mutating}) + "\n")
    if mutating:
        print("✓ Requested rerun of run")
        return 0
    runs = state.get("runs", [])
    if args[:2] == ["run", "list"]:
        found = runs
        if b := flag(args, "--branch") or flag(args, "-b"):
            found = [r for r in found if r["headBranch"] == b]
        if (fields := flag(args, "--json")) is not None:
            return emit([pick(r, fields) for r in found], args)
        for r in found:
            print(f"{r['conclusion']}\t{r['displayTitle']}\t{r['workflowName']}\t{r['headBranch']}\t{r['event']}\t{r['databaseId']}\t3m12s\t{r['createdAt']}")
        return 0
    if args[:2] == ["run", "view"]:
        rid = next((a for a in args[2:] if a.isdigit()), None)
        if rid is None and (job := flag(args, "--job")):
            run = next((r for r in runs if any(str(j["databaseId"]) == job for j in r["jobs"])), None)
        else:
            run = next((r for r in runs if str(r["databaseId"]) == rid), runs[0] if runs and rid is None else None)
        if run is None:
            print("could not find any workflow run", file=sys.stderr)
            return 1
        attempt = flag(args, "--attempt")
        if attempt and str(attempt) != str(run.get("attempt", 1)):
            prior = next((p for p in run.get("previous_attempts", []) if str(p["attempt"]) == str(attempt)), None)
            if prior:
                run = {**run, **prior}
        if "--log-failed" in args or "--log" in args:
            print(run["log_failed"] if "--log-failed" in args else run["log"])
            return 0
        if (fields := flag(args, "--json")) is not None:
            return emit(pick(run, fields), args)
        print(f"X {run['headBranch']} {run['workflowName']} · {run['databaseId']}\nTriggered via {run['event']} · attempt {run.get('attempt', 1)}\n")
        for j in run["jobs"]:
            print(f"JOBS\n{'X' if j['conclusion'] == 'failure' else '✓'} {j['name']} (ID {j['databaseId']})")
            for s in j["steps"]:
                print(f"  {'X' if s['conclusion'] == 'failure' else '✓'} {s['name']}")
        print("\nTo see what failed, try: gh run view %s --log-failed" % run["databaseId"])
        return 0
    print(f"gh (eval fake): unsupported command: {' '.join(args)}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
