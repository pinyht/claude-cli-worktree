<!-- claude-worktree-rules:start -->
## worktree 并行开发（claude-cli-worktree）

版本：2

- 命令由用户级 Claude Code skills 提供（`~/.claude/skills/worktree-*/SKILL.md`），脚本：`~/.claude/claude-cli-worktree/scripts/worktree-task.py`，状态：`~/.claude-cli-worktree/state/`。
- 可用命令：`/worktree-new`、`/worktree-list`、`/worktree-info`、`/worktree-current`、`/worktree-status`、`/worktree-switch`、`/worktree-merge`、`/worktree-sync`、`/worktree-take-sql`、`/worktree-push-sql`、`/worktree-end`、`/worktree-help`。
- 这些命令全部只能由用户手动输入触发。不要自行调用 `worktree-task.py`，也不要用其他方式（直接 git 命令、复制文件、stash 等）复刻这些命令的流程。
- 主项目目录是可重置的统一调试槽：只用于创建任务、切换预览、合并任务、同步任务、用户手动运行服务验证和用户手动 commit。
- 任务 worktree 目录用于具体开发，不要在其中启动长期运行的项目服务。
- 槽里不要为了临时调试修改 tracked 文件；本地覆盖走 `config.local.yml`、`.env` 等已忽略文件，保证槽随时可被 `git reset --hard` + `git clean -fd` 重置。
- 任务状态保存在本地 `~/.claude-cli-worktree/state/`，不写入业务仓库。
- 脚本以非零退出码表示操作被停止或未完成（拒绝、冲突、部分失败）。遇到非零退出码时先向用户说明原因，不要自动重试，也不要用其他方式绕过约束；正常的空操作（没有任务、没有待合并改动）退出码为 0。
- 遇到数据库 schema、权限、路由、授权、配置、状态机等语义冲突时，先说明方案并询问用户。
<!-- claude-worktree-rules:end -->
