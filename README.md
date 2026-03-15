# skills

A collection of Agent Skills that encode best practices, conventions, and architectural guidance for use with AI coding assistants.

## Available Skills

| Skill | Description |
| ----- | ----------- |
| [aws-well-architected](skills/aws-well-architected/SKILL.md) | Enforces AWS Well-Architected Framework best practices across all six pillars (Operational Excellence, Security, Reliability, Performance Efficiency, Cost Optimization, Sustainability). |
| [language-conventions-source-en-docs-br](skills/language-conventions-source-en-docs-br/SKILL.md) | Enforces language usage conventions for teams based in Brazil — Brazilian Portuguese for documentation, docstrings, and inline comments; English for source code, configuration, and commit messages. |

## Usage

Each skill lives in its own directory under `skills/` and contains a `SKILL.md` file with:

- **Frontmatter** (`name`, `description`) for skill discovery and activation
- **Rules** the AI assistant should follow
- **Examples** illustrating correct and incorrect usage
- **Checklists** for self-review before submitting changes

Refer to a skill's `SKILL.md` when configuring your AI assistant, or link directly to the file in your project's coding guidelines.

## Skill Reviewers (GitHub Copilot Custom Agents)

Five specialized reviewer agents live in `.github/agents/`. Each reviews skills through a distinct best-practices lens:

| Agent | Source | Focus |
| ----- | ------ | ----- |
| `mgechev-skill-reviewer` | [mgechev/skills-best-practices](https://github.com/mgechev/skills-best-practices) | Structure, frontmatter discoverability, progressive disclosure, procedural instructions, deterministic scripts |
| `codex-skill-reviewer` | [OpenAI Codex Skills](https://developers.openai.com/codex/skills/) | Progressive disclosure model, implicit/explicit invocation, single-job scope, imperative style |
| `ms-agent-skill-reviewer` | [Microsoft Agent Framework](https://learn.microsoft.com/en-us/agent-framework/agents/skills) | Token budgets, security practices, script execution safety, skills-vs-workflows boundary |
| `agentskills-skill-reviewer` | [agentskills.io](https://agentskills.io/skill-creation/best-practices) | Expertise grounding, context efficiency, control calibration, instruction patterns |
| `claude-skill-reviewer` | [Claude Platform](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices) | Conciseness, degrees of freedom, naming/description, anti-patterns, feedback loops |

All five agents use the same output format (PASS / PASS WITH WARNINGS / FAIL) for uniform consumption by the LLM-as-Judge CI pipeline.
