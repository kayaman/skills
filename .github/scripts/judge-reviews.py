#!/usr/bin/env python3
"""
LLM-as-Judge: aggregates multiple reviewer outputs into a single verdict.

Usage:
    python judge-reviews.py --reviews-dir <dir> --provider <openai|anthropic>

Reads all .md files from --reviews-dir, sends them to an LLM with a judging
prompt, and outputs an aggregated review to stdout.

Environment variables:
    AI_GATEWAY_URL   — ai-gateway-rs base URL (e.g. https://gateway.example.com)
    GATEWAY_API_KEY  — Bearer token for the gateway
"""

import argparse
import json
import os
import sys
from pathlib import Path


JUDGE_PROMPT = """\
You are an LLM-as-Judge for Agent Skill reviews. You receive the outputs of six \
independent skill reviewers, each applying a different best-practices lens:

1. skill-reviewer (comprehensive cross-source reviewer covering all best-practice dimensions)
2. mgechev-skill-reviewer (structure, discoverability, progressive disclosure)
3. codex-skill-reviewer (Codex progressive disclosure, invocation, single-job scope)
4. ms-agent-skill-reviewer (security, token budgets, skills-vs-workflows)
5. agentskills-skill-reviewer (expertise grounding, context efficiency, patterns)
6. claude-skill-reviewer (conciseness, degrees of freedom, anti-patterns)

Your job:

1. Read all six reviews.
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
| unified  | ...     |
| mgechev  | ...     |
| codex    | ...     |
| ms-agent | ...     |
| agentskills | ... |
| claude   | ...     |
```
"""


PROVIDER_MODELS = {
    "openai": "gpt-4o",
    "anthropic": "claude-sonnet-4-5",
    "gemini": "gemini-2.5-flash",
}


def call_gateway(system_prompt: str, user_content: str, model: str, provider: str) -> str:
    import urllib.request

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
        "temperature": 0.1,
        "max_tokens": 4096,
    }).encode("utf-8")

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

    user_message = "Here are the six reviewer outputs. Aggregate them into a single verdict.\n\n" + "\n\n---\n\n".join(reviews)

    model = args.model or PROVIDER_MODELS.get(args.provider, "gpt-4o")
    result = call_gateway(JUDGE_PROMPT, user_message, model, args.provider)

    if args.output:
        Path(args.output).write_text(result, encoding="utf-8")
        print(f"Aggregated review written to {args.output}")
    else:
        print(result)


if __name__ == "__main__":
    main()
