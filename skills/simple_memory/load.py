#!/usr/bin/env python3

from __future__ import annotations

import argparse
from pathlib import Path
import sys

from mcp_multiskill.parser_to_schema import get_parser_json


def parse_args() -> argparse.Namespace:
	parser = argparse.ArgumentParser(description="读取 memorys/*.md 记忆或输出记忆列表")
	parser.add_argument("--memory_name", default="", type=str, help="记忆名（不含 .md 后缀）")
	parser.add_argument(
		"--list_memories",
		action="store_true",
		help="是否获取记忆列表（带上该参数时忽略记忆名）",
	)
	if get_parser_json(parser):
		exit(0)
	return parser.parse_args()


def main() -> int:
	args = parse_args()

	base_dir = Path(__file__).resolve().parent
	memory_dir = base_dir / "memorys"
	memory_dir.mkdir(parents=True, exist_ok=True)

	if args.list_memories:
		names = sorted(path.stem for path in memory_dir.glob("*.md") if path.is_file())
		print("\n".join(names))
		return 0

	if not args.memory_name:
		print("未提供记忆名", file=sys.stderr)
		return 2

	memory_path = memory_dir / f"{args.memory_name}.md"
	if not memory_path.exists():
		print(f"记忆不存在: {args.memory_name}", file=sys.stderr)
		return 1

	print(memory_path.read_text(encoding="utf-8"), end="")
	return 0


if __name__ == "__main__":
	sys.exit(main())
