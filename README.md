# Portable agent skills

Requirements and installation tooling for expert skills shared across Codex, Google Antigravity, and Claude Code. The first skill will create inbounds and configure Xray DNS and routing for an existing 3X-UI environment. It will not install 3X-UI or Xray. This repository contains requirements only; implementation awaits the user's documentation, and the user will run connection tests.

Read [REQUIREMENTS.md](REQUIREMENTS.md) for compatibility and release requirements and [EXPERTISE.md](EXPERTISE.md) for the agreed scope. Supply the technical documentation next so the expert skill can be authored.

## Install a skill

Prerequisites: Git to clone this private repository and Python 3.10 or newer to run the installer. Authenticate with a GitHub account that has repository access.

```sh
git clone https://github.com/nima-sadria/agent-skill-requirements.git
cd agent-skill-requirements
python install.py --agent codex --project /path/to/project
python install.py --agent antigravity --project /path/to/project
python install.py --agent claude-code --project /path/to/project
```

On Windows, use `py` if `python` is unavailable and quote paths containing spaces. Run only the command for your chosen agent. The installer copies complete folders from `skills/`; it reports that nothing is available until the first expert skill is added.

For another agent that supports the Agent Skills format, specify its documented discovery directory:

```sh
python install.py --destination /path/to/agent/skills
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
