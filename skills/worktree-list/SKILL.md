---
name: worktree-list
description: "查看当前仓库的 claude-cli-worktree 并行 Git worktree 任务列表。仅在用户输入 /worktree-list 时执行。"
disable-model-invocation: true
---

# worktree-list

当用户输入 `/worktree-list` 时使用本命令。

## 执行要求

- 建议在主项目目录执行。
- 调用 `python3 "$HOME/.claude/claude-cli-worktree/scripts/worktree-task.py" list`。
- 不要启动任何项目服务。
- 把任务名、状态、目录、分支和是否有未合并改动用简洁中文说明给用户。
