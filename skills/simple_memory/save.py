#!/usr/bin/env python3

from __future__ import annotations

import argparse
from pathlib import Path
import sys

from mcp_multiskill.parser_to_schema import get_parser_json


def parse_args() -> argparse.Namespace:
	parser = argparse.ArgumentParser(description="保存一条记忆到 memorys/*.md")
	parser.add_argument("--memory_name", required=True, type=str, help="记忆名（不含 .md 后缀）")
	if get_parser_json(parser):
		exit(0)
	return parser.parse_args()


def main() -> int:
	args = parse_args()

	base_dir = Path(__file__).resolve().parent
	memory_dir = base_dir / "memorys"
	memory_dir.mkdir(parents=True, exist_ok=True)

	memory_path = memory_dir / f"{args.memory_name}.md"
	memory_content = sys.stdin.read()
	memory_path.write_text(memory_content, encoding="utf-8")
	return 0


if __name__ == "__main__":
	sys.exit(main())
