#!/usr/bin/env python3
"""Validate and optionally apply PR review-thread replies and resolutions."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


REPLY_ONLY_DECISIONS = {"fix", "reply", "decline", "already-addressed", "stale"}
NON_RESOLVING_DECISIONS = {"clarify", "blocked"}

REPLY_MUTATION = """
mutation($threadId: ID!, $body: String!) {
  addPullRequestReviewThreadReply(
    input: {
      pullRequestReviewThreadId: $threadId
      body: $body
    }
  ) {
    comment {
      id
      url
      body
    }
  }
}
""".strip()

RESOLVE_MUTATION = """
mutation($threadId: ID!) {
  resolveReviewThread(input: {threadId: $threadId}) {
    thread {
      id
      isResolved
    }
  }
}
""".strip()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan-file", required=True, help="JSON file describing thread actions")
    parser.add_argument("--execute", action="store_true", help="Apply mutations with gh api graphql")
    parser.add_argument("--gh-bin", default="gh", help="GitHub CLI executable to run in execute mode")
    return parser.parse_args()


def load_plan(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def normalize_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def validate_plan(plan: dict[str, Any]) -> tuple[list[dict[str, Any]], list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    operations: list[dict[str, Any]] = []

    repository = normalize_text(plan.get("repository"))
    if not repository or "/" not in repository:
        errors.append("invalid-repository")

    pull_request = plan.get("pull_request")
    if not isinstance(pull_request, int) or pull_request <= 0:
        errors.append("invalid-pull-request")

    threads = plan.get("threads")
    if not isinstance(threads, list) or not threads:
        errors.append("missing-threads")
        return operations, errors, warnings

    seen_thread_ids: set[str] = set()
    for index, thread in enumerate(threads, start=1):
        prefix = f"thread[{index}]"
        if not isinstance(thread, dict):
            errors.append(f"{prefix}:invalid-thread-entry")
            continue

        thread_id = normalize_text(thread.get("thread_id"))
        if not thread_id:
            errors.append(f"{prefix}:missing-thread-id")
            continue
        if thread_id in seen_thread_ids:
            warnings.append(f"{prefix}:duplicate-thread-id:{thread_id}")
        seen_thread_ids.add(thread_id)

        decision = normalize_text(thread.get("decision"))
        if not decision:
            errors.append(f"{prefix}:missing-decision")
            continue

        reply = normalize_text(thread.get("reply"))
        resolve = bool(thread.get("resolve", False))
        verification = normalize_text(thread.get("verification"))
        resolution_reason = normalize_text(thread.get("resolution_reason"))
        path = normalize_text(thread.get("path"))
        line = thread.get("line")

        if not reply and not resolve:
            warnings.append(f"{prefix}:no-remote-actions")

        if reply and decision in NON_RESOLVING_DECISIONS:
            warnings.append(f"{prefix}:reply-with-nonresolving-decision:{decision}")

        if resolve:
            if decision in NON_RESOLVING_DECISIONS:
                errors.append(f"{prefix}:resolve-forbidden-for-decision:{decision}")
            if not reply:
                errors.append(f"{prefix}:resolve-requires-reply")
            if decision not in REPLY_ONLY_DECISIONS:
                warnings.append(f"{prefix}:resolve-with-unrecognized-decision:{decision}")
            if not verification and not resolution_reason:
                errors.append(f"{prefix}:resolve-requires-verification-or-reason")

        operations.append(
            {
                "thread_id": thread_id,
                "path": path or None,
                "line": line if isinstance(line, int) and line > 0 else None,
                "classification": normalize_text(thread.get("classification")) or None,
                "decision": decision,
                "reply": reply or None,
                "resolve": resolve,
                "verification": verification or None,
                "resolution_reason": resolution_reason or None,
            }
        )

    if not any(operation["reply"] or operation["resolve"] for operation in operations):
        warnings.append("plan-has-no-executable-actions")

    return operations, errors, warnings


def run_gh_graphql(gh_bin: str, query: str, variables: dict[str, str]) -> dict[str, Any]:
    command = [gh_bin, "api", "graphql", "-f", f"query={query}"]
    for key, value in variables.items():
        command.extend(["-f", f"{key}={value}"])

    completed = subprocess.run(command, text=True, capture_output=True, check=False)
    if completed.returncode != 0:
        raise RuntimeError(completed.stderr.strip() or completed.stdout.strip() or "gh api graphql failed")
    try:
        return json.loads(completed.stdout or "{}")
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"gh api graphql returned non-JSON output: {exc}") from exc


def execute_operations(operations: list[dict[str, Any]], gh_bin: str) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for operation in operations:
        entry = dict(operation)
        entry["status"] = "planned"
        entry["result"] = {}

        if not operation["reply"] and not operation["resolve"]:
            entry["status"] = "skipped"
            results.append(entry)
            continue

        if operation["reply"]:
            reply_result = run_gh_graphql(
                gh_bin,
                REPLY_MUTATION,
                {
                    "threadId": operation["thread_id"],
                    "body": operation["reply"],
                },
            )
            entry["result"]["reply"] = reply_result

        if operation["resolve"]:
            resolve_result = run_gh_graphql(
                gh_bin,
                RESOLVE_MUTATION,
                {
                    "threadId": operation["thread_id"],
                },
            )
            entry["result"]["resolve"] = resolve_result

        entry["status"] = "executed"
        results.append(entry)

    return results


def summarize(results: list[dict[str, Any]]) -> dict[str, int]:
    return {
        "threads": len(results),
        "reply_count": sum(1 for item in results if item.get("reply")),
        "resolve_count": sum(1 for item in results if item.get("resolve")),
        "executed_count": sum(1 for item in results if item.get("status") == "executed"),
        "skipped_count": sum(1 for item in results if item.get("status") == "skipped"),
    }


def main() -> int:
    args = parse_args()
    plan = load_plan(Path(args.plan_file))
    operations, errors, warnings = validate_plan(plan)

    if errors:
        result = {
            "allowed": False,
            "repository": plan.get("repository"),
            "pull_request": plan.get("pull_request"),
            "execute": bool(args.execute),
            "errors": errors,
            "warnings": warnings,
            "operations": operations,
            "summary": summarize(operations),
        }
        print(json.dumps(result, sort_keys=True, indent=2))
        return 1

    try:
        results = execute_operations(operations, args.gh_bin) if args.execute else [
            {**operation, "status": "planned", "result": {}} for operation in operations
        ]
    except RuntimeError as exc:
        result = {
            "allowed": False,
            "repository": plan.get("repository"),
            "pull_request": plan.get("pull_request"),
            "execute": bool(args.execute),
            "errors": [f"execution-failed:{exc}"],
            "warnings": warnings,
            "operations": operations,
            "summary": summarize(operations),
        }
        print(json.dumps(result, sort_keys=True, indent=2))
        return 1

    result = {
        "allowed": True,
        "repository": plan.get("repository"),
        "pull_request": plan.get("pull_request"),
        "execute": bool(args.execute),
        "errors": [],
        "warnings": warnings,
        "operations": results,
        "summary": summarize(results),
    }
    print(json.dumps(result, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
