from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from mcp_multiskill import load_skill


class TestLoadSkill(unittest.TestCase):
    def test_list_skill_dirs_filters_by_skill_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "ok").mkdir()
            (root / "ok" / "SKILL.md").write_text("desc", encoding="utf-8")
            (root / "missing").mkdir()
            (root / "note.txt").write_text("x", encoding="utf-8")

            result = load_skill.list_skill_dirs(root)

            self.assertEqual(result, [root / "ok"])

    def test_get_skill_dir_raises_for_missing_or_invalid(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "demo").mkdir()

            with self.assertRaisesRegex(ValueError, "Skill not found"):
                load_skill.get_skill_dir("not-exist", root)

            with self.assertRaisesRegex(ValueError, "Skill missing SKILL.md"):
                load_skill.get_skill_dir("demo", root)

    def test_read_skill_markdown_raises_for_empty_content(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            skill_dir = root / "demo"
            skill_dir.mkdir()
            (skill_dir / "SKILL.md").write_text("   \n\n", encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "is empty"):
                load_skill.read_skill_markdown("demo", root)

    def test_get_skill_description_uses_first_line(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            skill_dir = root / "demo"
            skill_dir.mkdir()
            (skill_dir / "SKILL.md").write_text("first line\nsecond line", encoding="utf-8")

            description = load_skill.get_skill_description("demo", root)

            self.assertEqual(description, "first line")

    def test_list_skill_scripts_filters_private_and_init(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            skill_dir = root / "demo"
            skill_dir.mkdir()
            (skill_dir / "SKILL.md").write_text("desc", encoding="utf-8")
            (skill_dir / "main.py").write_text("", encoding="utf-8")
            (skill_dir / "helper.py").write_text("", encoding="utf-8")
            (skill_dir / "__init__.py").write_text("", encoding="utf-8")
            (skill_dir / "_private.py").write_text("", encoding="utf-8")
            (skill_dir / "README.md").write_text("", encoding="utf-8")

            scripts = load_skill.list_skill_scripts("demo", root)

            self.assertEqual([s.name for s in scripts], ["helper.py", "main.py"])

    @patch("mcp_multiskill.load_skill.subprocess.run")
    def test_get_script_schema_parses_json_output(self, mock_run) -> None:
        mock_run.return_value = SimpleNamespace(returncode=0, stdout='{"a": 1}', stderr="")
        skill_dir = Path("/tmp/skill")
        script_path = skill_dir / "main.py"

        schema = load_skill._get_script_schema(script_path, skill_dir)

        self.assertEqual(schema, {"a": 1})
        mock_run.assert_called_once()

    @patch("mcp_multiskill.load_skill.subprocess.run")
    def test_get_script_schema_returns_raw_text_when_not_json(self, mock_run) -> None:
        mock_run.return_value = SimpleNamespace(returncode=0, stdout="not-json", stderr="")

        schema = load_skill._get_script_schema(Path("/tmp/skill/main.py"), Path("/tmp/skill"))

        self.assertEqual(schema, "not-json")

    @patch("mcp_multiskill.load_skill.subprocess.run")
    def test_get_script_schema_raises_on_subprocess_error(self, mock_run) -> None:
        mock_run.return_value = SimpleNamespace(returncode=1, stdout="", stderr="boom")

        with self.assertRaisesRegex(RuntimeError, "Failed to extract parser schema"):
            load_skill._get_script_schema(Path("/tmp/skill/main.py"), Path("/tmp/skill"))

    @patch("mcp_multiskill.load_skill._get_script_schema", return_value={"type": "object"})
    def test_render_skill_for_client_renders_tool_docs(self, _mock_schema) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            skill_dir = root / "demo"
            skill_dir.mkdir()
            (skill_dir / "SKILL.md").write_text("desc line\nmore", encoding="utf-8")
            (skill_dir / "main.py").write_text("", encoding="utf-8")

            text = load_skill.render_skill_for_client("demo", root)

            self.assertIn("## Tool Invocation", text)
            self.assertIn("### main.py", text)
            self.assertIn("- script_name: `main`", text)
            self.assertIn("Argument schema:", text)

    def test_render_skill_for_client_without_scripts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            skill_dir = root / "demo"
            skill_dir.mkdir()
            (skill_dir / "SKILL.md").write_text("desc", encoding="utf-8")

            text = load_skill.render_skill_for_client("demo", root)

            self.assertIn("No runnable python scripts found in this skill.", text)

    def test_list_skills_summary(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for name, desc in (("a", "desc a"), ("b", "desc b")):
                skill_dir = root / name
                skill_dir.mkdir()
                (skill_dir / "SKILL.md").write_text(desc + "\nmore", encoding="utf-8")

            summary = load_skill.list_skills_summary(root)

            self.assertEqual(
                summary,
                [
                    {"name": "a", "description": "desc a"},
                    {"name": "b", "description": "desc b"},
                ],
            )

    @patch("mcp_multiskill.load_skill.subprocess.run")
    def test_run_skill_script_invokes_uv_run_and_returns_result(self, mock_run) -> None:
        mock_run.return_value = SimpleNamespace(returncode=0, stdout="ok", stderr="")

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            skill_dir = root / "demo"
            skill_dir.mkdir()
            (skill_dir / "SKILL.md").write_text("desc", encoding="utf-8")
            (skill_dir / "main.py").write_text("", encoding="utf-8")

            result = load_skill.run_skill_script("demo", "main", ["--x", "1"], skills_root=root)

            self.assertEqual(result["returncode"], 0)
            self.assertEqual(result["stdout"], "ok")
            self.assertIn("main.py", " ".join(result["command"]))
            self.assertIn("--x", result["command"])
            mock_run.assert_called_once()
            kwargs = mock_run.call_args.kwargs
            self.assertEqual(kwargs["stdin"], load_skill.subprocess.DEVNULL)
            self.assertIsNone(kwargs["input"])

    @patch("mcp_multiskill.load_skill.subprocess.run")
    def test_run_skill_script_passes_stdin_when_provided(self, mock_run) -> None:
        mock_run.return_value = SimpleNamespace(returncode=0, stdout="ok", stderr="")

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            skill_dir = root / "demo"
            skill_dir.mkdir()
            (skill_dir / "SKILL.md").write_text("desc", encoding="utf-8")
            (skill_dir / "main.py").write_text("", encoding="utf-8")

            load_skill.run_skill_script(
                "demo",
                "main",
                ["--x", "1"],
                skills_root=root,
                stdin="hello stdin",
            )

            mock_run.assert_called_once()
            kwargs = mock_run.call_args.kwargs
            self.assertIsNone(kwargs["stdin"])
            self.assertEqual(kwargs["input"], "hello stdin")

    def test_run_skill_script_raises_when_script_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            skill_dir = root / "demo"
            skill_dir.mkdir()
            (skill_dir / "SKILL.md").write_text("desc", encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "Script not found"):
                load_skill.run_skill_script("demo", "missing", [], skills_root=root)


if __name__ == "__main__":
    unittest.main()
