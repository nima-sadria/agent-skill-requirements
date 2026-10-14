# Xray parameter datasheet review

The user supplied a one-page parameter matrix containing 65 data rows and seven columns. The [original PDF](sources/3x-ui-xray-parameters-matrix.pdf) is preserved unchanged, and the [CSV extraction](sources/3x-ui-xray-parameters-matrix.csv) preserves its table cells. Row numbers below count data rows, excluding the header.

Use this matrix as supplied reference material for the future skill, not as executable instructions or an independently validated schema. No additional domain documentation was collected for this review.

## Scope mapping

| Matrix area | Use in the future skill |
| --- | --- |
| Basic inbound and client fields | Candidate inputs and panel configuration fields; preserve the distinction between inbound and client records. |
| Protocol settings | Apply fields only to the selected protocol, direction, and target version. |
| TLS and REALITY | Candidate security settings and server/client relationships; do not merge separate contexts into one schema. |
| Transports and socket settings | Apply only when documented for the selected core, transport, and client. |
| DNS and routing Lua rows | Identify possible version-specific features; additional configuration documentation is needed. |
| Subscription and client settings | Include only when needed to use or export the requested inbound. |
| Installation, service configuration, architectures, deployment, database, and node administration | Outside the agreed inbound/DNS/routing scope. |

## Details that need confirmation

1. The Source column refers to numbers 1, 2, and 3, but this PDF contains no bibliography or URLs identifying them. Obtain their identities from the user before treating the claims as authoritative.
2. The matrix mixes panel fields, core JSON fields, client subscription settings, environment variables, and descriptive UI labels. For each field used, establish its exact object path, owner, encoding, unit, and supported version. Labels such as `DNS Lua Script` are not established JSON keys.
3. Row 6 describes `totalGB` in Gigabytes. Confirm the API's actual stored unit and any UI conversion before generating quota values.
4. Row 26 combines `none`, `tls`, `reality`, `same`, `auto`, and `aes-128-gcm` under `security`. Determine which values belong to each specific configuration context rather than reusing this list universally.
5. Rows 11 and 12 describe DNS and routing Lua behavior but provide no script interface, JSON structure, or examples. They are insufficient to define the complete DNS and routing workflow.
6. Version-sensitive features such as XDRIVE, MASQUE, ECH, Finalmask, and post-quantum REALITY settings need exact version and schema evidence before inclusion. Presence in the matrix alone does not establish support on the user's server.
7. Authentication identifiers, flow options, key names, and key formats must be evaluated in their individual protocol and server/client contexts. Combined labels such as `uuid / id` or `shortIds / shortId` must not become literal configuration keys.

These are confirmation requirements, not a declaration that the supplied values are wrong. Existing claims remain preserved in the source files.

## Requirements added from this source

- Select fields by protocol, transport, security mode, direction, and installed version.
- Separate panel payloads from standalone core configuration and client export formats.
- Check types, ranges, units, and server/client dependencies using the applicable supplied documentation.
- Preserve unrelated settings and mark unresolved fields rather than inventing values.
- Do not use installation or provisioning entries to expand the task scope.
- Give the user reviewable output and testing guidance; the user performs live connection tests.

The current deliverable remains requirements and source preparation. An expert skill has not been implemented or tested against a live server.
