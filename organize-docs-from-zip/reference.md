# Reference: schemas and zip alignment

## Content config (verify in repo)

Paths and fields live in `src/content.config.ts`. As of the skill’s authoring, the collections are:

### `blog` (`./src/content/blog/**/*.md`)

| Field | Notes |
|-------|--------|
| `title` | string, required |
| `summary` | string, required |
| `publishedAt` | date, required |
| `updatedAt` | optional |
| `draft` | boolean, default `true` in schema |
| `coverImage` | optional path string |
| `coverImageCaption` | optional |
| `author` | optional |
| `tags` | string array, default `[]` |

### `references` (`./src/content/references/**/*.md`)

| Field | Notes |
|-------|--------|
| `title` | string, required |
| `description` | string, required |
| `date` | date, required |
| `updated` | optional |
| `draft` | boolean, default `false`—**override to `true`** for zip-import review workflow |
| `order` | number, default `0` |
| `tags` | string array, default `[]` |

## Production References zip pipeline (context only)

Admin upload uses a worker with safe unzip and caps (see `lambda/src/content-pipeline/zip-to-md.ts`):

- `MAX_ZIP_FILES = 40`
- `MAX_UNCOMPRESSED_BYTES = 20 * 1024 * 1024`

Only paths that map cleanly under `src/content/references/` are accepted there. **Local agent imports** can also target `blog/` and should follow the same **safety** mindset (no `..`, reasonable size/count).

## `externalUrl` / bookmarks

Some forks or older schemas use `externalUrl` for bookmark-style posts. **Check `src/content.config.ts`** before adding fields the Zod schema does not define.
