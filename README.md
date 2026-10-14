# Portable agent skills

The **xray-inbound-expert** skill designs and applies inbounds, DNS, and routing through the API of an existing Ubuntu-hosted 3X-UI panel. It asks for domain proxy states, client compatibility, and profile count before selecting a compatible direct or CDN path. It does not install 3X-UI or Xray; the user runs end-to-end connection tests.

The package uses the shared Agent Skills format for Codex, Google Antigravity, and Claude Code, with a Python standard-library API helper. Read [SKILL.md](skills/xray-inbound-expert/SKILL.md) for the workflow and [validation status](docs/VALIDATION.md) for actual checks and outstanding runtime validation.

Read [REQUIREMENTS.md](REQUIREMENTS.md) for compatibility and release requirements and [EXPERTISE.md](EXPERTISE.md) for the agreed scope. The supplied parameter matrix and its extracted table are preserved under `docs/sources/`; see the [datasheet review](docs/DATASHEET-REVIEW.md) for coverage and details needing confirmation before authoring the expert skill.

The supplied Persian architecture brief is also preserved under `docs/sources/`. The [source registry](docs/SOURCES.md) records direct upstream links and versioned evidence; [detailed configuration requirements](docs/CONFIGURATION-REQUIREMENTS.md) cover inbound/client consistency, DNS, routing, Lua, and panel API output.

## Install a skill

Prerequisites: Git to clone this private repository and Python 3.10 or newer to run the installer. Authenticate with a GitHub account that has repository access.

```sh
git clone https://github.com/nima-sadria/agent-skill-requirements.git
cd agent-skill-requirements
python3 install.py --agent codex --project /path/to/project
python3 install.py --agent antigravity --project /path/to/project
python3 install.py --agent claude-code --project /path/to/project
```

Replace `/path/to/project` with the directory where you run your agent on Ubuntu. Run only the command for your chosen agent. On Windows, use `python` or `py` instead of `python3` and quote paths containing spaces. The installer copies the complete skill folder from `skills/`.

For another agent that supports the Agent Skills format, specify its documented discovery directory:

```sh
python3 install.py --destination /path/to/agent/skills
```

Use `--skill skill-name` to select one skill, or `--dry-run` to preview. Existing identical skills are left in place. Conflicting installations are preserved and reported; the installer never overwrites them. It does not execute bundled scripts or change agent settings.

Agents without `SKILL.md` support need a separate adapter. A custom directory alone does not make an unsupported agent compatible.

## Project discovery paths

| Agent | Destination under your project |
| --- | --- |
| Codex | `.agents/skills/` |
| Antigravity | `.agents/skills/` |
| Claude Code | `.claude/skills/` |

Codex and Antigravity can share the same installation in a project. If a skill does not appear, reload the agent session and check its discovery settings.

The paths follow the official [Codex documentation](https://developers.openai.com/codex/skills), [Antigravity documentation](https://antigravity.google/docs/skills), and [Claude Code documentation](https://code.claude.com/docs/en/best-practices). Recheck these when supporting a new host version.

## Use the skill

Ask your agent in Persian or your preferred language, for example:

> Use xray-inbound-expert on my existing Ubuntu 3X-UI panel. Ask for my domains and their orange-cloud/DNS-only status, then create two suitable connection profiles and configure DNS/routing through the API. I will test the connections myself.

Codex can invoke it as `$xray-inbound-expert`; Claude Code can use `/xray-inbound-expert`. Other hosts use their documented skill invocation or discover it from the request.

Provide API access through your agent's existing credential facility or protected local environment. The [API reference](skills/xray-inbound-expert/references/api.md) explains the helper and snapshot handling. The agent inspects versions and current configuration, prepares the exact changes, applies authorized requests, and reads back their state. Availability of a valid profile still depends on the installed versions, domains, certificates, listeners, and client capabilities.
