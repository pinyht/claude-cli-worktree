#!/usr/bin/env python3
"""卸载 claude-cli-worktree：命令定义 + 脚本 + CLAUDE.md 规则块。"""
import shutil
from pathlib import Path


BEGIN = "<!-- claude-worktree-rules:start -->"
END = "<!-- claude-worktree-rules:end -->"
COMMANDS = [
    "worktree-new",
    "worktree-list",
    "worktree-info",
    "worktree-current",
    "worktree-status",
    "worktree-switch",
    "worktree-merge",
    "worktree-sync",
    "worktree-take-sql",
    "worktree-push-sql",
    "worktree-end",
    "worktree-help",
]


def remove_tree(path):
    if path.exists():
        shutil.rmtree(path)
        return "removed"
    return "not found"


def remove_commands(target_skills):
    removed = 0
    for command in COMMANDS:
        path = target_skills / command
        if path.exists():
            shutil.rmtree(path)
            removed += 1
    return removed


def remove_rules_block(claude_md):
    if not claude_md.exists():
        return "not found"

    content = claude_md.read_text(encoding="utf-8")
    if BEGIN not in content or END not in content:
        return "unchanged"

    before, rest = content.split(BEGIN, 1)
    _old, after = rest.split(END, 1)
    new_content = before.rstrip() + "\n\n" + after.lstrip()
    if new_content.strip():
        claude_md.write_text(new_content.rstrip() + "\n", encoding="utf-8")
    else:
        claude_md.write_text("", encoding="utf-8")
    return "updated"


def ask_keep_state():
    while True:
        answer = input("是否保留历史任务状态？[Y/n] ").strip().lower()
        if answer in ("", "y", "yes"):
            return True
        if answer in ("n", "no"):
            return False
        print("请输入 y 或 n。")


def main():
    home = Path.home()
    home_claude = home / ".claude"
    target_skills = home_claude / "skills"
    script_home = home_claude / "claude-cli-worktree"
    tool_home = home / ".claude-cli-worktree"

    removed = remove_commands(target_skills)
    script_status = remove_tree(script_home)
    md_status = remove_rules_block(home_claude / "CLAUDE.md")

    keep_state = ask_keep_state()
    state_status = "kept" if keep_state else remove_tree(tool_home)

    print("claude-cli-worktree 已卸载。")
    print(f"命令: {removed} 个已删除 -> {target_skills}/worktree-*")
    print(f"脚本: {script_status} -> {script_home}")
    print(f"CLAUDE.md 规则块: {md_status} -> {home_claude / 'CLAUDE.md'}")
    print(f"状态目录: {state_status} -> {tool_home}")
    print("请重启 Claude Code，让卸载结果生效。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
