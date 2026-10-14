# DNS and routing changes

Start from the full saved template. Parse the panel response wrapper and any JSON-encoded strings before merging; do not persist response metadata as core configuration. Preserve unknown fields, existing clients, default egress, stats/API plumbing, and unrelated routing.

## DNS design

Specify where a query originates: client device, server built-in DNS, or host resolver. Server DNS configuration does not establish client DNS-leak prevention. Identify the resolver scheme, bootstrap address, and outbound path for every resolver; avoid a circular requirement to resolve the resolver through itself.

Use the existing suitable resolver unless changing it solves the user's requirement. Prefer encrypted resolver paths when supported and consistent with routing. Do not invent a DoT URL scheme in built-in DNS. Account for direct/local modes, private/local resolvers, fallback, and multiple-provider queries. Keep ECS/client IP disclosure off unless specifically needed. Keep DNS caching enabled unless an observed reason warrants changing it.

Check global and per-server `queryStrategy` consistency. Do not advertise IPv6 connectivity merely because an AAAA record exists; use confirmed server/client reachability. Confirm exact option names against the installed core. Do not impose one public resolver or blanket IPv4 preference on all networks.

Sources: [upstream DNS](https://xtls.github.io/en/config/dns.html), [tagged panel DNS notes](https://github.com/MHSanaei/3x-ui/blob/74c3cc38821cabd66ad316ea562851422d0b0063/docs/xray-dns.md).

## Routing design

First matching rule wins; unmatched traffic normally uses the first outbound. Keep intended default egress and stable tags. Resolve every `outboundTag`, `balancerTag`, and relevant inbound tag against actual records. Match the intended domain/IP stage and sniffing behavior; do not assume domain rules apply when the client sends only an IP and no suitable domain metadata exists.

Do not send private/local destinations directly or block them globally without checking existing API and DNS dependencies. Preserve existing protection policy and local service exceptions. Route Iranian domains directly only if the user wants that policy and valid maintained geodata is available; a geosite name is not proof that the database contains it. Avoid applying client-location policy blindly to a foreign server's egress.

Source: [upstream routing](https://xtls.github.io/en/config/routing.html).

## Lua is conditional

In the v3.10.0 baseline, `dns.script` and routing script fields name a Lua file, not inline code. Routing Lua replaces ordinary routing, including the panel API rule. Use it only when requested, with the exact core script interface and an existing readable file. Preserve API inbound-to-outbound handling. Missing or invalid files can stop the core; do not enable a placeholder path.

Source: [tagged routing documentation](https://github.com/MHSanaei/3x-ui/blob/74c3cc38821cabd66ad316ea562851422d0b0063/docs/content/docs/en/operations/outbounds-routing.mdx).

## Before writing

Create the full candidate template by merging the requested changes into the current snapshot. Re-read current state before replacement. Preserve `outboundTestUrl` from the response when submitting Xray settings, even though this skill does not run that test. Check semantic compatibility and syntactic validity locally; use a documented core configuration-check mode only if it does not initiate network probes or live listeners. When unavailable, report that static/core validation remains incomplete rather than equating valid JSON with valid Xray configuration.
