---
name: organize-docs-from-zip
description: >-
  Unpacks a user-provided documentation zip, normalizes Markdown into magj.dev
  content layout (blog vs references), matches site voice and frontmatter, and
  stages files with draft flags and a human review handoff. Use when the user
  attaches or paths to a .zip of docs (e.g. samples.file.zip), asks to import or
  organize bundled Markdown for the blog or references, or prepare zip content
  for publication review.
---

# Organize docs from zip (magj.dev)

## When this applies

The user supplies a **local zip path** (for example `./samples.file.zip`). The agent unpacks safely, classifies each Markdown file, writes or proposes paths under `src/content/blog/` or `src/content/references/`, aligns tone with the site, and **does not** treat the result as published until a human confirms.

This is a **local editorial workflow**. It complements (does not replace) the admin References zip pipeline described in [reference.md](reference.md).

## Quick checklist

```
- [ ] Confirm zip path; refuse if missing or not a file
- [ ] Inspect archive (list entries; no path traversal)
- [ ] Extract to a disposable staging directory under the repo or /tmp
- [ ] Parse each .md: frontmatter + body; classify blog vs references
- [ ] Normalize frontmatter to project Zod schemas (see reference.md)
- [ ] Choose filenames (kebab-case slugs); avoid overwriting without explicit user OK
- [ ] Edit prose for magj.dev tone (see Tone)
- [ ] Set draft for human review (blog defaults draft; force draft on references until publish)
- [ ] Leave REVIEW.md or inline PR notes: sources, assumptions, open questions
```

## Safe unpack

1. **List only first**: `unzip -l <zip>` (or equivalent) to see paths and sizes.
2. **Reject** entries containing `..`, absolute paths, or non-UTF-8 names you cannot normalize.
3. **Extract** to something like `.staging/docs-import-<date>/` (gitignored if needed) or `/tmp/magj-docs-import/`.
4. Respect rough limits aligned with production zip handling: on the order of **tens of Markdown files** and **tens of MB** uncompressed; if larger, stop and ask to split the archive.

Do not execute binaries from the zip. Only treat `.md` (and optionally `.mdx` if the project supports it—this repo uses `.md` in content loaders) as first-class import targets.

## Classify: blog vs references

| Signal | Prefer collection |
|--------|-------------------|
| Long-form narrative, dated post, tags like a blog | `blog` |
| Short entry pointing at an external canonical URL | `blog` with `externalUrl` if the schema in use supports it—**verify** `src/content.config.ts` before adding fields |
| Curated reading list / link page, stable “reference” doc | `references` |
| User explicitly says “blog” or “references” | As specified |

If the active `content.config.ts` differs from [reference.md](reference.md), **the repo file wins**.

## Tone (magj.dev)

- Clear, technical, complete sentences—**not** telegraphic bullet chains as the only prose.
- Prefer short paragraphs; explain decisions where useful.
- Match existing posts: read one or two current files from `src/content/blog/` and `src/content/references/` before heavy rewriting.
- For deep edits, follow [edit-article](../edit-article/SKILL.md) and [blog-post-with-diagrams](../blog-post-with-diagrams/SKILL.md) when diagrams help.

## Frontmatter and drafts

- **Blog** (`src/content/blog/`): `title`, `summary`, `publishedAt` required per schema; keep **`draft: true`** until the human approves.
- **References** (`src/content/references/`): `title`, `description`, `date` required; set **`draft: true`** for this workflow even though the schema default may be false—human toggles off when publishing.

Normalize dates to `YYYY-MM-DD`. Derive missing titles from the first H1 or filename. Add sensible `tags` from content.

## Slugs and collisions

- Filename = kebab-case slug + `.md`.
- If a path already exists, **do not overwrite**: use a suffix (`-import`, `-2`) or stop and list options for the user.

## Handoff for human review

Deliver:

1. **Table of files**: source path in zip → repo path → collection → draft status.
2. **Assumptions**: anything inferred (dates, tags, blog vs references).
3. **Checks**: suggest `bun run lint` and `bun run build` (or project-standard commands) after edits.
4. **Do not** merge or deploy unless the user explicitly asks.

## Additional detail

- Schema tables and zip pipeline alignment: [reference.md](reference.md)
