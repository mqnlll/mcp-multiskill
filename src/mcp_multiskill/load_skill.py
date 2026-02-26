from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path
from typing import Any


SKILL_MARKDOWN = "SKILL.md"


def get_default_skills_root() -> Path:
	return Path(__file__).resolve().parents[2] / "skills"


def list_skill_dirs(skills_root: Path | None = None) -> list[Path]:
	root = skills_root or get_default_skills_root()
	if not root.exists():
		return []

	skill_dirs: list[Path] = []
	for child in sorted(root.iterdir()):
		if not child.is_dir():
			continue
		if (child / SKILL_MARKDOWN).exists():
			skill_dirs.append(child)
	return skill_dirs


def get_skill_dir(skill_name: str, skills_root: Path | None = None) -> Path:
	candidate = (skills_root or get_default_skills_root()) / skill_name
	if not candidate.exists() or not candidate.is_dir():
		raise ValueError(f"Skill not found: {skill_name}")
	if not (candidate / SKILL_MARKDOWN).exists():
		raise ValueError(f"Skill missing {SKILL_MARKDOWN}: {skill_name}")
	return candidate


def read_skill_markdown(skill_name: str, skills_root: Path | None = None) -> str:
	skill_dir = get_skill_dir(skill_name, skills_root)
	skill_md = skill_dir / SKILL_MARKDOWN
	content = skill_md.read_text(encoding="utf-8").strip()
	if not content:
		raise ValueError(f"{skill_name}/{SKILL_MARKDOWN} is empty")
	return content


def get_skill_description(skill_name: str, skills_root: Path | None = None) -> str:
	content = read_skill_markdown(skill_name, skills_root)
	first_line = content.splitlines()[0].strip()
	if not first_line:
		raise ValueError(f"First line of {skill_name}/{SKILL_MARKDOWN} must be description")
	return first_line


def list_skill_scripts(skill_name: str, skills_root: Path | None = None) -> list[Path]:
	skill_dir = get_skill_dir(skill_name, skills_root)
	scripts = [
		path
		for path in sorted(skill_dir.glob("*.py"))
		if path.name != "__init__.py" and not path.name.startswith("_")
	]
	return scripts


def _get_script_schema(script_path: Path, skill_dir: Path) -> Any:
	env = os.environ.copy()
	env["PRINT_MCP_SCHEMA"] = "1"
	command = [
		"uv",
		"run",
		"--project",
		str(skill_dir),
		"python",
		str(script_path),
	]
	result = subprocess.run(command, capture_output=True, text=True, env=env, stdin=subprocess.DEVNULL)
	if result.returncode != 0:
		raise RuntimeError(
			f"Failed to extract parser schema from {script_path.name}: {result.stderr.strip()}"
		)

	output = result.stdout.strip()
	if not output:
		return None
	try:
		return json.loads(output)
	except json.JSONDecodeError:
		return output


def render_skill_for_client(skill_name: str, skills_root: Path | None = None) -> str:
	skill_dir = get_skill_dir(skill_name, skills_root)
	base_markdown = read_skill_markdown(skill_name, skills_root)
	scripts = list_skill_scripts(skill_name, skills_root)

	lines: list[str] = [base_markdown, "", "## Tool Invocation", ""]
	if not scripts:
		lines.append("No runnable python scripts found in this skill.")
		return "\n".join(lines)

	lines.append("Use MCP tool `run_skill(skill_name, script_name, argv)` to execute a script.")
	lines.append("")

	for script in scripts:
		schema = _get_script_schema(script, skill_dir)
		lines.append(f"### {script.name}")
		lines.append("")
		lines.append(f"- skill_name: `{skill_name}`")
		lines.append(f"- script_name: `{script.stem}`")
		lines.append("- argv: list of CLI arguments")
		lines.append("- stdin: optional text passed to process stdin")
		lines.append("")
		if schema is not None:
			lines.append("Argument schema:")
			lines.append("```json")
			lines.append(json.dumps(schema, ensure_ascii=False, indent=2))
			lines.append("```")
			lines.append("")

	return "\n".join(lines).strip()


def list_skills_summary(skills_root: Path | None = None) -> list[dict[str, str]]:
	summaries: list[dict[str, str]] = []
	for skill_dir in list_skill_dirs(skills_root):
		skill_name = skill_dir.name
		summaries.append(
			{
				"name": skill_name,
				"description": get_skill_description(skill_name, skills_root),
			}
		)
	return summaries


def run_skill_script(
	skill_name: str,
	script_name: str,
	argv: list[str] | None = None,
	skills_root: Path | None = None,
	stdin: str | None = None,
) -> dict[str, Any]:
	skill_dir = get_skill_dir(skill_name, skills_root)
	script_file = script_name if script_name.endswith(".py") else f"{script_name}.py"
	script_path = skill_dir / script_file
	if not script_path.exists():
		raise ValueError(f"Script not found in skill {skill_name}: {script_file}")

	command = [
		"uv",
		"run",
		"--project",
		str(skill_dir),
		"python",
		str(script_path),
		*(argv or []),
	]
	result = subprocess.run(
		command,
		capture_output=True,
		text=True,
		input=stdin,
		stdin=subprocess.DEVNULL if stdin is None else None,
	)
	return {
		"command": command,
		"returncode": result.returncode,
		"stdout": result.stdout,
		"stderr": result.stderr,
	}
