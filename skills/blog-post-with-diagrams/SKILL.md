---
name: blog-post-with-diagrams
description: Guides writing technical blog posts that embed Mermaid diagrams, ASCII art, and annotated code blocks to explain architecture, workflows, and decisions. Use when drafting engineering blog posts, developer tutorials, or technical deep-dives that benefit from visual explanations.
---

# Blog Post with Diagrams

Write technical blog posts that combine narrative, code, and diagrams to explain complex topics visually.

## When to Use

- Drafting a technical blog post that explains architecture or system design
- Writing a developer tutorial with step-by-step workflows
- Creating a deep-dive or postmortem that involves data flow or component interaction
- Any post where a diagram would clarify what prose alone cannot

## Post Structure

Follow this skeleton. Sections marked *optional* may be dropped when the post type does not need them.

```
# Title                          ← concise, specific
## TL;DR                         ← 2-3 sentence summary
## Context / Problem             ← why this matters
## Approach / Solution           ← what you built or decided
  ### Diagram: <caption>         ← at least one diagram here
  ### Code: <caption>            ← annotated code block
## Results / Tradeoffs           ← evidence or comparison
## Conclusion                    ← recap + call to action
## References                    ← optional, links and credits
```

## Diagram Guidelines

### When to Use Which Diagram Type

| Situation | Diagram type | Tool |
|-----------|-------------|------|
| Request/response flow between services | Sequence diagram | Mermaid |
| System components and their connections | C4 container or component | Mermaid |
| Decision tree or process steps | Flowchart | Mermaid |
| Database tables and relationships | Entity-Relationship diagram | Mermaid |
| State transitions | State diagram | Mermaid |
| Simple layout or structure that does not need interactivity | ASCII art | Plain text |
| Timeline or release plan | Gantt chart | Mermaid |

### Mermaid Best Practices

1. **One concept per diagram.** Split complex flows into multiple diagrams rather than cramming everything into one.
2. **Caption every diagram.** Use a heading or bold text immediately before the fenced block.
3. **Use readable node IDs.** `AuthService` not `A`, `UserDB` not `DB1`.
4. **Avoid styling directives.** Let the renderer handle colors; do not embed `style` or `classDef` since they break across themes.
5. **Keep labels short.** Edge labels over 5-6 words become unreadable; move detail into prose.
6. **Escape special characters.** Wrap labels containing parentheses, colons, or commas in double quotes.

### ASCII Art Best Practices

Use ASCII art when:
- The diagram is simple enough that Mermaid adds unnecessary complexity
- The target medium does not render Mermaid (e.g. terminal output, plain-text emails)
- You want to show a compact layout inline with code

Wrap ASCII art in a fenced code block with no language tag to preserve alignment.

## Code Block Guidelines

1. **Annotate, do not narrate.** Comments in code examples should explain *why*, not *what*.
2. **Highlight the relevant part.** If showing a large file, use `// ...` to truncate irrelevant sections.
3. **Specify the language tag.** Always include the language in the fenced code block for syntax highlighting.
4. **Show input and output together** when demonstrating CLI commands or API calls.
5. **Keep examples runnable.** A reader should be able to copy-paste and get the expected result.

## Writing Style

- **Lead with the diagram.** Place the most important diagram early in the post, before readers lose context.
- **Refer to diagrams explicitly.** Use phrases like "as shown in the sequence diagram above" to connect prose and visuals.
- **Use progressive disclosure.** Start with a high-level overview diagram, then zoom into specifics in later sections.
- **Avoid wall-of-text sections.** If a section runs longer than three paragraphs without a visual element, consider adding a diagram, code block, or callout.
- **Write for skimmers.** Use headings, bold key terms, and bullet lists so readers can scan for the section they need.

## Checklist

Before publishing, verify:

- [ ] Post has at least one Mermaid diagram or ASCII art illustration
- [ ] Every diagram has a caption (heading or bold text)
- [ ] Mermaid blocks render correctly (no styling directives, readable node IDs, escaped special chars)
- [ ] Code blocks specify a language tag and are copy-pasteable
- [ ] No section exceeds three paragraphs without a visual break
- [ ] TL;DR section is present and summarizes the post in 2-3 sentences
- [ ] Diagrams are referenced in the surrounding prose
- [ ] Progressive disclosure: overview diagram first, details later
