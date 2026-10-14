# Requirements for portable expert skills

Build one expert skill that supports the same user outcomes in Codex, Google Antigravity, and Claude Code. Keep the source in `skills/<skill-name>/` and copy the complete folder into each host's discovery directory. The requirements below are project requirements; they do not imply that the future skill has passed runtime checks.

## Scope for the first skill

The [xray-inbound-expert skill](skills/xray-inbound-expert/SKILL.md) creates inbounds and configures Xray DNS and routing in an existing Ubuntu-hosted 3X-UI environment through the panel API. Follow [EXPERTISE.md](EXPERTISE.md) for its scope and the [detailed configuration requirements](docs/CONFIGURATION-REQUIREMENTS.md) for source-derived constraints. Installation and upgrades are excluded. The user runs connection tests. See [validation status](docs/VALIDATION.md) for completed checks and unverified combinations.

## Shared package format

Follow the [Agent Skills specification](https://agentskills.io/specification):

- Include UTF-8 `SKILL.md` with YAML frontmatter and Markdown instructions.
- Require `name` and `description` in the portable core.
- Use a name of 1 to 64 lowercase ASCII letters, digits, or hyphens, matching the folder name. Disallow leading, trailing, or consecutive hyphens.
- Keep the description nonempty and at most 1024 characters. Explain the capability and its trigger.
- Add `scripts/`, `references/`, and `assets/` only when they support the actual workflow. Link references with relative paths and explain when to read them.

## Expert behavior

Define the domain, supported tasks, inputs, outputs, and observable success criteria before authoring the skill. Capture specialist decisions, important constraints, and authoritative references. Keep general advice and duplicated instructions out of the entrypoint.

Give examples of relevant requests and similar requests outside scope. Distinguish source facts from assumptions. Ask for missing information only when it changes the result, and preserve the user's established authorization and task boundaries.

Define appropriate recovery behavior for unavailable tools, invalid input, or partial failures. Choose retry limits according to the actual task. Never claim success without checking the requested outcome.

## Compatibility and installation

- The core workflow must describe capabilities rather than depend on one host's tool names, slash commands, or hidden state.
- Keep host-specific metadata and optional tool integrations separate. Codex may use `agents/openai.yaml`; shared instructions must work without it.
- Document necessary runtimes, operating systems, network services, and credentials. Supply an alternative workflow where feasible when an optional integration is absent.
- Use relative resource paths and explicit script arguments. Resolve packaged resources from the installed skill directory.
- Default to project installation. The installer must preserve the complete package, support paths containing spaces, preview changes, and preserve conflicting existing files.
- Support other Agent Skills hosts through a custom destination. Verify discovery and behavior separately for each added host; do not promise support for every AI agent.

## Release acceptance

Before marking an expert skill ready:

1. Validate frontmatter, naming, resource links, and absence of unfinished placeholders.
2. Install into a fresh project for each of the three target agents and verify discovery.
3. Evaluate realistic relevant requests, an out-of-scope request, and a missing-input or missing-tool case. Check generated outputs against the expertise criteria. For the first skill, the user runs connection tests; agent evaluation must not initiate live connection tests.
4. Run bundled scripts on their supported operating systems. Check installation preview, repeat installation, conflicting files, and paths containing spaces.
5. Record actual agent versions, operating systems, results, and any untested combinations. Format compatibility alone is not runtime validation.
6. Keep GitHub visibility private and exclude credentials, personal data, generated installations, and local environment files.

## Implementation sequence

Receive the user's technical documentation, finalize the expertise requirements, author the smallest useful skill, validate the package, and verify behavior on the target hosts. The user then performs connection tests. Publish with the actual validation status in this private repository. Add adapters only when a concrete host difference requires one.
