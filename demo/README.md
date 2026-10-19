# Tiny Agent Harness

一个可直接阅读和修改的 Python 智能体执行框架。模型通过本地 Ollama `/api/chat` 接入；agent 负责消息循环、工具结果回传、步数上限和执行轨迹。运行时只用 Python 标准库，不需要 API key。

## 快速开始

要求 Python 3.10+，本机已启动 Ollama，并已安装一个支持工具调用的模型。默认模型名是 `qwen3:8b`，可用 `--model` 更改。

如果 Windows 的 `python` 命令指向不可用的应用商店别名，请将下面命令中的 `python` 换成实际 Python 可执行文件路径。

```powershell
cd D:\AIPro\code\demo
ollama pull qwen3:8b
python -m agent_harness "列出当前工作区的文件，并概括 README.md"
```

指定工作区、开启写入和打印工具轨迹：

```powershell
python -m agent_harness "在 notes.txt 中写一段摘要" --workspace D:\AIPro\code\demo --allow-write --trace
```

也可使用 `pip install -e .` 后运行 `tiny-agent "你的任务"`。

## 结构

- `agent_harness/model.py`：Ollama HTTP 适配器。
- `agent_harness/agent.py`：模型与工具循环，默认最多 8 步。
- `agent_harness/tools.py`：工作区工具定义、参数校验、路径限制。
- `agent_harness/__main__.py`：命令行入口。
- `tests/`：不需要 Ollama 的离线测试。

默认只暴露 `list_files` 和 `read_file`。`--allow-write` 才暴露 `write_file`；写入已存在文件还需模型明确传入 `overwrite=true`。工具路径必须相对工作区，`.git` 元数据不可访问，读取有长度上限，不提供任意命令执行。一次运行的消息只保存在内存中；`--trace` 会把工具参数和结果打印到标准错误输出，可能包含文件内容，使用时注意终端日志。

测试：

```powershell
python -m unittest discover -s tests -v
```
