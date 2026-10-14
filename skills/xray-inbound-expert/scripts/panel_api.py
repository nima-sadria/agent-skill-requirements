"""Send a reviewed 3X-UI API request; preview writes unless --apply is supplied."""

import argparse
import ipaddress
import json
import os
import ssl
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path


class ApiError(Exception):
    pass


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def strict_json(text):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError(f"Duplicate JSON key: {key}")
            result[key] = value
        return result

    def constant(value):
        raise ValueError(f"Invalid JSON constant: {value}")

    return json.loads(text, object_pairs_hook=pairs, parse_constant=constant)


def decode_nested(value):
    # Several panel response fields historically contain JSON-encoded strings.
    if isinstance(value, str) and value.lstrip().startswith(("{", "[")):
        try:
            return strict_json(value)
        except ValueError:
            pass
    return value


def redact(value):
    value = decode_nested(value)
    if isinstance(value, list):
        return [redact(item) for item in value]
    if isinstance(value, dict):
        result = {}
        for key, item in value.items():
            name = key.lower().replace("_", "").replace("-", "")
            if any(part in name for part in ("password", "secret", "token", "privatekey", "cookie")) or name in {
                "uuid", "subid", "shortid", "shortids", "email", "auth", "publickey", "mldsa65seed",
                "mldsa65verify", "presharedkey", "links", "link", "msg", "url", "spiderx",
            } or (name == "id" and isinstance(item, str)):
                result[key] = "[redacted]"
            elif isinstance(item, str) and "://" in item:
                result[key] = "[URL omitted]"
            elif name in {"obj", "settings", "streamsettings", "xraysetting"} and isinstance(decode_nested(item), str):
                result[key] = "[text payload omitted]"
            else:
                result[key] = redact(item)
        return result
    if isinstance(value, str) and "://" in value:
        return "[URL omitted]"
    return value


def loopback(host):
    if host == "localhost":
        return True
    try:
        return ipaddress.ip_address(host).is_loopback
    except ValueError:
        return False


def request_url(base, path):
    panel = urllib.parse.urlsplit(base)
    if panel.scheme not in ("http", "https") or not panel.hostname:
        raise ValueError("Set an http(s) panel base URL, including its custom base path")
    if panel.username or panel.password or panel.query or panel.fragment:
        raise ValueError("Base URL must not contain credentials, query parameters, or a fragment")
    if panel.scheme == "http" and not loopback(panel.hostname):
        raise ValueError("Use HTTPS for a remote panel, or HTTP through a loopback SSH tunnel")
    route = urllib.parse.urlsplit(path)
    decoded = urllib.parse.unquote(route.path)
    if route.scheme or route.netloc or route.fragment or not route.path.startswith("/panel/api/"):
        raise ValueError("Path must be a relative /panel/api/ route")
    if "\\" in decoded or "//" in decoded or any(p in (".", "..") for p in decoded.split("/")):
        raise ValueError("Path traversal is not a panel API route")
    return base.rstrip("/") + path


