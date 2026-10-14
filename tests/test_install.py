"""Verify the actual skill bundle installs without touching existing projects."""

import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]


class InstallTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="xray skill install ")
        self.root = Path(self.tmp.name)
        self.package = self.root / "package"
        self.package.mkdir()
        shutil.copy2(REPO / "install.py", self.package / "install.py")
        shutil.copytree(REPO / "skills", self.package / "skills", ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))

    def tearDown(self):
        self.tmp.cleanup()

    def install(self, *args, expected=0):
        result = subprocess.run([sys.executable, str(self.package / "install.py"), *map(str, args)], capture_output=True, text=True)
        self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
        return result

    def test_three_agent_locations_with_resources_and_repeat(self):
        for agent, directory in [("codex", ".agents/skills"), ("antigravity", ".agents/skills"), ("claude-code", ".claude/skills")]:
            with self.subTest(agent=agent):
                project = self.root / (agent + " project with spaces")
                self.install("--agent", agent, "--project", project, "--dry-run")
                self.assertFalse(project.exists())
                self.install("--agent", agent, "--project", project)
                target = project / directory / "xray-inbound-expert"
                self.assertTrue((target / "SKILL.md").is_file())
                self.assertTrue((target / "references/api.md").is_file())
                result = subprocess.run([sys.executable, str(target / "scripts/panel_api.py"), "--help"], capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.install("--agent", agent, "--project", project)

    def test_custom_destination_and_existing_edit_preserved(self):
        destination = self.root / "another agent"
        self.install("--destination", destination, "--skill", "xray-inbound-expert")
        file = destination / "xray-inbound-expert/SKILL.md"
        file.write_text("Keep local customization", encoding="utf-8")
        self.install("--destination", destination, expected=1)
        self.assertEqual(file.read_text(), "Keep local customization")

    def test_cache_does_not_ship_or_break_repeat_install(self):
        source = self.package / "skills/xray-inbound-expert/scripts/__pycache__"
        source.mkdir()
        (source / "example.pyc").write_bytes(b"temporary")
        target = self.root / "target"
        self.install("--destination", target)
        self.assertFalse((target / "xray-inbound-expert/scripts/__pycache__").exists())
        (source / "example.pyc").write_bytes(b"updated temporary")
        self.install("--destination", target)


if __name__ == "__main__":
    unittest.main()
