from mcp.server.fastmcp import FastMCP

from .load_skill import (
	list_skills_summary,
	render_skill_for_client,
	run_skill_script,
)


mcp = FastMCP(
	"mcp-multiskill",
	instructions="You are interacting with a multi-skill MCP server. Before executing any skills, you MUST first call the `get_skill_index` tool to retrieve the list of available skills and their descriptions."
)


def skills_index() -> str:
	summaries = list_skills_summary()
	if not summaries:
		return "No skills found."

	lines = ["# Skills", ""]
	for item in summaries:
		lines.append(f"- {item['name']}: {item['description']}")
	return "\n".join(lines)

@mcp.tool(name="get_skill_index")
def get_skill_index() -> str:
	"""Get the skill index. You MUST first call this tool to retrieve the list of available skills"""
	return skills_index()

@mcp.tool(name="get_skill")
def get_skill(skill_name: str) -> str:
	"""Get a specific skill detail by name."""
	return render_skill_for_client(skill_name)


@mcp.tool(name="run_skill")
def run_skill(
	skill_name: str,
	script_name: str,
	argv: list[str] | None = None,
	stdin: str | None = None,
) -> dict:
	"""Single entry tool for executing scripts in a skill through uv. You should call get_skill to check the details of the skill before calling this tool, as you need to provide the correct script_name, argv and optional stdin."""
	return run_skill_script(
		skill_name=skill_name,
		script_name=script_name,
		argv=argv,
		stdin=stdin,
	)


if __name__ == "__main__":
	mcp.run()
