# mcp-multiskill

一个面向多技能目录的 MCP Server。

## Skill 目录约定

每个 Skill 必须是 `skills/<skill_name>/` 下的一个文件夹，并至少包含：

- `SKILL.md`
	- 首行必须是该 skill 的简要描述。
	- 其余与一般 SKILL.md 无异。
- 一个或多个独立 `.py` 脚本
	- 脚本用 `argparse` 定义参数。
	- 在 `parse_args()` 前调用钩子：`get_parser_json(parser)`。
- `pyproject.toml`
	- 使用 `uv` 管理依赖与运行环境。

参考示例：`skills/cal`。

## MCP Server 行为

- Tool：
	- `get_skill_index()`：返回可用 skill 列表与描述。
	- `get_skill(skill_name)`：返回指定 skill 的 `SKILL.md`，并自动追加该 skill 下每个 `.py` 的调用信息与参数 schema。
	- `run_skill(skill_name, script_name, argv)`：执行指定 skill 脚本。
	- 服务端通过子进程执行：`uv run --project <skill_dir> python <script.py> ...`。

期望 agent 调用顺序：

1. 先调用 `get_skill_index()` 获取技能列表。
2. 再调用 `get_skill(skill_name)` 查看脚本与参数。
3. 最后调用 `run_skill(...)` 执行目标脚本。

## 将已有项目改造成 Skill

1. 复制/链接到 `skills/<skill_name>/`
2. 在项目目录新增 `SKILL.md`，并确保首行是 skill 描述。
3. 确保项目可被 `uv` 构建与运行（包含 `pyproject.toml`）。
```bash
cd skills/<skill_name>/
uv sync # 构建环境
uv run python xxx.py # 测试运行
```
4. 在该项目依赖中加入 MCP server 所需依赖 `mcp-multiskill`。
```bash
uv add --editable ../../
```
5. 在 argparse 脚本中加入钩子：

```python
from mcp_multiskill.parser_to_schema import get_parser_json

if get_parser_json(parser):
	exit(0)
```

```bash
PRINT_MCP_SCHEMA=1 uv run python xxx.py
# 若输出为 JSON 格式的参数描述, 则钩子添加成功
```