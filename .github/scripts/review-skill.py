#!/usr/bin/env python3
"""
Sends a skill's content to an LLM with a reviewer agent's prompt and outputs the review.

Usage:
    python review-skill.py --agent <agent-file> --skill <skill-dir> --provider <openai|anthropic>

Environment variables:
    OPENAI_API_KEY   — required when provider is openai
    ANTHROPIC_API_KEY — required when provider is anthropic

Outputs the review text to stdout. Exits non-zero on API or input errors.
"""

import argparse
import json
import os
import sys
from pathlib import Path


def read_file(path: str) -> str:
    p = Path(path)
    if not p.exists():
        print(f"Error: file not found: {path}", file=sys.stderr)
        sys.exit(1)
    return p.read_text(encoding="utf-8")


def collect_skill_content(skill_dir: str) -> str:
    skill_path = Path(skill_dir)
    if not skill_path.is_dir():
        print(f"Error: skill directory not found: {skill_dir}", file=sys.stderr)
        sys.exit(1)

    parts = []

    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        print(f"Error: no SKILL.md found in {skill_dir}", file=sys.stderr)
        sys.exit(1)

    parts.append(f"## SKILL.md\n\n{skill_md.read_text(encoding='utf-8')}")

    for sub in sorted(skill_path.iterdir()):
        if sub.is_dir() and sub.name in ("scripts", "references", "assets"):
            for f in sorted(sub.iterdir()):
                if f.is_file():
                    parts.append(f"## {sub.name}/{f.name}\n\n{f.read_text(encoding='utf-8')}")

    tree_lines = []
    for item in sorted(skill_path.rglob("*")):
        rel = item.relative_to(skill_path)
        indent = "  " * (len(rel.parts) - 1)
        prefix = "├── " if item.is_file() else "└── "
        tree_lines.append(f"{indent}{prefix}{item.name}")

    parts.insert(0, f"## Directory Structure\n\n```\n{skill_path.name}/\n" + "\n".join(tree_lines) + "\n```")

    return "\n\n---\n\n".join(parts)


def parse_agent_prompt(agent_path: str) -> str:
    content = read_file(agent_path)
    if "---" not in content:
        return content

    parts = content.split("---", 2)
    if len(parts) >= 3:
        return parts[2].strip()
    return content


def call_openai(system_prompt: str, user_content: str, model: str) -> str:
    import urllib.request

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY not set", file=sys.stderr)
        sys.exit(1)

    payload = json.dumps({
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content},
        ],
        "temperature": 0.2,
        "max_tokens": 4096,
    }).encode("utf-8")

    req = urllib.request.Request(
        "https://api.openai.com/v1/chat/completions",
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
    )

    with urllib.request.urlopen(req, timeout=120) as resp:
        result = json.loads(resp.read().decode("utf-8"))
        return result["choices"][0]["message"]["content"]


def call_anthropic(system_prompt: str, user_content: str, model: str) -> str:
    import urllib.request

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("Error: ANTHROPIC_API_KEY not set", file=sys.stderr)
        sys.exit(1)

    payload = json.dumps({
        "model": model,
        "max_tokens": 4096,
        "system": system_prompt,
        "messages": [
            {"role": "user", "content": user_content},
        ],
    }).encode("utf-8")

    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=payload,
        headers={
            "Content-Type": "application/json",
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
        },
    )

    with urllib.request.urlopen(req, timeout=120) as resp:
        result = json.loads(resp.read().decode("utf-8"))
        return result["content"][0]["text"]


def main():
    parser = argparse.ArgumentParser(description="Review a skill using an LLM-powered agent")
    parser.add_argument("--agent", required=True, help="Path to the .agent.md file")
    parser.add_argument("--skill", required=True, help="Path to the skill directory")
    parser.add_argument("--provider", default="openai", choices=["openai", "anthropic"])
    parser.add_argument("--model", default=None, help="Model override (defaults: gpt-4o for openai, claude-sonnet-4-20250514 for anthropic)")
    parser.add_argument("--output", default=None, help="Write review to file instead of stdout")
    args = parser.parse_args()

    system_prompt = parse_agent_prompt(args.agent)
    skill_content = collect_skill_content(args.skill)
    user_message = f"Review the following skill:\n\n{skill_content}"

    if args.provider == "openai":
        model = args.model or "gpt-4o"
        review = call_openai(system_prompt, user_message, model)
    else:
        model = args.model or "claude-sonnet-4-20250514"
        review = call_anthropic(system_prompt, user_message, model)

    if args.output:
        Path(args.output).write_text(review, encoding="utf-8")
        print(f"Review written to {args.output}")
    else:
        print(review)


if __name__ == "__main__":
    main()
