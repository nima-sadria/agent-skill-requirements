# Detailed requirements for inbound and Xray configuration

Create reviewable inbound, DNS, and routing configuration for an existing Ubuntu-hosted 3X-UI installation. These requirements define the [xray-inbound-expert skill](../skills/xray-inbound-expert/SKILL.md) using the [expertise scope](../EXPERTISE.md) and [registered sources](SOURCES.md).

## Inputs and output format

Obtain the panel version, actual Xray-core version, relevant client application/core version, current redacted configuration, and desired behavior. Do not assume that the server runs the versions described by the supplied architecture brief.

Choose an output format appropriate to the request: panel fields, panel API payload, standalone core JSON, or client configuration. Label that format and preserve its documented nesting, encoding, and units. An inbound fragment must be identified as a fragment rather than a complete core configuration.

Provide only the necessary missing-input questions. Keep secrets out of tracked examples. Use clearly marked placeholders in drafts, and identify unresolved values before describing any output as ready to apply. Validate strict JSON outputs without comments or unresolved template markers.

## Inbound and client consistency

- Select settings according to the actual protocol, transport, security mode, and version.
- Distinguish client records from inbound settings and distinguish server keys from client public-key parameters.
- Keep applicable identifiers, flow, SNI, short IDs, transport, and security consistent across server and client outputs.
- Do not infer one universal security enumeration from the matrix's combined contexts.
- Preserve existing clients and unrelated fields in an update. Include a precise description of the proposed changes.
- Verify quota units from serialization and implementation before converting a UI amount into `totalGB` or another stored value. The tagged OpenAPI describes GB in one schema and presents a byte-scale example in another, so the schema description alone does not resolve this.

The [REALITY upstream example](https://github.com/XTLS/REALITY) defines separate inbound and outbound objects. Use it for those relationships, subject to the actual core version; do not copy it into the panel API without verifying the panel representation.

## DNS requirements

Define resolver addresses and schemes, hostname bootstrap, IPv4/IPv6 preferences, cache/fallback behavior, and how resolver traffic reaches its destination. Change only the fields needed for the user's requested behavior.

Check for resolver routing loops and distinguish resolution on the server from resolution on the client. Explain how local-mode resolvers or the host resolver affect the intended path. Do not add resolver providers, ECS/client IP data, or broad fallback behavior without a reason in the requested configuration. The [versioned DNS notes](https://github.com/MHSanaei/3x-ui/blob/74c3cc38821cabd66ad316ea562851422d0b0063/docs/xray-dns.md) describe these path and privacy considerations.

## Routing requirements

Check ordered rule matching, the default outbound, inbound/outbound tags, balancer references if used, and any DNS/sniffing behavior on which a rule depends. Preserve panel-owned routing and API entries.

In the [v3.10.0 routing documentation](https://github.com/MHSanaei/3x-ui/blob/74c3cc38821cabd66ad316ea562851422d0b0063/docs/content/docs/en/operations/outbounds-routing.mdx), Lua inputs are paths to files defining `HandleRoute` or `HandleDNSQuery`. A routing script replaces ordinary rules, including the panel's internal API rule. Therefore:

- Do not put raw Lua code into a path field.
- Do not introduce a routing script as a default substitute for static rules.
- When requested and supported, preserve the API inbound-to-outbound path inside the script.
- Identify the required file location and existence as prerequisites; do not represent an absent file as a working configuration.
- Require the exact core Lua interface before generating executable script logic. A function name alone is insufficient.

## Panel API requirements

Use the applicable versioned API schema and verify payload normalization in the panel implementation where examples are ambiguous. The [tagged OpenAPI](https://github.com/MHSanaei/3x-ui/blob/74c3cc38821cabd66ad316ea562851422d0b0063/docs/public/openapi.json) documents inbound add/update routes and a form-encoded Xray settings update with the full template in `xraySetting`. Do not send a partial DNS or routing fragment as the full template.

Some inbound examples use broad object schemas and illustrative values. The presence of an endpoint and example does not validate every nested core field or prove the same payload works on another version. In particular, resolve example differences such as `dest` versus the upstream REALITY `target` before choosing a field.

The skill can apply configuration through the API when the user's active request authorizes that work. Generating a draft alone does not authorize a live write. Snapshot affected state, prepare the concrete change, preserve the current `outboundTestUrl`, and read back results. A panel update can apply or restart the running core. End-to-end connectivity tests remain with the user.

In the v3.10.0 baseline, the template inspection route is `POST /panel/api/xray/`; response objects may contain JSON-encoded wrappers. The inbound update route ignores body clients and enable state, so manage those through the documented client and enable endpoints when requested. These distinctions are encoded in the skill's [API workflow](../skills/xray-inbound-expert/references/api.md).

## Version dependent features and boundaries

The [v3.10.0 release](https://github.com/MHSanaei/3x-ui/releases/tag/v3.10.0) documents MASQUE, XDRIVE, and Lua-related additions. Their inclusion in the source document is not a request to enable them. Use advanced features only when relevant, with their full schema and server/client compatibility established. Keep systemd, database, installation, fleet administration, and web-server provisioning material outside this skill's scope.

Do not turn the supplied document's claims about defeating DPI into acceptance criteria. Connectivity under Iranian filtering is assessed from user-supplied results for the actual network and configuration.

## Observable acceptance cases

| Case | Expected behavior |
| --- | --- |
| Create an inbound with complete inputs | Produce the selected output format with matching server/client parameters and version evidence. |
| Modify DNS or routing in an existing template | Preserve unrelated fields and internal panel paths; identify the changed fields. |
| Requested feature requires an unverified version | Identify the compatibility gap instead of silently introducing unsupported fields. |
| Lua routing requested | Use a file path, preserve the API route, and obtain the actual Lua interface before generating logic. |
| Required version or parameter is missing | Request the necessary information or deliver a clearly incomplete draft. |
| User asks for panel installation | Explain that this skill covers configuration and does not perform installation. |
| User reports a failed connection | Revise from the supplied evidence and state what the next user-run check would establish. |

Package and static checks may be performed during implementation. The user performs live connection tests; record those results separately from agent discovery and package validation.
