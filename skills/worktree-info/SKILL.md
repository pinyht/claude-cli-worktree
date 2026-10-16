---
name: worktree-info
description: "查看指定 claude-cli-worktree 任务的状态、分支和任务目录。仅在用户输入 /worktree-info 时执行。"
argument-hint: "<任务名>"
disable-model-invocation: true
---

# worktree-info

当用户输入 `/worktree-info 任务名` 时使用本命令。

## 执行要求

- 建议在主项目目录执行。
- 从用户输入中提取任务名；任务名不能为空。
- 调用 `python3 "$HOME/.claude/claude-cli-worktree/scripts/worktree-task.py" info "任务名"`。
- 不要启动任何项目服务。
- 成功后，向用户说明这是任务信息查询，不会自动切换当前 Claude Code 会话目录。
- 如果用户要继续开发，提示使用脚本输出的 `cd ... && claude` 命令在任务目录打开新的 Claude Code。
