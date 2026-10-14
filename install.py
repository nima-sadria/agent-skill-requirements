"""Copy portable skill bundles into an agent's discovery directory."""

import argparse
import re
import shutil
import sys
from pathlib import Path


AGENT_PATHS = {
    "codex": Path(".agents/skills"),
    "antigravity": Path(".agents/skills"),
    "claude-code": Path(".claude/skills"),
}


def files(folder):
    return {p.relative_to(folder): p.read_bytes() for p in folder.rglob("*")
            if p.is_file() and "__pycache__" not in p.relative_to(folder).parts and p.suffix != ".pyc"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--agent", choices=AGENT_PATHS)
    mode.add_argument("--destination", type=Path, help="Discovery directory for another Agent Skills host")
    parser.add_argument("--project", type=Path, help="Project root; required with --agent")
    parser.add_argument("--skill", help="Install one named skill instead of all available skills")
    parser.add_argument("--dry-run", action="store_true", help="Preview without writing files")
    args = parser.parse_args()
    if args.agent and args.project is None:
        parser.error("--project is required with --agent")
    if args.destination and args.project is not None:
        parser.error("Use --project with --agent, or use --destination alone")
    if args.skill and not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", args.skill):
        parser.error("--skill must be a lowercase skill folder name")

    source = Path(__file__).resolve().parent / "skills"
    destination = (args.project / AGENT_PATHS[args.agent] if args.agent else args.destination).resolve()
    if destination == source or source in destination.parents:
        parser.error("Destination must be outside the source skills directory")
    bundles = sorted(p for p in source.iterdir() if p.is_dir()) if source.is_dir() else []
    if args.skill:
        bundles = [p for p in bundles if p.name == args.skill]
    if not bundles:
        print("No matching skill bundles are available. Add the expert skill under skills/ first.")
        return 1

    # Preflight all bundles so predictable conflicts cannot cause a partial install.
    pending = []
    for bundle in bundles:
        if not (bundle / "SKILL.md").is_file():
            raise ValueError(f"Missing SKILL.md: {bundle}")
        if bundle.is_symlink() or any(p.is_symlink() for p in bundle.rglob("*")):
            raise ValueError(f"Use regular files and directories in the package: {bundle}")
        target = destination / bundle.name
        if target.is_symlink():
            raise ValueError(f"Existing symlink preserved: {target}")
        if target.exists():
            if target.is_dir() and files(bundle) == files(target):
                print(f"Already installed: {target}")
                continue
            raise ValueError(f"Existing conflicting installation preserved: {target}")
        pending.append((bundle, target))

    for bundle, target in pending:
        if args.dry_run:
            print(f"Would install: {bundle.name} -> {target}")
        else:
            destination.mkdir(parents=True, exist_ok=True)
            shutil.copytree(bundle, target, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
            print(f"Installed: {target}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, ValueError) as error:
        print(f"Installation failed: {error}", file=sys.stderr)
        sys.exit(1)
