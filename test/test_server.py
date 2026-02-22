from __future__ import annotations

import unittest
from unittest.mock import patch

import sys
import types
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))


fake_fastmcp_module = types.ModuleType("mcp.server.fastmcp")


class DummyFastMCP:
    def __init__(self, *_args, **_kwargs):
        pass

    def tool(self, name=None):
        def decorator(func):
            return func

        return decorator

    def run(self):
        return None


fake_fastmcp_module.FastMCP = DummyFastMCP
fake_server_module = types.ModuleType("mcp.server")
fake_server_module.fastmcp = fake_fastmcp_module
fake_mcp_module = types.ModuleType("mcp")
fake_mcp_module.server = fake_server_module

sys.modules.setdefault("mcp", fake_mcp_module)
sys.modules.setdefault("mcp.server", fake_server_module)
sys.modules.setdefault("mcp.server.fastmcp", fake_fastmcp_module)

from mcp_multiskill import server


class TestServer(unittest.TestCase):
    @patch("mcp_multiskill.server.list_skills_summary", return_value=[])
    def test_skills_index_no_skills(self, _mock_summary) -> None:
        self.assertEqual(server.skills_index(), "No skills found.")

    @patch(
        "mcp_multiskill.server.list_skills_summary",
        return_value=[
            {"name": "cal", "description": "calculator"},
            {"name": "time", "description": "clock"},
        ],
    )
    def test_skills_index_with_items(self, _mock_summary) -> None:
        text = server.skills_index()

        self.assertIn("# Skills", text)
        self.assertIn("- cal: calculator", text)
        self.assertIn("- time: clock", text)

    @patch("mcp_multiskill.server.skills_index", return_value="# Skills")
    def test_get_skill_index_delegates(self, mock_skills_index) -> None:
        result = server.get_skill_index()

        self.assertEqual(result, "# Skills")
        mock_skills_index.assert_called_once_with()

    @patch("mcp_multiskill.server.render_skill_for_client", return_value="skill detail")
    def test_get_skill_delegates(self, mock_render) -> None:
        result = server.get_skill("cal")

        self.assertEqual(result, "skill detail")
        mock_render.assert_called_once_with("cal")

    @patch("mcp_multiskill.server.run_skill_script", return_value={"returncode": 0})
    def test_run_skill_delegates(self, mock_run_skill_script) -> None:
        result = server.run_skill("cal", "main", ["--x", "1"])

        self.assertEqual(result, {"returncode": 0})
        mock_run_skill_script.assert_called_once_with(
            skill_name="cal",
            script_name="main",
            argv=["--x", "1"],
        )


if __name__ == "__main__":
    unittest.main()
