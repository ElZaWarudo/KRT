#!/usr/bin/env python3
"""Call the Jira Server/Data Center REST API with the checkout-local env.

  jira_api.py [--root DIR] METHOD PATH [--query k=v ...] [--data JSON | --data-file FILE]

Loads .krt/env/jira-scribe.env, normalizes JIRA_HOST, sends
`Authorization: Bearer $JIRA_API_TOKEN`, and prints {"status", "body"} as JSON.
The token never appears on the command line or in output. Exit 0 on 2xx,
1 on an HTTP or network error, 2 when configuration is missing.
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

from jira_env_runtime import REQUIRED_VARS, SECRET_PATH, load_env_from_secret

HOST_VAR, TOKEN_VAR = "JIRA_HOST", "JIRA_API_TOKEN"


def auth_header(env: dict[str, str]) -> str:
    return f"Bearer {env[TOKEN_VAR]}"


def base_url(host: str) -> str:
    host = host.strip()
    if not host.startswith(("http://", "https://")):
        host = f"https://{host}"
    return host.rstrip("/")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="Consumer project root (default: cwd).")
    parser.add_argument("method", type=str.upper, choices=["GET", "POST", "PUT", "DELETE"])
    parser.add_argument("path", help="API path starting with /rest/, e.g. /rest/api/2/search")
    parser.add_argument("--query", action="append", default=[], metavar="KEY=VALUE", help="Query parameter; repeatable.")
    body = parser.add_mutually_exclusive_group()
    body.add_argument("--data", help="JSON request body.")
    body.add_argument("--data-file", type=Path, help="File containing the JSON request body.")
    args = parser.parse_args()

    root = args.root.resolve()
    if not (root / SECRET_PATH).exists():
        print(json.dumps({"ok": False, "reason": "missing-secret-env-file", "secret_path": str(SECRET_PATH)}))
        return 2
    try:
        env, _ = load_env_from_secret(root)
    except ValueError as exc:
        print(json.dumps({"ok": False, "reason": "env-file-parse-error", "detail": str(exc)}))
        return 2
    missing = [name for name in REQUIRED_VARS if not env.get(name)]
    if missing:
        print(json.dumps({"ok": False, "reason": "missing-required-vars", "missing_required_vars": missing}))
        return 2
    if not args.path.startswith("/rest/"):
        print(json.dumps({"ok": False, "reason": "path-must-start-with-/rest/"}))
        return 2

    query = [tuple(item.split("=", 1)) for item in args.query if "=" in item]
    url = base_url(env[HOST_VAR]) + args.path + (f"?{urllib.parse.urlencode(query)}" if query else "")
    raw = args.data_file.read_text(encoding="utf-8") if args.data_file else args.data
    data = None
    if raw is not None:
        try:
            data = json.dumps(json.loads(raw), ensure_ascii=False).encode("utf-8")
        except json.JSONDecodeError as exc:
            print(json.dumps({"ok": False, "reason": "invalid-json-body", "detail": str(exc)}))
            return 2

    request = urllib.request.Request(url, data=data, method=args.method)
    request.add_header("Authorization", auth_header(env))
    request.add_header("Accept", "application/json")
    if data is not None:
        request.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            status, text = response.status, response.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as exc:
        status, text = exc.code, exc.read().decode("utf-8", errors="replace")
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        print(json.dumps({"ok": False, "reason": "network-error", "detail": str(getattr(exc, "reason", exc)), "url": url}))
        return 1
    try:
        payload = json.loads(text) if text.strip() else None
    except json.JSONDecodeError:
        payload = text[:4000]
    print(json.dumps({"status": status, "body": payload}, ensure_ascii=False, indent=1))
    return 0 if 200 <= status < 300 else 1


if __name__ == "__main__":
    sys.exit(main())
