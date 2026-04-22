---
name: HTML to Markdown LOD
overview: Convert the saved W3C "Linked Data" Design Issues article from HTML to clean GitHub-flavored Markdown, excluding injected browser-extension markup at the end of the file, and write the result beside the source (or optionally into your linked-data skill folder).
todos:
  - id: strip-extension-html
    content: Truncate or extract body-only HTML; exclude rreader/browser-mcp tail from line ~535
    status: completed
  - id: pandoc-or-fallback
    content: Run pandoc html→markdown (or Python fallback) on cleaned HTML
    status: completed
  - id: touchup-md
    content: Fix pre/<br>, optional heading anchors, frontmatter, image path
    status: completed
  - id: write-linkeddatadesignissues-md
    content: Save LinkedDataDesignIssues.md beside source; optionally copy to skills/linked-data
    status: completed
isProject: false
---

# Convert LinkedDataDesignIssues.html to Markdown

## Source and scope

- **Input:** [`/home/kayaman/Projects/LinkedDataDesignIssues.html`](/home/kayaman/Projects/LinkedDataDesignIssues.html)
- **Real content ends** after the final paragraph linking to [Tim BL](https://www.w3.org/People/Berners-Lee) (around line 532). Everything from `<div id="rreader-annotations-notifications"` / `<browser-mcp-container` onward (line 535+) is **not** part of the article and must be **stripped** before conversion.

## Recommended approach

1. **Produce a minimal clean HTML fragment** (one-off file or stdin) containing only:
   - A proper document wrapper: `<html><head><meta charset="utf-8"><title>…</title></head><body>…</body></html>`
   - The **body** subtree from the original from `<address>` through the last `<p><a href="…Berners-Lee">Tim BL</a></p>`, with no extension junk.

2. **Convert with Pandoc** (if available: `pandoc --version`):
   - `pandoc cleaned.html -f html -t markdown` with options such as `--wrap=none` (or `preserve`) so paragraphs are not hard-wrapped awkwardly.
   - Pandoc will map: `h1`–`h3` → `#`–`###`, `ol`/`ul` → lists, `a` → `[text](url)`, `blockquote` → `>`, `table` (5-star section) → a GFM pipe table, `hr` → `---`, and `pre` → fenced code blocks.

3. **Manual touch-ups** (quick pass in the generated `.md`):
   - **`<pre>` blocks** in the source embed `<br>` as line breaks; if Pandoc leaves literal `<br>` inside fences, replace with real newlines.
   - **Headings with anchors** (e.g. `<h2><a id="browsable" …>Browsable graphs</a></h2>`): ensure the Markdown heading text is correct; optionally add explicit IDs if your renderer supports it: `## Browsable graphs {#browsable}`.
   - **`<small>`** (URI, RDF, etc.): usually becomes plain text; no change needed unless you want emphasis.
   - **Image:** the cafepress mug uses `./LinkedDataDesignIssues_files/597992118v2_350x350_Back.jpg` — keep that relative path so the image still resolves next to the `_files` folder, or switch to the W3C diagram URL from the original page if you prefer no local asset dependency.
   - **Optional YAML frontmatter** at the top: `title`, `source: https://www.w3.org/DesignIssues/LinkedData.html`, author, date from the `<address>` block.

4. **Write output** to [`/home/kayaman/Projects/LinkedDataDesignIssues.md`](/home/kayaman/Projects/LinkedDataDesignIssues.md) next to the HTML (default). **Optional:** also copy or symlink into [`/home/kayaman/Projects/skills/linked-data/`](/home/kayaman/Projects/skills/linked-data/) if you want this doc to back the linked-data skill.

## Fallback if Pandoc is missing

- Use `pip install html2text` or a small **Python** script with **BeautifulSoup** / **html.parser**: walk `body`, emit headings, paragraphs, lists, links, and tables by hand; same strip-and-scope rules as above.

## Verification

- Open the `.md` in a preview (VS Code / Cursor): check the five-star table, code fences (N3 / RDF/XML examples), and that no Tailwind or `browser-mcp` text appears.
- Compare section count to the original: intro, four rules, basic lookup, 303 variation, FOAF/seeAlso, browsable graphs, limitations, query services, 5-star LOD, conclusion, followup.

## Fidelity note

Preserve **original wording** (including known typos like "seeAslo", "mBrowse-ableust") unless you explicitly want an editorial pass; the task is format conversion, not copyediting.
