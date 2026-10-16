# claude-cli-worktree

Claude Code 的 Git worktree 并行开发辅助工具。

它安装一组用户级 Claude Code skills（`/worktree-*`）和一个 Python 辅助脚本，用来简化多会话并行开发时的 worktree 创建、预览、合并、同步和清理流程。

**核心模型：主项目目录 = 可重置的统一调试槽。** 任务在独立 worktree 里开发，需要看效果时把任务的**未提交改动**复制进主目录验证，验证通过再合并回主目录并手动 commit——整个流程不需要为了「能调试」而做 WIP 提交，主线历史里也不会出现一堆临时 commit。

## 功能

- 创建独立 Git worktree 任务目录。
- 预览时先把主项目目录恢复干净，再把某个任务的改动复制过来看效果，不污染其他任务，不自动 commit。
- 合并任务时先把主项目目录恢复干净，再把任务改动三方合并回主项目目录，但不自动 commit；遇到冲突会保留冲突状态，并由 Claude 基于冲突上下文和本次合并完整改动范围给出 AI 语义级整体修复方案。
- 可把任务中新增的 SQL 迁移文件提前拿到主项目目录 review，或一键提交并推送主线后同步回各任务。
- 查看当前会话任务、恢复预览、同步、清理 worktree 任务。
- 任务状态按仓库隔离保存到 `~/.claude-cli-worktree/state/`，不写入业务项目仓库。
- **所有命令只能由用户手动触发**：通过 frontmatter 的 `disable-model-invocation: true` 锁定，模型看不到这些命令、无法自主调用、也不会被告知可以用别的方式复刻流程。

## 适用场景

适合在同一个 Git 仓库里同时推进多个任务，且**项目只能单实例运行**的情况（例如登录态、授权、持久化数据无法复制多份）：

- 一个任务在改后端接口，同时另一个会话修前端样式。
- 你想让多个会话互不影响地改代码，但最终都回到主项目目录统一验证和 commit。
- 你需要在多个任务之间来回切换预览效果，但暂时不想把某个任务作为最终合并结果。

它不负责启动服务、运行长期进程或自动 commit。主项目目录是可重置的统一调试槽，只用于创建任务、切换预览、合并任务、同步任务、用户手动验证和用户手动 commit；任务 worktree 目录用于具体开发。

## 要求

- Claude Code 2.1.x（本工具在 2.1.301 上验证；依赖 skill 的 `disable-model-invocation` 与 `user-invocable-only` 状态）。
- Python 3。
- Git。
- Linux 或 macOS。暂不适配 Windows。

## 安装

```bash
python3 install.py
```

安装脚本会：

```text
skills/worktree-*/SKILL.md  -> ~/.claude/skills/worktree-*/SKILL.md
scripts/worktree-task.py    -> ~/.claude/claude-cli-worktree/scripts/worktree-task.py
rules/claude-md-block.md    -> 注入 ~/.claude/CLAUDE.md 的标记块
```

并创建 `~/.claude-cli-worktree/state/`。安装时会逐个校验 SKILL.md 的 frontmatter（缺 `disable-model-invocation: true` 或描述未加引号会直接报错退出），避免 Claude Code 静默降级导致锁定失效。

安装后重启 Claude Code，输入 `/skills` 确认 12 个命令的状态为 `user-invocable-only`。

## 怎么使用

安装并重启 Claude Code 后，在输入框里直接输入命令名（**只能手动触发**）：

```text
/worktree-list
/worktree-new 修复登录跳转
/worktree-status
/worktree-switch 修复登录跳转
/worktree-merge 修复登录跳转
/worktree-take-sql 修复登录跳转 migrations/18.sql
/worktree-push-sql 修复登录跳转 migrations/18.sql
```

任务名可以使用中文、英文、数字、`-`、`_`、`.`，但必须是单个参数，不能包含空格、Tab、换行、路径分隔符或 `: * ? " < > |` 等路径非法字符，也不能以 `-` 开头或结尾。

## 命令说明

除特别说明外，建议在主项目目录执行这些命令。

| 输入 | 执行位置 | 作用 |
| --- | --- | --- |
| `/worktree-new <任务名>` | 主项目目录 | 创建新的任务 worktree 和任务分支。 |
| `/worktree-list` | 主项目目录，任务目录也可 | 查看当前 Git 仓库的 worktree 任务。 |
| `/worktree-info <任务名>` | 主项目目录，任务目录也可 | 查看指定任务的状态、分支和任务目录，并输出继续开发命令。 |
| `/worktree-current` | 主项目目录，任务目录也可 | 查看当前会话对应任务；在主项目目录查看当前是 switch 预览、主线基线还是未提交改动状态。 |
| `/worktree-status` | 主项目目录，任务目录也可 | 查看当前会话所在 Git 仓库的 `git status --short --branch --untracked-files=all`。 |
| `/worktree-switch <任务名>` | 主项目目录 | 先把主项目目录恢复干净，再把任务目录里的改动复制过来用于验证，不反向同步、不自动 commit。 |
| `/worktree-switch --clear` | 主项目目录 | 清除当前 switch 预览，把主项目目录恢复到当前提交并清理新增文件。 |
| `/worktree-merge <任务名>` | 主项目目录 | 先把主项目目录恢复干净，再把任务目录里的改动三方合并到主项目目录，不自动 commit；冲突时由 Claude 分析并引导处理。 |
| `/worktree-sync <任务名>` | 主项目目录 | 把主项目最新提交带到指定任务目录；任务改动已被主线吸收时自动对齐。 |
| `/worktree-sync --all` | 主项目目录 | 把主项目最新提交带到所有任务目录；无法自动同步的任务会停止并在汇总中列出。 |
| `/worktree-take-sql <任务名> <sql...>` | 主项目目录 | 把任务 worktree 中新增的 `.sql` 文件拿到主项目目录，并从任务 worktree 删除；不自动 commit。 |
| `/worktree-push-sql <任务名> <sql...>` | 主项目目录 | 拿取 SQL 并删除任务副本，自动 add/commit/push，把本次 SQL 同步到各任务后切到该任务预览。 |
| `/worktree-end <任务名>` | 主项目目录 | 清理任务 worktree、任务分支和任务状态。任务仍有未合并改动时会停止。 |
| `/worktree-end <任务名> --force` | 主项目目录 | 强制清理任务。仅在确认任务 worktree 剩余差异可以放弃时使用。 |
| `/worktree-help` | 任意 Git 项目目录 | 查看命令帮助。 |

