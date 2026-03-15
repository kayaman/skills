---
name: git-best-practices
description: Enforces Git workflow best practices including trunk-based development, conventional commits, atomic commits, small pull requests, and Git hooks. Use when choosing a branching strategy, writing commit messages, structuring pull requests, configuring Git hooks and CI pipelines, managing feature flags, or setting up semantic versioning automation.
---

# Git Best Practices

Reference: *Pro Git* (Chacon & Straub), *Continuous Delivery* (Humble & Farley), *Accelerate* (Forsgren et al.)

## When to Apply

- Choosing or evaluating a branching strategy for a team or project
- Writing commit messages or reviewing them in pull requests
- Structuring pull requests for effective code review
- Setting up Git hooks and commit validation tooling
- Implementing automated versioning and changelog generation
- Improving DORA metrics (lead time, deployment frequency, change failure rate)

---

## Branching Strategy

### Trunk-Based Development (Recommended Default)

All developers collaborate on a single branch (trunk/main). Two variants:

| Variant | Team Size | Branch Lifetime | Merge Method |
|---------|-----------|----------------|--------------|
| **Direct to trunk** | Small (≤5 developers) | No branches | Direct push |
| **Short-lived feature branches** | Any size | 1–2 days maximum | PR + merge |

- SHOULD default to trunk-based development — DORA research confirms higher-performing organizations are more likely to use TBD
- MUST keep feature branches to 1–2 days maximum; MUST NOT let branches live longer than a week
- MUST use feature flags to decouple deployment from release when features span multiple days

### Branching Strategies Compared

| Strategy | Best For | Avoid When |
|----------|----------|------------|
| **Trunk-Based** | SaaS, continuous deployment, high-cadence teams | N/A — suitable for most teams |
| **GitHub Flow** | Simple — main + short-lived branches + PRs | Multiple supported release versions |
| **GitLab Flow** | Teams needing environment branches (staging, production) | Teams doing continuous deployment |
| **GitFlow** | Versioned software with multiple supported releases | Continuous delivery — Driessen himself (2020): *"adopt a simpler workflow"* |

### Feature Flags

Feature flags decouple deployment from release. MUST use them when incomplete features need to ship to production.

| Flag Type | Purpose | Lifetime |
|-----------|---------|----------|
| **Release Toggle** | Hide incomplete features in production | Days to weeks — remove after launch |
| **Ops Toggle** | Runtime circuit breakers and operational controls | Permanent or long-lived |
| **Experiment Toggle** | A/B testing and gradual rollout | Days to weeks — remove after decision |
| **Permission Toggle** | Feature access by user segment (beta, premium) | Long-lived |

- MUST remove release toggles promptly after the feature is fully launched
- SHOULD track all active flags and assign cleanup owners

---

## Commit Messages

### Conventional Commits Format

```
<type>(scope): description

[optional body]

[optional footer(s)]
```

**Core types and their SemVer mapping:**

| Type | SemVer | Purpose |
|------|--------|---------|
| `feat` | MINOR | New user-facing functionality |
| `fix` | PATCH | Bug fix |
| `feat!` or `BREAKING CHANGE:` footer | MAJOR | Breaking API change |
| `docs` | — | Documentation only |
| `style` | — | Formatting, whitespace (no logic change) |
| `refactor` | — | Code restructuring (no behavior change) |
| `perf` | PATCH | Performance improvement |
| `test` | — | Adding or correcting tests |
| `build` | — | Build system or dependency changes |
| `ci` | — | CI configuration changes |
| `chore` | — | Other maintenance (no production code) |
| `revert` | — | Reverts a previous commit |

### Chris Beams' 7 Rules

1. Separate subject from body with a blank line
2. Limit subject to **50 characters**
3. Capitalize the subject line
4. Do not end the subject with a period
5. **Use imperative mood** — "Add feature" not "Added feature" or "Adds feature"
6. Wrap body at 72 characters
7. Body explains **what and why**, not how

### Rules

- MUST use imperative mood in subject: the commit message completes the sentence *"If applied, this commit will..."*
- MUST make each commit **atomic** — one logical change that compiles and passes tests independently
- MUST NOT mix unrelated changes in a single commit (formatting + feature + bug fix)
- SHOULD use Conventional Commits format for automated changelog and versioning
- SHOULD include a body for non-trivial changes explaining WHY, not WHAT

---

## Pull Requests

### Size Matters

| PR Size | Review Time | Defect Detection | Recommendation |
|---------|-------------|-----------------|----------------|
| < 200 lines | Fast (~30 min) | Highest (~40% more defects found) | **Ideal** |
| 200–400 lines | Moderate | Good | Acceptable |
| 400–1000 lines | Slow | Declining | Split if possible |
| > 1000 lines | Very slow | Drops by ~70% | MUST split |

