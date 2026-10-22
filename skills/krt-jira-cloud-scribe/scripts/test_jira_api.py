#!/usr/bin/env python3
"""jira_api.py loads the checkout env, authenticates, and keeps the token out of output."""

from __future__ import annotations

import base64
import json
import subprocess
import sys
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent / "jira_api.py"
TOKEN = "tok-" "secret-123"
ENV_FILE = ".krt/env/jira-cloud-scribe.env"
EXPECTED_AUTH = "Basic " + base64.b64encode(f"bot@example.com:{TOKEN}".encode()).decode()


def env_text(host: str) -> str:
    return f"JIRA_CLOUD_HOST={host}\nJIRA_CLOUD_EMAIL=bot@example.com\nJIRA_CLOUD_PROJECT_KEY=PDP\nJIRA_CLOUD_API_TOKEN={TOKEN}\n"


class Handler(BaseHTTPRequestHandler):
    seen: list[dict] = []

    def log_message(self, *args):
        pass

    def _reply(self):
        length = int(self.headers.get("Content-Length") or 0)
        body = self.rfile.read(length).decode() if length else ""
        Handler.seen.append({"method": self.command, "path": self.path, "auth": self.headers.get("Authorization"), "body": body})
        ok = self.headers.get("Authorization") == EXPECTED_AUTH
        payload = json.dumps({"ok": ok}).encode()
        self.send_response(200 if ok else 401)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(payload)

    do_GET = do_POST = _reply


class JiraApiTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = HTTPServer(("127.0.0.1", 0), Handler)
        threading.Thread(target=cls.server.serve_forever, daemon=True).start()
        cls.host = f"http://127.0.0.1:{cls.server.server_address[1]}/"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()

    def run_script(self, root: Path, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run([sys.executable, str(SCRIPT), "--root", str(root), *args], capture_output=True, text=True)

    def test_authenticated_get_with_query_and_no_token_in_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ENV_FILE).parent.mkdir(parents=True)
            (root / ENV_FILE).write_text(env_text(self.host))
            result = self.run_script(root, "GET", "/rest/api/3/search", "--query", 'jql=project = PDP AND summary ~ "exportación"')
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual(json.loads(result.stdout)["status"], 200)
            self.assertNotIn(TOKEN, result.stdout + result.stderr)
            self.assertIn("jql=project+%3D+PDP", Handler.seen[-1]["path"])

    def test_post_sends_json_body(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ENV_FILE).parent.mkdir(parents=True)
            (root / ENV_FILE).write_text(env_text(self.host))
            result = self.run_script(root, "POST", "/rest/api/3/issue/PDP-1/transitions", "--data", '{"transition":{"id":"31"}}')
            self.assertEqual(result.returncode, 0)
            self.assertEqual(json.loads(Handler.seen[-1]["body"]), {"transition": {"id": "31"}})

    def test_missing_env_file_reports_path_and_exits_2(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = self.run_script(Path(tmp), "GET", "/rest/api/3/myself")
            self.assertEqual(result.returncode, 2)
            self.assertEqual(json.loads(result.stdout)["secret_path"], ENV_FILE)

    def test_http_error_exits_1(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ENV_FILE).parent.mkdir(parents=True)
            (root / ENV_FILE).write_text(env_text(self.host).replace(TOKEN, "wrong"))
            result = self.run_script(root, "GET", "/rest/api/3/myself")
            self.assertEqual(result.returncode, 1)
            self.assertEqual(json.loads(result.stdout)["status"], 401)


if __name__ == "__main__":
    unittest.main()
