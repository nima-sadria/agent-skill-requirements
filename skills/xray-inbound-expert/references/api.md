# Applying reviewed configuration through the API

The Python helper sends requests over verified HTTPS, or HTTP on loopback for a local panel/SSH tunnel. It supports a locally supplied Bearer token or existing session cookie plus CSRF token. It does not log in, create credentials, install software, bypass certificate validation, or retry requests. A trusted private CA can be supplied with `--ca-file`.

Store `XUI_SKILL_BASE_URL` and **one** of `XUI_SKILL_BEARER` or `XUI_SKILL_COOKIE` using the agent's credential facility or a local protected environment; for cookie POST requests also supply `XUI_SKILL_CSRF`. Do not put values into chat, tracked files, command arguments, or shell history. The base URL includes the panel's custom path, for example `https://panel.example.com/custom-base`. The helper appends `/panel/api/...` without dropping that prefix.

## Discover and snapshot

Use an authorized endpoint/schema for the actual version. These are baseline v3.10.0 routes:

| Request | Purpose |
| --- | --- |
| `GET /panel/api/openapi.json` | Installed panel schema. |
| `GET /panel/api/server/status` | Core state/version; panel version may need another documented source. |
| `GET /panel/api/inbounds/list` | Existing listeners and client data; snapshot privately. |
| `GET /panel/api/inbounds/get/{id}` | Affected inbound detail. |
| `POST /panel/api/xray/` | Saved template and metadata; inspection endpoint despite POST method. |

The template-read handler can normalize legacy wrapped storage in this baseline. It is intended for inspection, not a connection test; do not promise that it is strictly side-effect-free on malformed old storage. Read `obj`, then parse a JSON-encoded wrapper if necessary, then read/parse `xraySetting`. Preserve `outboundTestUrl` separately. Avoid nesting this wrapper inside the core template.

```sh
python3 scripts/panel_api.py --path /panel/api/openapi.json
python3 scripts/panel_api.py --path /panel/api/inbounds/list --out /private/run/inbounds-before.json
python3 scripts/panel_api.py --method POST --path /panel/api/xray/ --out /private/run/xray-before.json
```

Run from the installed skill directory or use the absolute script path. Output directories must already exist with restricted access. On Ubuntu, a suitable snapshot location is a directory under `~/.local/state/xray-inbound-expert/` created with owner-only permissions. Output files are new and mode 0600 on POSIX; on Windows use a directory with appropriate account ACLs. Raw snapshots and share links contain credentials. Default console output is redacted, but it is not a complete secret scanner; do not publish panel responses.

## Write contracts

| Baseline request | Contract |
| --- | --- |
| `POST /panel/api/inbounds/add` | Full reviewed JSON inbound body. Nested settings/stream/sniffing objects are supported; legacy JSON strings are also accepted. |
| `POST /panel/api/inbounds/update/{id}` | Replaces inbound configuration, retaining stored clients and enable state. Body clients/enable are ignored in this baseline. |
| `POST /panel/api/inbounds/setEnable/{id}` | Explicit enable-state change when requested. |
| `POST /panel/api/clients/add` and versioned client routes | Create/attach/manage identities. Consult exact schema; some multi-inbound client operations can partially succeed. |
| `POST /panel/api/xray/update` | Form fields: `xraySetting` is the serialized full template; retain existing `outboundTestUrl`. Saving can apply/reload/restart the running core. |

Sources: [tagged OpenAPI](https://github.com/MHSanaei/3x-ui/blob/74c3cc38821cabd66ad316ea562851422d0b0063/docs/public/openapi.json), [tagged controller](https://github.com/MHSanaei/3x-ui/blob/74c3cc38821cabd66ad316ea562851422d0b0063/internal/web/controller/xray_setting.go).

Prepare body files in the private run directory. For form writes, a JSON file maps each form key to its **string** value; serialize the candidate template once into the `xraySetting` value. The helper URL-encodes those strings. A standalone core inbound is not automatically a panel inbound payload.

```sh
# Preview the reviewed inbound without sending a write.
python3 scripts/panel_api.py --method POST --path /panel/api/inbounds/add --json-file /private/run/inbound.json
# Execute once when the user's task authorizes creation.
python3 scripts/panel_api.py --method POST --path /panel/api/inbounds/add --json-file /private/run/inbound.json --apply --out /private/run/inbound-result.json
# A reviewed full-template replacement uses a form body.
python3 scripts/panel_api.py --method POST --path /panel/api/xray/update --form-file /private/run/xray-form.json --apply --out /private/run/xray-result.json
```

`--apply` is a script switch for executing an already-authorized change, not a requirement to ask the user again. A preview is not validation of protocol semantics. The helper does not select protocols, merge templates, verify DNS/routing, perform rollback, or enforce all host authorization rules; the agent follows the skill workflow for those tasks.

## After a request

Check both HTTP status and the panel's `success` result. A failure or timeout may occur after some state was persisted. Re-read before repeating a create or batch operation. Do not treat `success:false` as transactional rollback. The helper saves an available failure response to the selected private file and exits nonzero.

Inspect affected persisted fields, client records, actual assigned IDs/keys, and core state. For a template replacement, compare the full before/after objects and explain panel normalization. If the update saved but failed to apply, stop and reconcile from snapshots rather than issuing more speculative changes. Configuration rollback must also handle independently managed client/enable state and preserve intervening edits.

The user's live connection test is separate from these administrative checks. Do not call outbound/route testing endpoints as a hidden verification step.
