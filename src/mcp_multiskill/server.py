from mcp.server.fastmcp import FastMCP

from mcp_multiskill.load_skill import (
	list_skills_summary,
	render_skill_for_client,
	run_skill_script,
)


mcp = FastMCP("mcp-multiskill")


@mcp.resource("skill://index")
def skills_index() -> str:
	summaries = list_skills_summary()
	if not summaries:
		return "No skills found."

	lines = ["# Skills", ""]
	for item in summaries:
		lines.append(f"- {item['name']}: {item['description']}")
	return "\n".join(lines)


@mcp.resource("skill://{skill_name}")
def skill_detail(skill_name: str) -> str:
	return render_skill_for_client(skill_name)


@mcp.tool(name="run_skill")
def run_skill(skill_name: str, script_name: str, argv: list[str] | None = None) -> dict:
	"""Single entry tool for executing scripts in a skill through uv."""
	return run_skill_script(skill_name=skill_name, script_name=script_name, argv=argv)


if __name__ == "__main__":
	mcp.run()
