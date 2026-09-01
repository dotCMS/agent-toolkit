# 00 · VTL wiring

**Every file below is yours to author** — VTL mode has no app scaffold to inherit, so read
this before building anything. If you're working in an existing site, list
`/application/themes/` and `/application/containers/` first and extend what's there rather
than duplicating it.

In addition to [core/00](../core/00-what-must-exist.md), a VTL-rendered page needs:

1. **Template → theme.** The theme's `template.vtl` must loop `$dotThemeLayout`;
   without that loop the page is a bare shell whatever you place ([02](02-themes.md)).
2. **Container → non-empty `preloop.vtl`/`postloop.vtl` + one `<Var>.vtl` per content
   type**, filename = the type's Velocity variable, case-exact ([03](03-containers.md)).
3. **Each item renders through the right mechanism** — content section, widget or
   detail page ([01](01-choose-mechanism.md)). Wrong mechanism renders empty.

Verify in LIVE ([05](05-verify-and-debug.md)). A VTL error is swallowed into an empty
string with HTTP 200, so "no error" is not evidence that anything rendered.

## The tree you are creating

Everything lives under `/application/` on the site. Nothing goes in `/assets` — that path is
reserved ([core/03](../core/03-content.md)).

```
/application/
  themes/<name>/
    template.vtl          REQUIRED — html shell + the $dotThemeLayout loop
    <partial>.vtl         optional, included via ${dotTheme.path}<name>.vtl
  containers/<name>/
    container.vtl         REQUIRED — metadata only, $dotJSON.put
    preloop.vtl           REQUIRED — must be non-empty, a comment is enough
    postloop.vtl          REQUIRED — must be non-empty; an empty one breaks assembly
    <Var>.vtl             REQUIRED — one per accepted content type, case-exact filename
  vtl/<name>.vtl          optional — shared includes, listing/detail bodies
```

Three of those are required-but-easy to leave out, and each fails silently:

| Missing | What you see |
|---|---|
| the `$dotThemeLayout` loop | theme, header and footer render; **every content slot is missing** |
| a non-empty `postloop.vtl` | container assembly breaks |
| a `<Var>.vtl` for a placed type | that slot renders empty, HTTP 200, no error anywhere |

Templates reference containers by **host-qualified path** —
`//<site>/application/containers/<name>/`. A relative path resolves against whatever site is
current, which may not be yours, and a path that doesn't resolve gives you an empty slot with
no error ([core/06](../core/06-containers.md)).

## Author locally, then upload

Write these files on disk first and push them with `upload_assets` — never inline bytes, and
never author directly in the instance. Local files are far faster to iterate on: you can diff
them, keep them in git, and re-upload a single file after a change instead of hunting through
the Site Browser.

**Mirror the dotCMS path in your local tree.** If the local layout matches
`/application/...` exactly, the upload path for any file is its own relative path — no mapping
to maintain and nothing to get wrong.

Upload order matters, because a template's POST names container paths that must already
resolve and a theme id that must already exist:

```
theme files → container folders → create + publish the template → pages → content → placement
```

That is the same dependency order as [reference/README.md](../README.md); the theme and
containers are just files, so they go up before anything references them.

## Then

- Choosing how each thing renders → [01-choose-mechanism.md](01-choose-mechanism.md)
- The theme and its layout loop → [02-themes.md](02-themes.md)
- Per-type container markup → [03-containers.md](03-containers.md)
- Listings and URL-mapped detail pages → [04-listings-and-details.md](04-listings-and-details.md)
- Verifying, and triaging a blank render → [05-verify-and-debug.md](05-verify-and-debug.md)
- VTL syntax while you write → [velocity.md](velocity.md)
