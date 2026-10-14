# Revise from user-run connection tests

The agent checks configuration readback and core state. The user tests end-to-end connectivity. Ask for the profile used, client/core version, network/ISP, approximate time, error message, and a short redacted client/server log excerpt. Do not request share links or private keys in public logs.

| Evidence | Next inspection |
| --- | --- |
| API rejected a request | Authentication, exact versioned route/body, field validation, port ownership; do not create again blindly. |
| API reported success but state differs | Read affected records and template; check normalization, ignored client/enable fields, and partial writes. |
| Core stopped or reports config error | Last valid snapshot, unsupported field/combination, missing key/certificate/Lua file, unresolved tag; stop further changes. |
| Direct connection times out | Endpoint/address/port and user-reported origin reachability; DNS and IPv6 selection before assuming DPI. |
| TLS/REALITY authentication fails | Key role, client identity/flow, SNI, short ID, versions, time skew, target prerequisite. |
| CDN returns 403/404 or upgrade fails | Host/path/service name, WAF/Access/redirect behavior, WebSockets/gRPC requirements, origin mapping. |
| Connection works but names fail | Resolver bootstrap, route loops, local-mode path, global/per-server address-family conflicts. |
| Some destinations or apps fail | Rule ordering/default outbound, sniffing/domain availability, UDP behavior, geodata, MTU evidence supplied by user. |

Separate an ISP-specific failure from an invalid server/client configuration using the evidence available. Do not announce DPI as the cause solely from a timeout. Propose one targeted change with its expected observation; preserve a working alternative.

If a write fails or times out, reconcile state before retrying. If the panel saved a template but failed to apply it, report both facts. Restore only the affected settings from the snapshot when needed for the authorized repair; do not overwrite newer unrelated edits or assume one inbound update restores client identity and enable state. Tell the user which changes succeeded, which remain, and which test should be repeated.
