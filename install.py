#!/usr/bin/env python3
"""安装 claude-cli-worktree：用户级 skills + 脚本 + CLAUDE.md 规则块。"""
import re
import shutil
from pathlib import Path


VERSION = "1"
BEGIN = "<!-- claude-worktree-rules:start -->"
END = "<!-- claude-worktree-rules:end -->"
SCRIPT_NAME = "worktree-task.py"
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


def validate_skill(path):
    """校验 SKILL.md frontmatter。

    Claude Code 在 frontmatter 解析失败时会静默退回「目录名 + 正文第一行」当描述，
    此时 allowed-tools / disable-model-invocation 会一起静默失效——必须在安装期拦住。
    """
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise SystemExit(f"frontmatter 缺失（文件必须以 --- 开头）: {path}")
    end = text.find("\n---", 3)
    if end == -1:
        raise SystemExit(f"frontmatter 未闭合: {path}")
    frontmatter = text[4:end]
    problems = []
    if not re.search(r"(?m)^name:\s*\S", frontmatter):
        problems.append("缺少 name")
    if not re.search(r'(?m)^description:\s*"', frontmatter):
        problems.append("description 缺失或未用双引号包裹")
    if not re.search(r"(?m)^disable-model-invocation:\s*true\s*$", frontmatter):
        problems.append("缺少 disable-model-invocation: true")
    if problems:
        raise SystemExit(f"{path} frontmatter 校验失败: {'; '.join(problems)}")


def install_skills(source_root, target_skills):
    installed = []
    for command in COMMANDS:
        src = source_root / "skills" / command
        if not (src / "SKILL.md").is_file():
            raise SystemExit(f"缺少命令定义: {src / 'SKILL.md'}")
        dst = target_skills / command
        if dst.exists():
            shutil.rmtree(dst)
        shutil.copytree(src, dst)
        validate_skill(dst / "SKILL.md")
        installed.append(dst / "SKILL.md")
    return installed


def install_script(source_root, target_scripts):
    target_scripts.mkdir(parents=True, exist_ok=True)
    src = source_root / "scripts" / SCRIPT_NAME
    if not src.is_file():
        raise SystemExit(f"缺少脚本: {src}")
    dst = target_scripts / SCRIPT_NAME
    shutil.copy2(src, dst)
    return dst


def load_rule_block(source_root):
    path = source_root / "rules" / "claude-md-block.md"
    block = path.read_text(encoding="utf-8").strip()
    if BEGIN not in block or END not in block:
        raise SystemExit(f"规则块缺少标记 {BEGIN} / {END}: {path}")
    return block


def update_claude_md(claude_md, block):
    content = claude_md.read_text(encoding="utf-8") if claude_md.exists() else ""
    if BEGIN in content and END in content:
        before, rest = content.split(BEGIN, 1)
        _old, after = rest.split(END, 1)
        new_content = before.rstrip() + "\n\n" + block + "\n" + after.lstrip()
        changed = new_content != content
    else:
        sep = "\n\n" if content.strip() else ""
        new_content = content.rstrip() + sep + block + "\n"
        changed = True

    if changed:
        claude_md.parent.mkdir(parents=True, exist_ok=True)
        claude_md.write_text(new_content, encoding="utf-8")
        return "updated"
    return "unchanged"


def main():
    source_root = Path(__file__).resolve().parent
    home = Path.home()
    home_claude = home / ".claude"
    target_skills = home_claude / "skills"
    target_scripts = home_claude / "claude-cli-worktree" / "scripts"
    tool_state = home / ".claude-cli-worktree" / "state"

    target_skills.mkdir(parents=True, exist_ok=True)
    skills = install_skills(source_root, target_skills)
    script = install_script(source_root, target_scripts)
    block = load_rule_block(source_root)
    claude_md = home_claude / "CLAUDE.md"
    md_status = update_claude_md(claude_md, block)
    tool_state.mkdir(parents=True, exist_ok=True)

    print("claude-cli-worktree 已安装/更新。")
    print(f"命令: {len(skills)} 个 -> {target_skills}/worktree-*/SKILL.md")
    print(f"脚本: {script}")
    print(f"CLAUDE.md 规则块: {md_status} -> {claude_md}")
    print(f"状态目录: {tool_state}")
    print()
    print("请重启 Claude Code，然后：")
    print("  1. 输入 /skills 确认这 12 个命令的状态为 user-invocable-only（模型不可调用）")
    print("  2. 在业务项目主目录输入 /worktree-list 试运行")
    print()
    print("首次运行命令时如果弹出权限确认，选「总是允许」即可，Claude Code 会记住。")
    print("也可以预先在 ~/.claude/settings.json 里加：")
    print('  "permissions": { "allow": ["Bash(python3 '
          f'{script}:*)"] }}')
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
