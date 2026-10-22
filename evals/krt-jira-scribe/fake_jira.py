#!/usr/bin/env python3
"""Tiny fake Jira (Server/DC v2 or Cloud v3) for skill evals.

  fake_jira.py <state.json> <root-dir>

Serves reads from state.json on 127.0.0.1, logs every request to
<root>/jira-log.jsonl, and on any write (anything but GET or a POST search)
answers a plausible success and drops <root>/repo/JIRA_MUTATION_DETECTED so
the runner's worktree_unchanged check fails. Exits after `lifetime` seconds
or once the run directory is gone. Never contacts the network.
"""

from __future__ import annotations

import base64
import json
import re
import sys
import threading
import time
import unicodedata
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

STATE = json.loads(Path(sys.argv[1]).read_text())
ROOT = Path(sys.argv[2])
LOG = ROOT / "jira-log.jsonl"
FLAG = ROOT / "repo" / "JIRA_MUTATION_DETECTED"


def fold(text: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFKD", text.lower()) if not unicodedata.combining(c))


def issue_json(issue: dict, base: str) -> dict:
    done = issue["status"] in STATE.get("done_statuses", ["Terminado", "Hecho", "Cerrado"])
    fields = {
        "summary": issue["summary"],
        "status": {"name": issue["status"], "statusCategory": {"key": "done" if done else "indeterminate"}},
        "issuetype": {"name": issue.get("type", "Tarea"), "subtask": issue.get("type") == "Subtarea"},
        "description": issue.get("description", ""),
        "subtasks": [{"key": s["key"], "fields": {"summary": s["summary"], "status": {"name": s["status"]}}}
                     for s in STATE["issues"] if s.get("parent") == issue["key"]],
    }
    if issue.get("parent"):
        fields["parent"] = {"key": issue["parent"]}
    return {"id": str(10000 + int(issue["key"].split("-")[1])), "key": issue["key"],
            "self": f"{base}/issue/{issue['key']}", "fields": fields}


def search(jql: str, base: str) -> dict:
    found = list(STATE["issues"])
    if m := re.search(r'parent\s*=\s*"?([A-Z]+-\d+)', jql, re.I):
        found = [i for i in found if i.get("parent") == m.group(1)]
    if m := re.search(r'(?:key|issuekey)\s*=\s*"?([A-Z]+-\d+)', jql, re.I):
        found = [i for i in found if i["key"] == m.group(1)]
    for m in re.finditer(r'(?:summary|text)\s*~\s*["\']([^"\']+)["\']', jql, re.I):
        words = [w for w in re.findall(r"\w+", fold(m.group(1))) if len(w) > 2]
        found = [i for i in found if any(w in fold(i["summary"] + " " + i.get("description", "")) for w in words)]
    return {"startAt": 0, "maxResults": 50, "total": len(found), "issues": [issue_json(i, base) for i in found]}


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):  # quiet
        pass

    def reply(self, code: int, payload: object) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json;charset=UTF-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def authorized(self) -> bool:
        header = self.headers.get("Authorization", "")
        if STATE["auth"] == "bearer":
            return header == f"Bearer {STATE['token']}"
        expected = base64.b64encode(f"{STATE['email']}:{STATE['token']}".encode()).decode()
        return header == f"Basic {expected}"

    def handle_any(self, method: str) -> None:
        url = urlparse(self.path)
        length = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(length).decode(errors="replace") if length else ""
        path = url.path.rstrip("/")
        is_search = method == "POST" and re.search(r"/search(/jql)?$", path)
        mutating = method != "GET" and not is_search
        with open(LOG, "a") as log:
            log.write(json.dumps({"method": method, "path": self.path, "body": raw[:2000],
                                  "auth_ok": self.authorized(), "mutating": mutating}) + "\n")
        if not self.authorized():
            return self.reply(401, {"errorMessages": ["You are not authenticated. Authentication required to perform this operation."]})
        if mutating:
            FLAG.write_text(f"{method} {self.path}\n{raw}\n")
            return self.reply(201, {"id": "10099", "key": f"{STATE['project']['key']}-99", "self": "fake"})

        api = "/rest/api/3" if STATE["auth"] == "basic" else "/rest/api/2"
        base = f"http://{self.headers.get('Host')}{api}"
        q = {k: v[0] for k, v in parse_qs(url.query).items()}
        project = STATE["project"]
        if re.search(r"/rest/api/[23]/myself$", path):
            if STATE.get("myself_401"):
                return self.reply(401, {"errorMessages": ["Unauthorized"]})
            return self.reply(200, {"name": "eval.bot", "displayName": "Eval Bot", "emailAddress": STATE.get("email", "bot@example.com"), "accountId": "5f0eval"})
        if re.search(r"/rest/api/[23]/project$", path) or path.endswith("/project/search"):
            listing = [{"key": project["key"], "name": project["name"], "id": "10000"}]
            return self.reply(200, {"values": listing, "total": 1} if path.endswith("/search") else listing)
        if m := re.search(r"/rest/api/[23]/project/([A-Za-z]+)$", path):
            if m.group(1).upper() != project["key"]:
                return self.reply(404, {"errorMessages": ["No project could be found with key '%s'." % m.group(1)]})
            types = [{"id": str(i), "name": n, "subtask": n == "Subtarea"} for i, n in enumerate(project["issue_types"], 1)]
            return self.reply(200, {"key": project["key"], "name": project["name"], "id": "10000", "issueTypes": types})
        if "createmeta" in path:
            types = [{"id": str(i), "name": n, "subtask": n == "Subtarea"} for i, n in enumerate(project["issue_types"], 1)]
            return self.reply(200, {"projects": [{"key": project["key"], "issuetypes": types}], "issueTypes": types, "values": types})
        if re.search(r"/search(/jql)?$", path):
            jql = q.get("jql", "")
            if raw:
                try:
                    jql = json.loads(raw).get("jql", jql)
                except json.JSONDecodeError:
                    pass
            return self.reply(200, search(jql, base))
        if m := re.search(r"/issue/([A-Z]+-\d+)(/[a-z]+)?$", path):
            issue = next((i for i in STATE["issues"] if i["key"] == m.group(1)), None)
            if issue is None:
                return self.reply(404, {"errorMessages": ["La incidencia no existe o no tiene permiso para verla."]})
            sub = m.group(2)
            if sub == "/transitions":
                return self.reply(200, {"transitions": [{"id": t["id"], "name": t["name"], "to": {"name": t["to"]}}
                                                         for t in issue.get("transitions", [])]})
            if sub == "/remotelink":
                return self.reply(200, issue.get("remotelinks", []))
            if sub == "/comment":
                return self.reply(200, {"comments": [], "total": 0})
            return self.reply(200, issue_json(issue, base))
        if path.endswith("/rest/agile/1.0/board"):
            return self.reply(200, {"values": STATE.get("boards", []), "total": len(STATE.get("boards", []))})
        if m := re.search(r"/rest/agile/1.0/board/(\d+)/sprint$", path):
            sprints = [s for s in STATE.get("sprints", []) if not q.get("state") or s["state"] in q["state"].split(",")]
            return self.reply(200, {"values": sprints, "isLast": True})
        return self.reply(404, {"errorMessages": [f"fake jira: unsupported {method} {url.path}"]})

    def do_GET(self):
        self.handle_any("GET")

    def do_POST(self):
        self.handle_any("POST")

    def do_PUT(self):
        self.handle_any("PUT")

    def do_DELETE(self):
        self.handle_any("DELETE")


def watchdog(server: ThreadingHTTPServer, lifetime: int) -> None:
    start = time.time()
    while time.time() - start < lifetime and (ROOT / "repo").exists():
        time.sleep(5)
    server.shutdown()


if __name__ == "__main__":
    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    (ROOT / "jira-port").write_text(str(server.server_address[1]))
    threading.Thread(target=watchdog, args=(server, STATE.get("lifetime", 1100)), daemon=True).start()
    server.serve_forever()