## 推荐流程

假设任务叫 `修复登录跳转`：

1. 在主项目目录输入 `/worktree-new 修复登录跳转`，记下输出的任务目录。
2. 在任务目录打开新的 Claude Code 会话（输出里给了 `cd ... && claude`）。
3. 在任务目录开发、改文件、跑必要的短命令；不要启动长期运行的项目服务。
4. 需要临时看效果时，回主项目目录输入 `/worktree-switch 修复登录跳转`，然后手动启动服务或运行验证命令。
5. 要切换看另一个任务，直接 `/worktree-switch 另一个任务名`；工具会先确认主项目目录只有上一轮预览改动，再恢复干净并切换。
6. 开发完成后，回主项目目录输入 `/worktree-merge 修复登录跳转`。合并成功后任务 worktree 会自动对齐主线。
7. 验证通过后，由你手动 `git commit`。
8. 主项目有新提交后，可输入 `/worktree-sync --all` 把最新提交带到其他任务目录。
9. 输入 `/worktree-end 修复登录跳转` 清理任务。

## 状态和生成文件

```text
~/.claude-cli-worktree/state/<repo-id>/tasks.json    # 任务注册表
../<repo-name>.claude-worktrees/task-<任务名>-<hash>/ # 任务 worktree
```

状态文件只保存在本机，不会写入业务项目仓库。任务 worktree 放在仓库外的同级目录，是为了让**未提交的工作**不受仓库内任何清理操作影响（`git clean -xfd`、`rm -rf .claude`、IDE 索引等都碰不到它）。

## 安全约束

- 不自动 commit（`/worktree-push-sql` 除外，它的语义就是提交并推送 SQL）。
- `/worktree-switch` 只用于临时预览，不更新任务基线、不反向同步任务 worktree。
- `/worktree-switch` 会在主项目目录干净或等于已记录的 switch 预览时，自动恢复到当前提交并清理新增文件后复制任务改动；遇到无法确认来源的未提交改动会停止。
- `/worktree-merge` 不自动 commit；冲突时保留冲突状态并由 Claude 给出语义级修复方案供你选择。
- 主项目目录有无法确认来源的未提交改动时，不执行 switch/merge/sync/take-sql/push-sql。
- 任务 worktree 有未合并改动时，不执行 end；`--force` 只在你明确确认放弃剩余差异时使用。
- 不自动启动项目服务。

## 退出码约定

- `0`：操作完成，包括正常的空操作（没有任务、任务没有待合并改动）。
- 非零：操作被停止或未完成，原因写到 stderr。包括：拒绝执行（槽里有来源不明改动）、合并冲突、任务无法同步、`/worktree-sync --all` 或 `/worktree-push-sql` 有部分任务被阻止、`/worktree-end` 发现未合并改动。

命令定义据此要求 Claude 先说明原因再让用户决定，不要自动重试或绕过。

## 常见问题

**为什么不用 `~/.claude/commands/`？**
该目录在 2.1.301 里已标记为废弃（`commands_DEPRECATED`），且被列入内置写保护目录。skills 与斜杠命令在本版本已统一：命令定义放 `~/.claude/skills/`，用户侧体验完全一样（输入 `/worktree-x`）。

**为什么任务 worktree 不放 `.claude/worktrees/`？**
那里是 Claude Code 原生 worktree 自己管理的地盘（`claude -w` 创建、`claude rm` 清理、带 locked 标记）。本项目要长期保存未提交的开发成果，放在仓库外的 `../<repo>.claude-worktrees/` 更安全，归属也更清楚。

**命令会不会被 Claude 自动调用？**
不会。每个命令的 frontmatter 都带 `disable-model-invocation: true`，模型看不到、调不了；即使强行调用也会被拒绝，并被明确告知不得用其他方式复刻该流程。

**运行命令时弹权限确认怎么办？**
首次运行时在权限提示里选「总是允许」即可，Claude Code 会记住。也可以预先在 `~/.claude/settings.json` 里加：

```json
{
  "permissions": {
    "allow": ["Bash(python3 /home/<你>/.claude/claude-cli-worktree/scripts/worktree-task.py:*)"]
  }
}
```

## 卸载

```bash
python3 uninstall.py
```

卸载脚本会删除已安装的命令定义、脚本和 `~/.claude/CLAUDE.md` 中的规则块，并询问是否保留历史任务状态。

## 升级

```bash
git pull
python3 install.py
```

升级后同样需要重启 Claude Code。

## 许可证

MIT
