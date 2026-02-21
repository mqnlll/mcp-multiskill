# mcp-multiskill

一个面向多技能目录的 MCP Server。

## Skill 目录约定

每个 Skill 必须是 `skills/<skill_name>/` 下的一个文件夹，并至少包含：

- `SKILL.md`
	- 首行必须是该 skill 的简要描述。
- 一个或多个独立 `.py` 脚本
	- 脚本用 `argparse` 定义参数。
	- 在 `parse_args()` 前调用钩子：`get_parser_json(parser)`。
- `pyproject.toml`
	- 使用 `uv` 管理依赖与运行环境。

参考示例：`skills/cal`。

## MCP Server 行为

- Resource：
	- `skill://index` 返回可用技能列表与描述。
	- `skill://{skill_name}` 返回 `SKILL.md` 内容，并自动追加该 skill 下每个 `.py` 的调用信息与参数 schema。
- Tool：
	- 只提供一个入口工具 `run_skill(skill_name, script_name, argv)`。
	- 由服务端通过子进程执行 `uv run --project <skill_dir> python <script.py> ...`。

## 将已有项目改造成 Skill

1. 在项目目录新增 `SKILL.md`，并确保首行是 skill 描述。
2. 在 argparse 脚本中加入钩子：

```python
from mcp_multiskill.parser_to_schema import get_parser_json

if get_parser_json(parser):
		exit(0)
```

3. 确保项目可被 `uv` 构建与运行（包含 `pyproject.toml`）。
4. 在该项目依赖中加入 MCP server 所需依赖（至少 `mcp-multiskill`，必要时加入 `mcp[cli]`）。
