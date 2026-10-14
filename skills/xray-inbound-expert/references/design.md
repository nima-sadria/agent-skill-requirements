# Protocol and transport selection

This is a conditional design policy, not a ranking of measured Iran performance. Validate the specific panel/core/client versions and existing infrastructure. Use one profile per useful architecture; several users may share an appropriate inbound with separate authentication identities.

## Candidate architectures

| Available path | Candidate | Conditions and tradeoffs |
| --- | --- | --- |
| Direct reachable origin and compatible clients | VLESS with raw/TCP, REALITY, and Vision | Requires a compatible core/client and a suitable REALITY target. It depends on direct origin reachability; the endpoint must bypass an ordinary HTTP CDN. |
| Existing TLS origin with orange-cloud hostname | VLESS over WebSocket with TLS | Requires a working HTTP upgrade path, matching Host/path, supported HTTPS port, valid origin TLS, and client support. Do not attach a raw-TCP Vision flow to WS. |
| Existing proxied HTTP/2 origin and enabled gRPC | VLESS over gRPC with TLS | Conditional alternative; check service name, origin ALPN/HTTP2, zone gRPC, and port 443. Do not assume all HTTP CDN paths support it. |
| Explicitly supported XHTTP origin, CDN mode, and client | VLESS over XHTTP with documented security/settings | Version and transport-mode specific. Verify current upstream guidance and the existing HTTP path; do not transplant settings from WS/gRPC or enable Vision by guesswork. |
| User-requested TLS protocol and compatible clients | Trojan or another documented protocol/transport | Require its actual authentication, TLS, and transport constraints. Avoid universal cipher or flow rules across protocols. |

These starting candidates are project choices. They do not imply every candidate works on the user's ISP, that a certificate exists, or that the requested port is free. Plain unauthenticated HTTP/SOCKS exposure is not a substitute for the requested secure client profile.

## Cloudflare constraints

An orange-cloud record sends traffic through Cloudflare's HTTP/HTTPS proxy; a DNS-only record resolves toward the origin. Inspect each hostname and CNAME chain. Cloudflare's standard HTTPS ports include 443, 2053, 2083, 2087, 2096, and 8443. Port availability alone does not make a non-HTTP protocol proxyable. Spectrum and other explicit relay architectures require their own confirmed capabilities; ordinary orange-cloud status does not imply them.

Sources: [proxy status](https://developers.cloudflare.com/dns/proxy-status/), [network ports](https://developers.cloudflare.com/fundamentals/reference/network-ports/).

Prefer the existing validated HTTPS origin path. Do not disable certificate verification to get a profile working. A Cloudflare Origin CA certificate is for the edge-to-origin hop, not automatically trusted by a client connecting directly to that origin. Distinguish client-to-edge SNI/certificate validation from edge-to-origin TLS.

Proxied WebSockets require a valid upgrade path and can be interrupted by edge changes/timeouts. Check the actual zone and origin settings. gRPC requires TLS, HTTP/2 advertised through ALPN, port 443, proxied hostname, and an enabled zone setting with at least Full SSL. Access, redirects, WAF challenges, and Tunnel routing can affect compatibility; verify the selected path rather than disabling protections globally.

Sources: [WebSockets](https://developers.cloudflare.com/network/websockets/), [gRPC](https://developers.cloudflare.com/network/grpc-connections/), [Origin CA](https://developers.cloudflare.com/ssl/origin-configuration/origin-ca/).

## REALITY and Vision invariants

Use the installed core's key-generation commands and match server private key to the client public-key field for that version. Keep client ID and compatible flow consistent. The selected client `serverName` must be allowed by server `serverNames`; `shortId` must be in the configured `shortIds` with the documented hex format. A UUID, a key pair, and a short ID are different values.

Keep `target`/legacy `dest` spelling version-specific. Use the upstream target-selection criteria and avoid assuming an arbitrary famous domain is valid. Do not perform target or user-path connection tests when the user has retained that work; identify checks for the user. A "steal oneself" design needs an existing suitable local TLS origin, domain/certificate correspondence, and no listener loop. Do not install Nginx/Caddy/ACME to create that prerequisite within this skill.

Vision is not a switch to enable on every transport. Follow actual core/panel restrictions, including newer VLESS encryption behavior, instead of treating the matrix's flow list as universal.

Source: [upstream REALITY example](https://github.com/XTLS/REALITY), [3X-UI v3.10.0 release](https://github.com/MHSanaei/3x-ui/releases/tag/v3.10.0).

## Capacity and identity

Check socket binding by address, TCP/UDP, and existing processes. Do not create multiple listeners on the same conflicting address/port. Reuse an existing compatible inbound for additional clients when requested. Keep independent identities distinct; reuse credentials across alternative profiles only when that is the user's intended account model and the panel supports it. Quotas, expiry, and subscription IDs must follow the documented units and semantics.

Do not add masks, UDP hopping, post-quantum options, Lua, MASQUE, or XDRIVE solely because they are recent. Require a concrete benefit, exact schema, and matching client support. Keep a simpler viable profile when an advanced path has unmet prerequisites.
