#!/usr/bin/env python3
"""
Sends a skill's content to an LLM with a reviewer agent's prompt and outputs the review.

Usage:
    python review-skill.py --agent <agent-file> --skill <skill-dir> --provider <openai|anthropic>

Environment variables:
    AI_GATEWAY_URL   — ai-gateway-rs base URL (e.g. https://gateway.example.com)
    GATEWAY_API_KEY  — Bearer token for the gateway

Outputs the review text to stdout. Exits non-zero on API or input errors.
"""

import argparse
import json
import os
import sys
import time
import random
from pathlib import Path

MAX_RETRIES = 10
BASE_DELAY = 5
MAX_DELAY = 120


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


def _retry_on_rate_limit(make_request):
    """Retry a request function with exponential backoff on HTTP 429."""
    import urllib.error
    for attempt in range(MAX_RETRIES):
        try:
            return make_request()
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < MAX_RETRIES - 1:
                retry_after = e.headers.get("Retry-After")
                if retry_after and retry_after.isdigit():
                    delay = int(retry_after) + random.uniform(0, 2)
                else:
                    delay = min(BASE_DELAY * (2 ** attempt), MAX_DELAY) + random.uniform(0, 5)
                print(f"Rate limited (429). Retrying in {delay:.1f}s (attempt {attempt + 1}/{MAX_RETRIES})...", file=sys.stderr)
                time.sleep(delay)
            else:
                raise


PROVIDER_MODELS = {
    "openai": "gpt-4o",
    "anthropic": "claude-sonnet-4-5",
    "gemini": "gemini-2.5-flash",
}


def call_gateway(system_prompt: str, user_content: str, model: str, provider: str) -> str:
    import urllib.request
    import urllib.error

    gateway_url = os.environ.get("AI_GATEWAY_URL", "").rstrip("/")
    api_key = os.environ.get("GATEWAY_API_KEY", "")
    if not gateway_url:
        print("Error: AI_GATEWAY_URL not set", file=sys.stderr)
        sys.exit(1)

    payload = json.dumps({
        "model": model,
        "provider": provider,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content},
        ],
        "temperature": 0.2,
        "max_tokens": 4096,
    }).encode("utf-8")

    def make_request():
        req = urllib.request.Request(
            f"{gateway_url}/v1/chat/completions",
            data=payload,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
            },
        )
        with urllib.request.urlopen(req, timeout=180) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            return result["choices"][0]["message"]["content"]

    return _retry_on_rate_limit(make_request)


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

    model = args.model or PROVIDER_MODELS.get(args.provider, "gpt-4o")
    review = call_gateway(system_prompt, user_message, model, args.provider)

    if args.output:
        Path(args.output).write_text(review, encoding="utf-8")
        print(f"Review written to {args.output}")
    else:
        print(review)


if __name__ == "__main__":
    main()
