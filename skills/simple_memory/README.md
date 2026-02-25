# simple_memory

一个最小的“记忆存取”脚本示例：

- `save.py`：保存一条记忆到 `memorys/<记忆名>.md`
- `load.py`：读取指定记忆，或列出所有记忆名

记忆文件统一保存在当前目录下的 `memorys/` 文件夹。

## 环境要求

- Python 3.10+

## 使用方式

在 `simple_memory` 目录下执行。

### 1) 保存记忆

```bash
python save.py --memory_name demo --memory_content "# 标题
这是一条记忆"
```

说明：

- `--memory_name`：记忆名（不含 `.md` 后缀）
- `--memory_content`：Markdown 文本内容

执行后会写入文件：`memorys/demo.md`

### 2) 读取指定记忆

```bash
python load.py --memory_name demo
```

记忆内容会通过标准输出（stdout）返回。

### 3) 获取记忆列表

```bash
python load.py --list_memories
```

会输出所有记忆名（每行一个，不带 `.md` 后缀）。

## 返回码（load.py）

- `0`：成功
- `1`：记忆不存在
- `2`：未提供 `--memory_name`（且未使用 `--list_memories`）

## 目录结构

```text
simple_memory/
├── save.py
├── load.py
├── memorys/
└── README.md
```
