# skills

A collection of Agent Skills that encode best practices, conventions, and architectural guidance for use with AI coding assistants.

## Available Skills

| Skill | Description |
| ----- | ----------- |
| [aws-well-architected](skills/aws-well-architected/SKILL.md) | Enforces AWS Well-Architected Framework best practices across all six pillars (Operational Excellence, Security, Reliability, Performance Efficiency, Cost Optimization, Sustainability). |
| [language-conventions-source-en-docs-br](skills/language-conventions-source-en-docs-br/SKILL.md) | Enforces language usage conventions for teams based in Brazil — Brazilian Portuguese for documentation and docstrings; English for source code, configuration, and commit messages. |

## Usage

Each skill lives in its own directory under `skills/` and contains a `SKILL.md` file with:

- **Frontmatter** (`name`, `description`) for skill discovery and activation
- **Rules** the AI assistant should follow
- **Examples** illustrating correct and incorrect usage
- **Checklists** for self-review before submitting changes

Refer to a skill's `SKILL.md` when configuring your AI assistant, or link directly to the file in your project's coding guidelines.
