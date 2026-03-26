# skills

A collection of Agent Skills that encode best practices, conventions, and architectural guidance for use with AI coding assistants.

These skills are published to [agentskills](https://github.com/kayaman/agentskills) for discovery and distribution.

## Available Skills

| Skill | Description |
| ----- | ----------- |
| [aws-genai-lens](aws-genai-lens/SKILL.md) | Enforces AWS Well-Architected Generative AI Lens best practices for foundation model workloads on Amazon Bedrock and SageMaker AI. |
| [aws-well-architected](aws-well-architected/SKILL.md) | Enforces AWS Well-Architected Framework best practices across all six pillars (Operational Excellence, Security, Reliability, Performance Efficiency, Cost Optimization, Sustainability). |
| [aws-well-architected-framework](aws-well-architected-framework/SKILL.md) | Comprehensive AWS Well-Architected Framework knowledge covering all six pillars, design principles, review process, and the Well-Architected Tool. |
| [azure-well-architected](azure-well-architected/SKILL.md) | Enforces Azure Well-Architected Framework best practices across all five pillars (Reliability, Security, Cost Optimization, Operational Excellence, Performance Efficiency). |
| [blog-post-with-diagrams](blog-post-with-diagrams/SKILL.md) | Guides writing technical blog posts that embed Mermaid diagrams, ASCII art, and annotated code blocks to explain architecture, workflows, and decisions. |
| [clean-architecture](clean-architecture/SKILL.md) | Enforces Clean Architecture principles including the dependency rule, layer separation, and component design. |
| [clean-code](clean-code/SKILL.md) | Enforces clean code principles including meaningful naming, small focused functions, command-query separation, and error handling. |
| [design-an-interface](design-an-interface/SKILL.md) | Generates multiple radically different interface designs for a module using parallel sub-agents. Use when user wants to design an API, explore interface options, compare module shapes, or mentions "design it twice". |
| [design-patterns](design-patterns/SKILL.md) | Enforces correct application of software design patterns including all 23 Gang of Four patterns and modern additions. |
| [domain-driven-design](domain-driven-design/SKILL.md) | Enforces Domain-Driven Design strategic and tactical patterns including Bounded Contexts, Aggregates, Value Objects, and Domain Events. |
| [dry-principle](dry-principle/SKILL.md) | Enforces the DRY principle correctly, distinguishing true knowledge duplication from incidental code similarity. |
| [edit-article](edit-article/SKILL.md) | Edit and improve articles by restructuring sections, improving clarity, and tightening prose. Use when user wants to edit, revise, or improve an article draft. |
| [git-best-practices](git-best-practices/SKILL.md) | Enforces Git workflow best practices including trunk-based development, conventional commits, atomic commits, and small pull requests. |
| [git-guardrails-claude-code](git-guardrails-claude-code/SKILL.md) | Set up Claude Code hooks to block dangerous git commands (push, reset --hard, clean, branch -D, etc.) before they execute. Use when user wants to prevent destructive git operations, add git safety hooks, or block git push/reset in Claude Code. |
| [grill-me](grill-me/SKILL.md) | Interviews the user relentlessly about a plan or design until reaching shared understanding, resolving each branch of the decision tree. Use when user wants to stress-test a plan, get grilled on their design, or mentions "grill me". |
| [hexagonal-architecture](hexagonal-architecture/SKILL.md) | Enforces Hexagonal Architecture (Ports and Adapters) principles including driving and driven ports, adapter separation, and technology-agnostic core. |
| [improve-codebase-architecture](improve-codebase-architecture/SKILL.md) | Explore a codebase to find opportunities for architectural improvement, focusing on making the codebase more testable by deepening shallow modules. Use when user wants to improve architecture, find refactoring opportunities, consolidate tightly-coupled modules, or make a codebase more AI-navigable. |
| [language-conventions-source-en-docs-br](language-conventions-source-en-docs-br/SKILL.md) | Enforces language usage conventions for teams based in Brazil — Brazilian Portuguese for documentation, docstrings, and inline comments; English for source code, configuration, and commit messages. |
| [object-oriented-programming](object-oriented-programming/SKILL.md) | Enforces object-oriented programming principles including encapsulation, composition over inheritance, GRASP patterns, and CRC-driven design. |
| [oop-design-patterns](oop-design-patterns/SKILL.md) | Best practices for Object-Oriented Programming and Design Patterns — covers OOP fundamentals, SOLID principles, all 23 GoF patterns, refactoring, clean code, and OOAD. |
| [organize-docs-from-zip](organize-docs-from-zip/SKILL.md) | Unpacks a documentation zip into magj.dev blog/references Markdown, normalizes frontmatter, matches site tone, and stages drafts for human review before publication. |
| [prd-to-issues](prd-to-issues/SKILL.md) | Break a PRD into independently-grabbable GitHub issues using tracer-bullet vertical slices. Use when user wants to convert a PRD to issues, create implementation tickets, or break down a PRD into work items. |
| [prd-to-plan](prd-to-plan/SKILL.md) | Turn a PRD into a multi-phase implementation plan using tracer-bullet vertical slices, saved as a local Markdown file in ./plans/. Use when user wants to break down a PRD, create an implementation plan, plan phases from a PRD, or mentions "tracer bullets". |
| [project-context-sync](project-context-sync/SKILL.md) | Enforces updating a shared status file after each work session so that every agent and collaborator starts with accurate project state. |
| [request-refactor-plan](request-refactor-plan/SKILL.md) | Guides creating a detailed refactor plan with tiny commits via user interview, then files it as a GitHub issue. Use when user wants to plan a refactor, create a refactoring RFC, or break a refactor into safe incremental steps. |
| [rfc2119](rfc2119/SKILL.md) | Enforces RFC 2119 (BCP 14) requirement level keywords in documentation, specifications, and technical writing. |
| [scaffold-exercises](scaffold-exercises/SKILL.md) | Create exercise directory structures with sections, problems, solutions, and explainers that pass linting. Use when user wants to scaffold exercises, create exercise stubs, or set up a new course section. |
| [semver](semver/SKILL.md) | Enforces Semantic Versioning 2.0.0 rules for version bumps, tagging, pre-release handling, and deprecation workflows. |
| [setup-pre-commit](setup-pre-commit/SKILL.md) | Set up Husky pre-commit hooks with lint-staged (Prettier), type checking, and tests in the current repo. Use when user wants to add pre-commit hooks, set up Husky, configure lint-staged, or add commit-time formatting/typechecking/testing. |
| [solid-principles](solid-principles/SKILL.md) | Enforces SOLID principles (SRP, OCP, LSP, ISP, DIP) in object-oriented and multi-paradigm code. |
| [tdd](tdd/SKILL.md) | Test-driven development with red-green-refactor loop. Use when user wants to build features or fix bugs using TDD, mentions "red-green-refactor", wants integration tests, or asks for test-first development. |
| [triage-issue](triage-issue/SKILL.md) | Triages a GitHub issue by exploring the codebase to find root cause, then creates a GitHub issue with a TDD-based fix plan. Use when user reports a bug, wants to file an issue, mentions "triage", or wants to investigate and plan a fix for a problem. |
| [ubiquitous-language](ubiquitous-language/SKILL.md) | Extract a DDD-style ubiquitous language glossary from the current conversation, flagging ambiguities and proposing canonical terms. Saves to UBIQUITOUS_LANGUAGE.md. Use when user wants to define domain terms, build a glossary, harden terminology, create a ubiquitous language, or mentions "domain model" or "DDD". |
| [write-a-prd](write-a-prd/SKILL.md) | Create a PRD through user interview, codebase exploration, and module design, then submit as a GitHub issue. Use when user wants to write a PRD, create a product requirements document, or plan a new feature. |
| [write-a-skill](write-a-skill/SKILL.md) | Guides creation of new agent skills with proper structure, progressive disclosure, and bundled resources. Use when user wants to create, write, or build a new skill. |
| [yagni-principle](yagni-principle/SKILL.md) | Enforces the YAGNI principle to prevent speculative complexity while maintaining code quality. |

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
