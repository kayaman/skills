---
name: linked-data
description: >-
  Applies Tim Berners-Lee's linked data principles (four rules, dereferencing,
  browsable graphs, FOAF/seeAlso, 5-star linked open data). Use when designing or
  reviewing RDF publishing, HTTP URIs for things, 303 redirects, SPARQL endpoints,
  semantic web data linking, or explaining LOD and open data star ratings.
---

# Linked data

## When to apply

Use this skill when the task touches **RDF on the web**, **cool URIs**, **dereferencing**, **linking datasets**, or **open-data publishing** - not for generic REST APIs unless the conversation is explicitly about RDF graphs and `URI`/`HTTP` lookup patterns.

## MUST

- **Read the canonical note** in [LinkedDataDesignIssues.md](LinkedDataDesignIssues.md) before giving detailed guidance; prefer its wording and structure over paraphrase when citing rules.
- **Preserve** the four expectations as behavioral norms (URI names, HTTP URIs, useful representations on lookup, links to other URIs) - see the note's numbered list and "four rules" section.
- **Distinguish** Linked Data from Linked Open Data (licence / openness) when the user asks about stars, government data, or "LOD".

## SHOULD

- Point implementers at **SPARQL**, **RDF** syntax choices, and **303** where the note discusses variations (hash URIs vs slash URIs, `seeAlso`, browsable graphs).
- Mention **trade-offs** of fully browsable graphs (duplication, consistency) when relevant.
- Use **relative links** inside this repo to `LinkedDataDesignIssues.md`; do not assume the W3C HTML snapshot path on disk.

## MAY

- Add explicit fragment IDs in Markdown headings elsewhere (e.g. `{#fivestar}`) when mirroring the note's anchors.

## Primary reference

| Resource | Role |
| -------- | ---- |
| [LinkedDataDesignIssues.md](LinkedDataDesignIssues.md) | Full converted Design Issues note (source: `https://www.w3.org/DesignIssues/LinkedData.html`) |

## Quick checklist

```
- [ ] Confirmed the user means RDF/HTTP-linked data (not only JSON hypermedia)
- [ ] Re-read or skim LinkedDataDesignIssues.md for the section in scope
- [ ] Stated the four rules or linked to them explicitly
- [ ] Called out openness only when the question is about LOD or star ratings
```
