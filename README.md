# skills

A collection of Agent Skills that encode best practices, conventions, and architectural guidance for use with AI coding assistants.

## Available Skills

| Skill | Description |
| ----- | ----------- |
| [aws-well-architected](skills/aws-well-architected/SKILL.md) | Enforces AWS Well-Architected Framework best practices across all six pillars (Operational Excellence, Security, Reliability, Performance Efficiency, Cost Optimization, Sustainability). |
| [blog-post-with-diagrams](skills/blog-post-with-diagrams/SKILL.md) | Guides writing technical blog posts that embed Mermaid diagrams, ASCII art, and annotated code blocks to explain architecture, workflows, and decisions. |
| [azure-well-architected](skills/azure-well-architected/SKILL.md) | Enforces Azure Well-Architected Framework best practices across all five pillars (Reliability, Security, Cost Optimization, Operational Excellence, Performance Efficiency). |
| [language-conventions-source-en-docs-br](skills/language-conventions-source-en-docs-br/SKILL.md) | Enforces language usage conventions for teams based in Brazil — Brazilian Portuguese for documentation, docstrings, and inline comments; English for source code, configuration, and commit messages. |
| [project-context-sync](skills/project-context-sync/SKILL.md) | Enforces updating a shared status file after each work session so that every agent and collaborator starts with accurate project state. |
| [rfc2119](skills/rfc2119/SKILL.md) | Enforces RFC 2119 (BCP 14) requirement level keywords in documentation, specifications, and technical writing. |
| [semver](skills/semver/SKILL.md) | Enforces Semantic Versioning 2.0.0 rules for version bumps, tagging, pre-release handling, and deprecation workflows. |

## Usage

Each skill lives in its own directory under `skills/` and contains a `SKILL.md` file with:

- **Frontmatter** (`name`, `description`) for skill discovery and activation
- **Rules** the AI assistant should follow
- **Examples** illustrating correct and incorrect usage
- **Checklists** for self-review before submitting changes

Refer to a skill's `SKILL.md` when configuring your AI assistant, or link directly to the file in your project's coding guidelines.

## Skill Reviewers (GitHub Copilot Custom Agents)

Six reviewer agents live in `.github/agents/`. One unified reviewer covers all best-practice dimensions, while five specialists dive deep into their respective source:

| Agent | Source | Focus |
| ----- | ------ | ----- |
| `skill-reviewer` | All sources | Comprehensive cross-source reviewer covering structure, discoverability, progressive disclosure, instruction quality, content expertise, scope, security, scripts, anti-patterns, and portability |
| `mgechev-skill-reviewer` | [mgechev/skills-best-practices](https://github.com/mgechev/skills-best-practices) | Structure, frontmatter discoverability, progressive disclosure, procedural instructions, deterministic scripts |
| `codex-skill-reviewer` | [OpenAI Codex Skills](https://developers.openai.com/codex/skills/) | Progressive disclosure model, implicit/explicit invocation, single-job scope, imperative style |
| `ms-agent-skill-reviewer` | [Microsoft Agent Framework](https://learn.microsoft.com/en-us/agent-framework/agents/skills) | Token budgets, security practices, script execution safety, skills-vs-workflows boundary |
| `agentskills-skill-reviewer` | [agentskills.io](https://agentskills.io/skill-creation/best-practices) | Expertise grounding, context efficiency, control calibration, instruction patterns |
| `claude-skill-reviewer` | [Claude Platform](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices) | Conciseness, degrees of freedom, naming/description, anti-patterns, feedback loops |

All six agents use the same output format (PASS / PASS WITH WARNINGS / FAIL) for uniform consumption by the LLM-as-Judge CI pipeline.

### CI Setup

The review pipeline requires LLM API keys. Run the setup script to configure secrets:

```bash
export OPENAI_API_KEY="sk-..."
# and/or
export ANTHROPIC_API_KEY="sk-ant-..."
export LLM_PROVIDER="openai"  # or "anthropic"
bash .github/scripts/setup-gh-secrets.sh
```
