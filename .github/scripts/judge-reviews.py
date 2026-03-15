#!/usr/bin/env python3
"""
LLM-as-Judge: aggregates multiple reviewer outputs into a single verdict.

Usage:
    python judge-reviews.py --reviews-dir <dir> --provider <openai|anthropic>

Reads all .md files from --reviews-dir, sends them to an LLM with a judging
prompt, and outputs an aggregated review to stdout.

Environment variables:
    OPENAI_API_KEY    — required when provider is openai
    ANTHROPIC_API_KEY — required when provider is anthropic
"""

import argparse
import json
import os
import sys
from pathlib import Path


JUDGE_PROMPT = """\
You are an LLM-as-Judge for Agent Skill reviews. You receive the outputs of five \
independent skill reviewers, each applying a different best-practices lens:

1. mgechev-skill-reviewer (structure, discoverability, progressive disclosure)
2. codex-skill-reviewer (Codex progressive disclosure, invocation, single-job scope)
3. ms-agent-skill-reviewer (security, token budgets, skills-vs-workflows)
4. agentskills-skill-reviewer (expertise grounding, context efficiency, patterns)
5. claude-skill-reviewer (conciseness, degrees of freedom, anti-patterns)

Your job:

1. Read all five reviews.
2. Identify findings that appear across multiple reviewers (consensus issues).
3. Identify findings unique to a single reviewer (specialist issues).
4. Prioritize: FAIL items first, then WARN items, grouped by theme.
5. Produce an aggregated verdict using these rules:
   - FAIL if any reviewer returned FAIL.
   - NEEDS WORK if two or more reviewers returned PASS WITH WARNINGS.
   - PASS WITH WARNINGS if exactly one reviewer returned PASS WITH WARNINGS.
   - PASS if all reviewers returned PASS.
6. List actionable fixes ordered by priority.

Output format:

```
## Aggregated Skill Review — `<skill-name>`

### Overall Verdict: PASS / PASS WITH WARNINGS / NEEDS WORK / FAIL

### Consensus Findings
[Issues flagged by 2+ reviewers]

### Specialist Findings
[Issues flagged by only 1 reviewer, grouped by reviewer]

### Prioritized Action Items
1. [highest priority fix]
2. [next fix]
...

### Individual Reviewer Verdicts
| Reviewer | Verdict |
|----------|---------|
| mgechev  | ...     |
| codex    | ...     |
| ms-agent | ...     |
| agentskills | ... |
| claude   | ...     |
```
"""


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
        "temperature": 0.1,
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

    with urllib.request.urlopen(req, timeout=180) as resp:
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

    with urllib.request.urlopen(req, timeout=180) as resp:
        result = json.loads(resp.read().decode("utf-8"))
        return result["content"][0]["text"]


def main():
    parser = argparse.ArgumentParser(description="LLM-as-Judge for skill reviews")
    parser.add_argument("--reviews-dir", required=True, help="Directory containing reviewer output .md files")
    parser.add_argument("--provider", default="openai", choices=["openai", "anthropic"])
    parser.add_argument("--model", default=None, help="Model override")
    parser.add_argument("--output", default=None, help="Write aggregated review to file")
    args = parser.parse_args()

    reviews_path = Path(args.reviews_dir)
    if not reviews_path.is_dir():
        print(f"Error: reviews directory not found: {args.reviews_dir}", file=sys.stderr)
        sys.exit(1)

    review_files = sorted(reviews_path.glob("*.md"))
    if not review_files:
        print(f"Error: no .md review files found in {args.reviews_dir}", file=sys.stderr)
        sys.exit(1)

    reviews = []
    for f in review_files:
        content = f.read_text(encoding="utf-8")
        reviews.append(f"### Review from {f.stem}\n\n{content}")

    user_message = "Here are the five reviewer outputs. Aggregate them into a single verdict.\n\n" + "\n\n---\n\n".join(reviews)

    if args.provider == "openai":
        model = args.model or "gpt-4o"
        result = call_openai(JUDGE_PROMPT, user_message, model)
    else:
        model = args.model or "claude-sonnet-4-20250514"
        result = call_anthropic(JUDGE_PROMPT, user_message, model)

    if args.output:
        Path(args.output).write_text(result, encoding="utf-8")
        print(f"Aggregated review written to {args.output}")
    else:
        print(result)


if __name__ == "__main__":
    main()
