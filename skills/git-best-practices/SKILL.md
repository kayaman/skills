---
name: git-best-practices
description: Enforces Git workflow best practices including trunk-based development, conventional commits, atomic commits, small pull requests, and Git hooks. Use when choosing a branching strategy, writing commit messages, structuring pull requests, configuring Git hooks and CI pipelines, managing feature flags, or setting up semantic versioning automation.
---

# Git Best Practices

> **Status:** Draft — book list for review. Content to be added in second round.

## Key References

| Book | Author(s) | Publisher | Year |
|------|-----------|-----------|------|
| *Pro Git* (2nd ed.) | Scott Chacon, Ben Straub | Apress | 2014 |
| *Head First Git* | Raju Gandhi | O'Reilly | 2022 |
| *Continuous Delivery* | Jez Humble, David Farley | Addison-Wesley | 2010 |
| *The DevOps Handbook* (2nd ed.) | Kim, Humble, Debois, Willis, Forsgren | IT Revolution | 2021 |
| *Accelerate* | Forsgren, Humble, Kim | IT Revolution | 2018 |
| *Software Engineering at Google* | Winters, Manshreck, Wright | O'Reilly | 2020 |

## Topics to Cover

- Trunk-Based Development: direct-to-trunk vs short-lived feature branches (1-2 days max)
- Feature flags as deployment/release decoupling: Release, Ops, Experiment, Permission toggles
- Branching strategies compared: GitFlow, GitHub Flow, GitLab Flow — when to use each
- Conventional Commits format: type(scope): description, mapping to SemVer
- Chris Beams' 7 rules for commit messages: imperative mood, 50-char subject, body explains why
- Atomic commits: one logical change, compiles and passes tests
- Small PRs (<200 lines): 3x faster approval, 40% more defects caught
- Stacked PRs for large features (Graphite, Meta)
- Git hooks: pre-commit (lint, format), commit-msg (commitlint), pre-push (tests)
- Tooling: Husky, pre-commit, Lefthook, commitizen, semantic-release, release-please
- DORA metrics and trunk-based development correlation
