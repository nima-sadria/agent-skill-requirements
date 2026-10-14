"""Exercise the helper against a local fake panel; never contact a real server."""

import contextlib
import importlib.util
import io
import json
import os
import tempfile
import threading
import unittest
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from unittest.mock import patch


SCRIPT = Path(__file__).resolve().parents[1] / "skills/xray-inbound-expert/scripts/panel_api.py"
spec = importlib.util.spec_from_file_location("panel_api", SCRIPT)
api = importlib.util.module_from_spec(spec)
spec.loader.exec_module(api)


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def handle_request(self):
        body = self.rfile.read(int(self.headers.get("Content-Length", "0")))
        self.server.calls.append((self.command, self.path, dict(self.headers), body))
        status, payload, headers = self.server.reply
        self.send_response(status)
        for key, value in headers.items():
            self.send_header(key, value)
        self.end_headers()
        self.wfile.write(payload)

    do_GET = handle_request
    do_POST = handle_request


class PanelApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base = f"http://127.0.0.1:{cls.server.server_port}/custom-panel"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()

    def setUp(self):
        self.server.calls = []
        self.reply({"success": True, "obj": {"id": 7}})
        self.tmp = tempfile.TemporaryDirectory(prefix="panel api test ")
        self.root = Path(self.tmp.name)
        self.environment = patch.dict(os.environ, {
            "XUI_SKILL_BASE_URL": self.base, "XUI_SKILL_BEARER": "local-test-token",
            "XUI_SKILL_COOKIE": "", "XUI_SKILL_CSRF": "",
        })
        self.environment.start()

    def tearDown(self):
        self.environment.stop()
        self.tmp.cleanup()

    def reply(self, value, status=200, headers=None):
        self.server.reply = (status, json.dumps(value).encode(), headers or {})

    def bodyfile(self, value):
        file = self.root / "body with spaces.json"
        file.write_text(json.dumps(value), encoding="utf-8")
        return str(file)

    def run_main(self, *args):
        stdout, stderr = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            code = api.main(list(args))
        return code, stdout.getvalue(), stderr.getvalue()

    def test_read_preserves_base_path_and_auth(self):
        self.run_main("--path", "/panel/api/inbounds/list")
        method, path, headers, body = self.server.calls[0]
        self.assertEqual((method, path, body), ("GET", "/custom-panel/panel/api/inbounds/list", b""))
        self.assertEqual(headers["Authorization"], "Bearer local-test-token")

    def test_write_preview_makes_no_request_and_hides_credentials(self):
        code, output, _ = self.run_main("--method", "POST", "--path", "/panel/api/inbounds/add",
                                       "--json-file", self.bodyfile({"settings": {"clients": [{"id": "client-secret"}], "privateKey": "key-secret"}}))
        self.assertEqual(code, 0)
        self.assertFalse(self.server.calls)
        self.assertNotIn("client-secret", output)
        self.assertNotIn("key-secret", output)

    def test_authorized_json_write_is_sent_once(self):
        body = {"remark": "آزمایش", "port": 443, "settings": {"clients": []}}
        self.run_main("--method", "POST", "--path", "/panel/api/inbounds/add", "--json-file", self.bodyfile(body), "--apply")
        self.assertEqual(len(self.server.calls), 1)
        call = self.server.calls[0]
        self.assertEqual(json.loads(call[3]), body)
        self.assertEqual(call[2]["Content-Type"], "application/json")

    def test_form_write_preserves_full_template_and_test_url(self):
        template = {"dns": {"hosts": {"example.com": "192.0.2.1"}}, "routing": {"rules": []}, "outbounds": [{"tag": "direct"}]}
        form = {"xraySetting": json.dumps(template), "outboundTestUrl": "https://example.com/check?a=1&b=2"}
        self.run_main("--method", "POST", "--path", "/panel/api/xray/update", "--form-file", self.bodyfile(form), "--apply")
        sent = urllib.parse.parse_qs(self.server.calls[0][3].decode())
        self.assertEqual(json.loads(sent["xraySetting"][0]), template)
        self.assertEqual(sent["outboundTestUrl"], [form["outboundTestUrl"]])

    def test_post_template_read_decodes_nested_redaction_and_saves_raw_snapshot(self):
        value = {"success": True, "obj": json.dumps({"xraySetting": {"inbounds": [{"settings": {"privateKey": "snapshot-secret"}}]}})}
        self.reply(value)
        output_file = self.root / "snapshot.json"
        code, output, _ = self.run_main("--method", "POST", "--path", "/panel/api/xray/", "--out", str(output_file))
        self.assertEqual(code, 0)
        self.assertNotIn("snapshot-secret", output)
        self.assertEqual(json.loads(output_file.read_text(encoding="utf-8")), value)
        if os.name != "nt":
            self.assertEqual(output_file.stat().st_mode & 0o777, 0o600)

    def test_output_conflict_blocks_request_and_preserves_file(self):
        out = self.root / "snapshot.json"
        out.write_text("preserve", encoding="utf-8")
        with self.assertRaises(FileExistsError):
            self.run_main("--method", "POST", "--path", "/panel/api/inbounds/add", "--apply", "--out", str(out))
        self.assertFalse(self.server.calls)
        self.assertEqual(out.read_text(), "preserve")

    def test_panel_failure_returns_nonzero_without_retry_and_keeps_response(self):
        failure = {"success": False, "msg": "secret detail", "obj": {"completed": [7]}}
        self.reply(failure)
        out = self.root / "failure.json"
        code, output, err = self.run_main("--method", "POST", "--path", "/panel/api/clients/add", "--apply", "--out", str(out))
        self.assertEqual(code, 1)
        self.assertEqual(len(self.server.calls), 1)
        self.assertIn("partial changes", err.lower())
        self.assertNotIn("secret detail", output)
        self.assertEqual(json.loads(out.read_text()), failure)

    def test_cookie_post_requires_csrf_before_request(self):
        with patch.dict(os.environ, {"XUI_SKILL_BEARER": "", "XUI_SKILL_COOKIE": "session=local"}):
            with self.assertRaises(ValueError):
                self.run_main("--method", "POST", "--path", "/panel/api/xray/")
            self.assertFalse(self.server.calls)
            with patch.dict(os.environ, {"XUI_SKILL_CSRF": "local-csrf"}):
                self.run_main("--method", "POST", "--path", "/panel/api/xray/")
        self.assertEqual(self.server.calls[0][2]["X-Csrf-Token"], "local-csrf")

    def test_redirect_is_not_followed(self):
        self.reply({}, status=302, headers={"Location": self.base + "/different-origin"})
        with self.assertRaises(api.ApiError):
            self.run_main("--path", "/panel/api/inbounds/list")
        self.assertEqual(len(self.server.calls), 1)

    def test_http_failure_is_not_retried(self):
        self.reply({}, status=500)
        with self.assertRaises(api.ApiError):
            self.run_main("--method", "POST", "--path", "/panel/api/inbounds/add", "--apply")
        self.assertEqual(len(self.server.calls), 1)

    def test_invalid_response_removes_empty_reserved_output(self):
        self.server.reply = (200, b"<html>login required</html>", {})
        out = self.root / "snapshot.json"
        with self.assertRaises(api.ApiError):
            self.run_main("--path", "/panel/api/inbounds/list", "--out", str(out))
        self.assertFalse(out.exists())

    def test_unknown_json_response_is_not_success(self):
        self.reply({"unrecognized": True})
        with self.assertRaises(api.ApiError):
            self.run_main("--path", "/panel/api/inbounds/list")

    def test_schema_response_is_accepted(self):
        self.reply({"openapi": "3.0.3", "paths": {}})
        code, output, _ = self.run_main("--path", "/panel/api/openapi.json")
        self.assertEqual(code, 0)
        self.assertIn("3.0.3", output)

    def test_input_validation_prevents_network_requests(self):
        for content in ['{"port":443,"port":80}', '{"value":NaN}', '[]']:
            file = self.root / "bad.json"
            file.write_text(content, encoding="utf-8")
            with self.assertRaises(ValueError):
                self.run_main("--method", "POST", "--path", "/panel/api/inbounds/add", "--json-file", str(file), "--apply")
        self.assertFalse(self.server.calls)

    def test_url_constraints(self):
        for base, path in [
            ("http://remote.example.com", "/panel/api/inbounds/list"),
            ("https://user:secret@example.com", "/panel/api/inbounds/list"),
            ("https://example.com", "https://other.example.com/panel/api/inbounds/list"),
            ("https://example.com", "/panel/api/../../login"),
            ("https://example.com", "/panel/api/%2e%2e/login"),
        ]:
            with self.subTest(base=base, path=path), self.assertRaises(ValueError):
                api.request_url(base, path)

    def test_connectivity_endpoint_is_blocked(self):
        with self.assertRaises(SystemExit):
            self.run_main("--method", "POST", "--path", "/panel/api/xray/testOutbounds", "--apply")
        self.assertFalse(self.server.calls)


if __name__ == "__main__":
    unittest.main()
