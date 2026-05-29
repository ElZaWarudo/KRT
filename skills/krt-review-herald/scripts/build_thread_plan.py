#!/usr/bin/env python3
"""Build a review-thread action plan from a GitHub pull request."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


THREADS_QUERY = """
query(
  $owner: String!,
  $name: String!,
  $prNumber: Int!,
  $after: String
) {
  repository(owner: $owner, name: $name) {
    pullRequest(number: $prNumber) {
      id
      number
      title
      url
      reviewThreads(first: 100, after: $after) {
        nodes {
          id
          isResolved
          isOutdated
          path
          line
          originalLine
          startLine
          originalStartLine
          diffSide
          comments(first: 20) {
            totalCount
            nodes {
              id
              body
              createdAt
              url
              author {
                login
              }
            }
          }
        }
        pageInfo {
          hasNextPage
          endCursor
        }
      }
    }
  }
}
""".strip()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", required=True, help="Repository in owner/repo format")
    parser.add_argument("--pr", type=int, required=True, help="Pull request number")
    parser.add_argument("--output", help="Optional file path for the generated plan")
    parser.add_argument("--include-resolved", action="store_true", help="Include already resolved threads")
    parser.add_argument("--gh-bin", default="gh", help="GitHub CLI executable")
    return parser.parse_args()


def parse_repo(value: str) -> tuple[str, str]:
    owner, sep, name = value.strip().partition("/")
    if not owner or not sep or not name:
        raise ValueError(f"repo must be owner/repo: {value}")
    return owner, name


def run_gh_graphql(gh_bin: str, owner: str, name: str, pr_number: int, after: str | None) -> dict[str, Any]:
    command = [
        gh_bin,
        "api",
        "graphql",
        "-f",
        f"query={THREADS_QUERY}",
        "-f",
        f"owner={owner}",
        "-f",
        f"name={name}",
        "-F",
        f"prNumber={pr_number}",
    ]
    if after:
        command.extend(["-f", f"after={after}"])

    completed = subprocess.run(command, text=True, capture_output=True, check=False)
    if completed.returncode != 0:
        raise RuntimeError(completed.stderr.strip() or completed.stdout.strip() or "gh api graphql failed")
    try:
        return json.loads(completed.stdout or "{}")
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"gh api graphql returned non-JSON output: {exc}") from exc


def fetch_threads(gh_bin: str, owner: str, name: str, pr_number: int) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    pull_request: dict[str, Any] | None = None
    threads: list[dict[str, Any]] = []
    after: str | None = None

    while True:
        payload = run_gh_graphql(gh_bin, owner, name, pr_number, after)
        repository = (payload.get("data") or {}).get("repository") or {}
        pull_request = repository.get("pullRequest")
        if not pull_request:
            raise RuntimeError(f"pull request not found: {owner}/{name}#{pr_number}")

        review_threads = pull_request.get("reviewThreads") or {}
        threads.extend(review_threads.get("nodes") or [])
        page_info = review_threads.get("pageInfo") or {}
        if not page_info.get("hasNextPage"):
            return pull_request, threads
        after = page_info.get("endCursor")
        if not after:
            raise RuntimeError("missing pagination cursor")


def clean_body(value: Any) -> str:
    return str(value or "").strip()


def summarize_thread(thread: dict[str, Any]) -> dict[str, Any]:
    comments = (thread.get("comments") or {}).get("nodes") or []
    first_comment = comments[0] if comments else {}
    last_comment = comments[-1] if comments else {}
    author = (first_comment.get("author") or {}).get("login")

    return {
        "thread_id": thread.get("id"),
        "path": thread.get("path"),
        "line": thread.get("line"),
        "start_line": thread.get("startLine"),
        "original_line": thread.get("originalLine"),
        "original_start_line": thread.get("originalStartLine"),
        "diff_side": thread.get("diffSide"),
        "is_resolved": bool(thread.get("isResolved")),
        "is_outdated": bool(thread.get("isOutdated")),
        "reviewer": author,
        "thread_url": first_comment.get("url") or last_comment.get("url"),
        "original_comment": clean_body(first_comment.get("body")),
        "latest_comment": clean_body(last_comment.get("body")),
        "comment_count": (thread.get("comments") or {}).get("totalCount", len(comments)),
        "classification": "",
        "decision": "",
        "reply": "",
        "resolve": False,
        "verification": "",
        "resolution_reason": "",
    }


def build_plan(
    repository: str,
    pull_request: dict[str, Any],
    threads: list[dict[str, Any]],
    include_resolved: bool,
) -> dict[str, Any]:
    selected_threads = [
        summarize_thread(thread)
        for thread in threads
        if include_resolved or not bool(thread.get("isResolved"))
    ]

    return {
        "repository": repository,
        "pull_request": pull_request.get("number"),
        "source": {
            "pull_request_id": pull_request.get("id"),
            "pull_request_title": pull_request.get("title"),
            "pull_request_url": pull_request.get("url"),
            "include_resolved": include_resolved,
            "generated_by": "build_thread_plan.py",
            "total_threads_seen": len(threads),
            "threads_included": len(selected_threads),
        },
        "threads": selected_threads,
    }


def write_output(plan: dict[str, Any], output: str | None) -> None:
    rendered = json.dumps(plan, sort_keys=True, indent=2) + "\n"
    if output:
        Path(output).write_text(rendered, encoding="utf-8")
        return
    sys.stdout.write(rendered)


def main() -> int:
    args = parse_args()
    try:
        owner, name = parse_repo(args.repo)
        pull_request, threads = fetch_threads(args.gh_bin, owner, name, args.pr)
        plan = build_plan(args.repo, pull_request, threads, args.include_resolved)
        write_output(plan, args.output)
    except (RuntimeError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