def build_body(json_file, form_file):
    path = json_file or form_file
    if path is None:
        return None, None
    value = strict_json(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("Request body file must contain a JSON object")
    if json_file:
        return json.dumps(value, ensure_ascii=False, allow_nan=False).encode("utf-8"), "application/json"
    if any(not isinstance(item, str) for item in value.values()):
        raise ValueError("Form values must be strings; serialize the full template into xraySetting")
    return urllib.parse.urlencode(value).encode("utf-8"), "application/x-www-form-urlencoded"


def call_api(url, method, body, content_type, token, cookie, csrf, timeout, ca_file):
    if bool(token) == bool(cookie):
        raise ValueError("Supply exactly one local Bearer token or session cookie")
    headers = {"Accept": "application/json"}
    if token:
        headers["Authorization"] = "Bearer " + token
    else:
        headers["Cookie"] = cookie
        if method != "GET":
            if not csrf:
                raise ValueError("Cookie-authenticated POST requires the local CSRF token")
            headers["X-CSRF-Token"] = csrf
    if content_type:
        headers["Content-Type"] = content_type
    context = ssl.create_default_context(cafile=str(ca_file) if ca_file else None)
    # No redirects or retries: credentials stay on the selected origin, and an
    # ambiguous create cannot be duplicated automatically.
    opener = urllib.request.build_opener(NoRedirect(), urllib.request.HTTPSHandler(context=context))
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with opener.open(req, timeout=timeout) as response:
            raw = response.read(32 * 1024 * 1024 + 1)
    except urllib.error.HTTPError as error:
        raise ApiError(f"HTTP {error.code}; inspect authentication/path or reconcile state before retrying a write") from None
    except (urllib.error.URLError, TimeoutError, OSError):
        raise ApiError("Request did not complete; a write may have applied. Read state before retrying") from None
    if len(raw) > 32 * 1024 * 1024:
        raise ApiError("Response exceeded 32 MiB; use a smaller read and reconcile any write")
    try:
        result = strict_json(raw.decode("utf-8"))
    except (ValueError, UnicodeError):
        raise ApiError("Response was not valid JSON; check panel base path/session and reconcile any write") from None
    if not isinstance(result, dict) or not (isinstance(result.get("success"), bool) or "openapi" in result):
        raise ApiError("Unrecognized API response; inspect the exact version and reconcile any write")
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default=os.environ.get("XUI_SKILL_BASE_URL"))
    parser.add_argument("--method", choices=("GET", "POST"), default="GET")
    parser.add_argument("--path", required=True, help="Relative route including /panel/api/, with optional query")
    body = parser.add_mutually_exclusive_group()
    body.add_argument("--json-file", type=Path, help="Reviewed JSON request body")
    body.add_argument("--form-file", type=Path, help="JSON object of string form values")
    parser.add_argument("--apply", action="store_true", help="Execute an authorized write instead of previewing it")
    parser.add_argument("--out", type=Path, help="Save the unredacted response in a new private file; never overwrite")
    parser.add_argument("--ca-file", type=Path, help="Trusted CA bundle for a private panel certificate")
    parser.add_argument("--timeout", type=float, default=20)
    args = parser.parse_args(argv)
    if not args.base_url:
        parser.error("Set XUI_SKILL_BASE_URL or --base-url")
    if args.timeout <= 0:
        parser.error("--timeout must be positive")
    url = request_url(args.base_url, args.path)
    payload, content_type = build_body(args.json_file, args.form_file)
    if args.method == "GET" and payload is not None:
        parser.error("GET requests cannot have a body")
    route = urllib.parse.urlsplit(args.path).path
    if any(term in route.lower() for term in ("testoutbound", "testroute", "routetest")):
        parser.error("The user runs connectivity tests; this helper does not call these test endpoints")
    read = args.method == "GET" or (args.method == "POST" and route == "/panel/api/xray/")
    if not read and not args.apply:
        print(json.dumps({"preview": True, "method": args.method, "path": args.path,
                          "content_type": content_type, "body": redact(strict_json(payload.decode()) if content_type == "application/json" else dict(urllib.parse.parse_qsl(payload.decode()))) if payload else None}, ensure_ascii=False, indent=2))
        return 0

    # Reserve the output before any request so an output conflict cannot follow
    # a successful write. Parent directories must already be private/existing.
    output = None
    try:
        if args.out:
            fd = os.open(args.out, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            output = os.fdopen(fd, "w", encoding="utf-8")
        result = call_api(url, args.method, payload, content_type,
                          os.environ.get("XUI_SKILL_BEARER"), os.environ.get("XUI_SKILL_COOKIE"),
                          os.environ.get("XUI_SKILL_CSRF"), args.timeout, args.ca_file)
        if output:
            json.dump(result, output, ensure_ascii=False, indent=2, allow_nan=False)
            output.close()
            output = None
            print("Unredacted response saved to the requested private file.")
        print(json.dumps(redact(result), ensure_ascii=False, indent=2, allow_nan=False))
        if result.get("success") is False:
            print("Panel reported failure; partial changes are possible. Reconcile state before another write.", file=sys.stderr)
            return 1
        return 0
    except Exception:
        if output:
            output.close()
            args.out.unlink()
        raise


if __name__ == "__main__":
    try:
        sys.exit(main())
    except ApiError as error:
        print(str(error), file=sys.stderr)
        sys.exit(1)
    except (ValueError, OSError):
        # Avoid printing errors that could embed request data, tokens or paths.
        print("API request failed or local input/output is invalid. Check the reviewed inputs and read state before retrying a write.", file=sys.stderr)
        sys.exit(1)
