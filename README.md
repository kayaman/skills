# skills

A collection of Agent Skills that encode best practices, conventions, and architectural guidance for use with AI coding assistants.

## Available Skills

| Skill | Description |
| ----- | ----------- |
| [aws-genai-lens](skills/aws-genai-lens/SKILL.md) | Enforces AWS Well-Architected Generative AI Lens best practices for foundation model workloads on Amazon Bedrock and SageMaker AI. |
| [aws-well-architected](skills/aws-well-architected/SKILL.md) | Enforces AWS Well-Architected Framework best practices across all six pillars (Operational Excellence, Security, Reliability, Performance Efficiency, Cost Optimization, Sustainability). |
| [aws-well-architected-framework](skills/aws-well-architected-framework/SKILL.md) | Comprehensive AWS Well-Architected Framework knowledge covering all six pillars, design principles, review process, and the Well-Architected Tool. |
| [azure-well-architected](skills/azure-well-architected/SKILL.md) | Enforces Azure Well-Architected Framework best practices across all five pillars (Reliability, Security, Cost Optimization, Operational Excellence, Performance Efficiency). |
| [blog-post-with-diagrams](skills/blog-post-with-diagrams/SKILL.md) | Guides writing technical blog posts that embed Mermaid diagrams, ASCII art, and annotated code blocks to explain architecture, workflows, and decisions. |
| [clean-architecture](skills/clean-architecture/SKILL.md) | Enforces Clean Architecture principles including the dependency rule, layer separation, and component design. |
| [clean-code](skills/clean-code/SKILL.md) | Enforces clean code principles including meaningful naming, small focused functions, command-query separation, and error handling. |
| [design-patterns](skills/design-patterns/SKILL.md) | Enforces correct application of software design patterns including all 23 Gang of Four patterns and modern additions. |
| [domain-driven-design](skills/domain-driven-design/SKILL.md) | Enforces Domain-Driven Design strategic and tactical patterns including Bounded Contexts, Aggregates, Value Objects, and Domain Events. |
| [dry-principle](skills/dry-principle/SKILL.md) | Enforces the DRY principle correctly, distinguishing true knowledge duplication from incidental code similarity. |
| [git-best-practices](skills/git-best-practices/SKILL.md) | Enforces Git workflow best practices including trunk-based development, conventional commits, atomic commits, and small pull requests. |
| [hexagonal-architecture](skills/hexagonal-architecture/SKILL.md) | Enforces Hexagonal Architecture (Ports and Adapters) principles including driving and driven ports, adapter separation, and technology-agnostic core. |
| [language-conventions-source-en-docs-br](skills/language-conventions-source-en-docs-br/SKILL.md) | Enforces language usage conventions for teams based in Brazil — Brazilian Portuguese for documentation, docstrings, and inline comments; English for source code, configuration, and commit messages. |
| [object-oriented-programming](skills/object-oriented-programming/SKILL.md) | Enforces object-oriented programming principles including encapsulation, composition over inheritance, GRASP patterns, and CRC-driven design. |
| [oop-design-patterns](skills/oop-design-patterns/SKILL.md) | Best practices for Object-Oriented Programming and Design Patterns — covers OOP fundamentals, SOLID principles, all 23 GoF patterns, refactoring, clean code, and OOAD. |
| [project-context-sync](skills/project-context-sync/SKILL.md) | Enforces updating a shared status file after each work session so that every agent and collaborator starts with accurate project state. |
| [rfc2119](skills/rfc2119/SKILL.md) | Enforces RFC 2119 (BCP 14) requirement level keywords in documentation, specifications, and technical writing. |
| [semver](skills/semver/SKILL.md) | Enforces Semantic Versioning 2.0.0 rules for version bumps, tagging, pre-release handling, and deprecation workflows. |
| [solid-principles](skills/solid-principles/SKILL.md) | Enforces SOLID principles (SRP, OCP, LSP, ISP, DIP) in object-oriented and multi-paradigm code. |
| [yagni-principle](skills/yagni-principle/SKILL.md) | Enforces the YAGNI principle to prevent speculative complexity while maintaining code quality. |

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
