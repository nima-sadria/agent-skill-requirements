# Expertise requirements for Xray configuration

The [xray-inbound-expert skill](skills/xray-inbound-expert/SKILL.md) creates inbounds and configures Xray for an existing Ubuntu-hosted 3X-UI environment through the panel API, including DNS and routing. Its goal is to produce configurations suitable for the user's connectivity needs under Iranian filtering and DPI conditions. The user supplies infrastructure details and performs connection tests.

## Included tasks

- Create inbound configurations compatible with the installed 3X-UI and Xray versions.
- Configure Xray DNS and routing according to the user's requirements and supplied documentation.
- Keep related server and client parameters consistent when client settings are needed to use the inbound.
- Explain required inputs, resulting changes, and how the user can check the configuration.
- Revise the configuration using test results supplied by the user.
- Ask for each domain's Cloudflare orange-cloud or DNS-only state, client compatibility, and desired number of profiles versus users/listeners.
- Apply authorized configuration changes through the existing panel API, snapshot affected state, and verify persisted settings and core process state.

Protocol and transport coverage will be defined by the user's documentation. Do not assume a fixed protocol list from the voice transcript.

## Excluded tasks

- Installing, reinstalling, or upgrading 3X-UI or Xray.
- Provisioning servers or changing operating system, firewall, SSH, or hosting settings.
- Running connection tests on behalf of the user.
- Changing Cloudflare records, provisioning web servers, or issuing certificates as an implicit side effect of creating an inbound.

## Required inputs for the future skill

Request only information needed for the particular configuration: installed panel and core versions, selected protocol and transport, relevant existing settings, desired DNS and routing behavior, and required client compatibility. Domain, address, port, and certificate or REALITY parameters depend on the selected configuration.

Use redacted examples for existing settings. Do not require passwords or private keys in chat or commit them to the repository. If a necessary detail is absent, identify it instead of inventing a working value.

## Expected outputs

Produce the appropriate inbound payload or panel field instructions and the relevant Xray DNS or routing configuration. Distinguish a panel API payload from a standalone Xray configuration; choose the actual output format after the user provides documentation and preferences.

Preserve unrelated settings. Explain parameter dependencies, any assumptions, and the checks the user should perform. Treat effectiveness against filtering as dependent on the user's network and test results, rather than a guaranteed property.

## Acceptance criteria

- The package installs for Codex, Antigravity, and Claude Code through the shared installer; other Agent Skills hosts can use a custom destination.
- Instructions and generated configuration follow the supplied documentation and target versions.
- Generated fields and references are internally consistent, and unrelated configuration is preserved.
- The skill does not install software, provision servers, or run live connection tests.
- The user can review the output and provide test results for a subsequent revision.
- Compatibility checks and user connection tests are reported separately; neither is represented as completed without evidence.

## Next input

The user supplied the [parameter matrix](docs/sources/3x-ui-xray-parameters-matrix.pdf), the [Persian architecture brief](docs/sources/3x-ui-v3.10.0-architecture-brief.fa.md), and web references, then requested an Ubuntu/API configuration workflow. See the [source registry](docs/SOURCES.md), [detailed configuration requirements](docs/CONFIGURATION-REQUIREMENTS.md), and [validation status](docs/VALIDATION.md). The skill package and API helper are authored; installed versions, credentials, domain proxy states, and intended profile count are collected when the skill is used on the actual server. The matrix's numbered sources remain unmapped, so implementation relies on identified versioned primary sources instead.
