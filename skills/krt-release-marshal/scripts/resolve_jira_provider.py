#!/usr/bin/env python3
"""Resolve Jira Cloud or Server/Data Center without a silent default."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


PROVIDERS = ("cloud", "server-datacenter")
SKILLS = {
    "cloud": "krt-jira-cloud-scribe",
    "server-datacenter": "krt-jira-scribe",
}


def provider_from_url(jira_url: str | None) -> str | None:
    if not jira_url:
        return None
    candidate = jira_url if "://" in jira_url else f"https://{jira_url}"
    hostname = (urlparse(candidate).hostname or "").lower()
    if not hostname:
        return None
    return "cloud" if hostname == "atlassian.net" or hostname.endswith(".atlassian.net") else "server-datacenter"


def resolve_provider(
    *,
    explicit: str | None,
    jira_url: str | None,
    readiness: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    inferred = provider_from_url(jira_url)
    reasons: list[str] = []

    if explicit == "none":
        return {
            "ok": True,
            "provider": "none",
            "skill": None,
            "source": "explicit",
            "ready": True,
            "readiness": readiness,
            "block_reasons": [],
        }

    if explicit and explicit not in PROVIDERS:
        reasons.append(f"jira-provider-unsupported:{explicit}")
    elif explicit and inferred and explicit != inferred:
        reasons.append("jira-provider-conflict:explicit-vs-url")

    provider: str | None = None
    source: str | None = None
    if not reasons and explicit:
        provider, source = explicit, "explicit"
    elif not reasons and inferred:
        provider, source = inferred, "url"
    elif not reasons:
        ready = [name for name in PROVIDERS if readiness.get(name, {}).get("ok") is True]
        if len(ready) == 1:
            provider, source = ready[0], "readiness"
        elif len(ready) > 1:
            reasons.append("jira-provider-ambiguous")
        else:
            reasons.append("jira-provider-unresolved")

    provider_ready = provider is not None and readiness.get(provider, {}).get("ok") is True
    if provider and not provider_ready:
        reasons.append(f"jira-provider-not-ready:{provider}")

    return {
        "ok": provider is not None and not reasons,
        "provider": provider if not reasons or (provider and len(reasons) == 1 and reasons[0].startswith("jira-provider-not-ready:")) else None,
        "skill": SKILLS.get(provider) if provider else None,
        "source": source,
        "ready": provider_ready,
        "readiness": readiness,
        "block_reasons": reasons,
    }


def check_readiness(skills_dir: Path, root: Path, provider: str) -> dict[str, Any]:
    skill = SKILLS[provider]
    checker = skills_dir / skill / "scripts" / "check_jira_env.py"
    if not checker.exists():
        return {"ok": False, "diagnosis": "checker-missing", "checker": str(checker)}
    completed = subprocess.run(
        [sys.executable, str(checker), "--root", str(root)],
        text=True,
        capture_output=True,
        check=False,
    )
    try:
        result = json.loads(completed.stdout)
    except json.JSONDecodeError:
        return {
            "ok": False,
            "diagnosis": "checker-output-not-json",
            "checker": str(checker),
            "returncode": completed.returncode,
        }
    result["checker"] = str(checker)
    result["returncode"] = completed.returncode
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--provider", choices=("auto", "cloud", "server-datacenter", "none"), default="auto")
    parser.add_argument("--jira-url")
    parser.add_argument("--skills-dir", type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()

    readiness = {
        provider: check_readiness(args.skills_dir.resolve(), args.root.resolve(), provider)
        for provider in PROVIDERS
    }
    result = resolve_provider(
        explicit=None if args.provider == "auto" else args.provider,
        jira_url=args.jira_url,
        readiness=readiness,
    )
    print(json.dumps(result, sort_keys=True, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