### Rules

- SHOULD keep PRs under 200 lines of changed code
- MUST include a clear description: context, what changed, why, how to test
- SHOULD use PR templates to ensure consistent descriptions
- MUST NOT submit PRs with failing CI checks
- SHOULD separate refactoring from feature changes — refactoring PRs reviewed differently than feature PRs

### Stacked PRs

For features too large for a single small PR, use stacked PRs — a chain of small dependent PRs that build on each other.

1. Break the feature into sequential, independently reviewable increments
2. Each PR in the stack targets the previous PR's branch (or main for the first)
3. Review and merge bottom-up
4. Tools: **Graphite**, **ghstack**, **git-branchless**

---

## Git Hooks

### Client-Side Hooks

| Hook | Stage | Purpose | Tooling |
|------|-------|---------|---------|
| `pre-commit` | Before commit is created | Lint, format, type-check staged files | lint-staged, prettier, eslint |
| `commit-msg` | After message is entered | Validate conventional commit format | commitlint |
| `pre-push` | Before push to remote | Run tests, check for secrets | jest, detect-secrets |
| `prepare-commit-msg` | Before editor opens | Pre-populate commit template | commitizen |

### Hook Management Tools

| Tool | Ecosystem | Key Feature |
|------|-----------|-------------|
| **Husky** | Node.js | Simple setup with package.json scripts |
| **pre-commit** | Python (language-agnostic) | Large plugin ecosystem, runs hooks in isolation |
| **Lefthook** | Go binary (no runtime dependency) | Parallel execution, fast, no Node required |

### Typical Hook Pipeline

```
pre-commit:
  1. lint-staged (format + lint only changed files)
  2. type-check (TypeScript, mypy)
  3. detect-secrets (prevent accidental credential commits)

commit-msg:
  1. commitlint (validate Conventional Commits format)

pre-push:
  1. test suite (unit tests, fast integration tests)
```

---

## Automated Versioning and Release

Conventional Commits enable fully automated semantic versioning:

| Tool | Approach | Best For |
|------|----------|----------|
| **semantic-release** | Fully automated: version, changelog, publish on merge | CI/CD pipelines with continuous release |
| **release-please** (Google) | Creates and maintains release PRs; merge to release | Teams wanting human approval before release; monorepo support |
| **changesets** | Developers describe changes; bot creates release PR | Monorepos with multiple packages |
| **commitizen** | Interactive CLI for crafting conventional commits | Teams onboarding to conventional commits |

---

## DORA Metrics Connection

The *Accelerate* research (Forsgren, Humble, Kim) shows four key metrics that distinguish high-performing teams:

| Metric | Elite Performance | Connection to Git Practices |
|--------|------------------|---------------------------|
| **Lead Time for Changes** | < 1 hour | Small PRs, trunk-based development, CI/CD |
| **Deployment Frequency** | Multiple per day | Feature flags, automated release |
| **Change Failure Rate** | 0–15% | Atomic commits, comprehensive tests, small PRs |
| **Time to Restore Service** | < 1 hour | Fast rollback via revert commits, feature flag kill switches |

---

## Checklist

When setting up or reviewing Git workflows, verify:

- [ ] Branching strategy matches team size and deployment model (TBD preferred)
- [ ] Feature branches live no longer than 1–2 days
- [ ] Feature flags are used for incomplete features deployed to production
- [ ] Commit messages follow Conventional Commits format with imperative mood
- [ ] Each commit is atomic — one logical change, compiles, passes tests
- [ ] PRs are under 200 lines; larger changes are stacked
- [ ] PR descriptions include context, rationale, and testing instructions
- [ ] Git hooks validate formatting, linting, and commit message format
- [ ] Automated versioning is connected to Conventional Commits
- [ ] Release toggles are tracked and removed after launch

## Key References

| Book | Author(s) | Publisher | Year |
|------|-----------|-----------|------|
| *Pro Git* (2nd ed.) | Scott Chacon, Ben Straub | Apress | 2014 |
| *Head First Git* | Raju Gandhi | O'Reilly | 2022 |
| *Continuous Delivery* | Jez Humble, David Farley | Addison-Wesley | 2010 |
| *The DevOps Handbook* (2nd ed.) | Kim, Humble, Debois, Willis, Forsgren | IT Revolution | 2021 |
| *Accelerate* | Forsgren, Humble, Kim | IT Revolution | 2018 |
| *Software Engineering at Google* | Winters, Manshreck, Wright | O'Reilly | 2020 |
