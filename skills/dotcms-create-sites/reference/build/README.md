# Build reference — index

Phase 2 of the skill. **Load only the file for the step you're on** — don't read the
folder up front.

The build forks by **delivery mode**, decided in Phase 1 and recorded in PLAN.md §3b:

| Mode | You build | Branch |
|------|-----------|--------|
| **VTL-rendered** | dotCMS renders the HTML: theme + container VTL | `core/` + `vtl/` |
| **Headless** | dotCMS serves the page; a front-end app renders it | `core/` + a framework branch (`nextjs/`) |

## core/ — both modes

| # | File | You're doing… |
|---|------|---------------|
| 00 | [core/00-what-must-exist.md](core/00-what-must-exist.md) | The wiring contract — read first |
| 01 | [core/01-site.md](core/01-site.md) | Creating and publishing the site — do this first |
| 02 | [core/02-content-types.md](core/02-content-types.md) | Content types + fields |
| 03 | [core/03-content.md](core/03-content.md) | Creating content — firing an action on a contentlet |
| 04 | [core/04-pages.md](core/04-pages.md) | Creating pages |
| 05 | [core/05-templates.md](core/05-templates.md) | Templates — layout, publish, container identifiers |
| 06 | [core/06-containers.md](core/06-containers.md) | Containers as slots — the folder scaffold |
| 09 | [core/09-placement.md](core/09-placement.md) | Placing content into page slots |

## vtl/ — VTL-rendered only

| # | File | You're doing… |
|---|------|---------------|
| 00 | [vtl/00-wiring.md](vtl/00-wiring.md) | The extra requirements VTL adds |
| 01 | [vtl/01-choose-mechanism.md](vtl/01-choose-mechanism.md) | Content type vs widget vs detail page |
| 02 | [vtl/02-themes.md](vtl/02-themes.md) | Theme — HTML shell, grid, SEO macro |
| 03 | [vtl/03-containers.md](vtl/03-containers.md) | Container VTL — `<Var>.vtl` per content type |
| 04 | [vtl/04-listings-and-details.md](vtl/04-listings-and-details.md) | Listing pages + URL-mapped detail pages |
| 05 | [vtl/05-verify-and-debug.md](vtl/05-verify-and-debug.md) | Two-layer verify + blank-render triage |
| — | [vtl/velocity.md](vtl/velocity.md) | VTL authoring lookup — consult while writing `.vtl` |

## nextjs/ — headless mode, Next.js

| # | File | You're doing… |
|---|------|---------------|
| 00 | [nextjs/00-connect.md](nextjs/00-connect.md) | What headless changes in dotCMS, client config, rendering |
| 01 | [nextjs/01-component-contract.md](nextjs/01-component-contract.md) | Content type variable = component key |
| 02 | [nextjs/02-next-config.md](nextjs/02-next-config.md) | `next.config` — dotCMS image loader, `/dA/` rewrite, UVE + StrictMode |
| 03 | [nextjs/03-routing.md](nextjs/03-routing.md) | Catch-all routing and the five-step route shape |
| 04 | [nextjs/04-listings-and-details.md](nextjs/04-listings-and-details.md) | Listings + urlmap detail pages (`urlContentMap`) |
| 05 | [nextjs/05-verify.md](nextjs/05-verify.md) | Verifying a headless render (`page_verify` does not apply) |

**The two branches share a spine.** `00` wire up · `01` type↔renderer contract ·
`02`–`03` mode-specific plumbing · `04` listings & detail · `05` verify. Steps 00, 01,
04 and 05 are direct counterparts; 02–03 differ because the modes genuinely differ
(VTL needs a theme and container markup, headless needs app config and routing).

The SDK APIs are owned by their own npm READMEs — `@dotcms/client`, `@dotcms/react`,
`@dotcms/uve` — and by the `examples/nextjs` app in `dotCMS/core`. This branch shows
the basics and links for the detail; it must never restate the API surface.

**Next.js is the only framework documented here.** dotCMS also ships `@dotcms/angular`
and `@dotcms/vue`, with `angular`, `angular-ssr`, `astro` and `vuejs` example apps in
`dotCMS/core/examples`. Those would be sibling branches. Do **not** apply this branch's
routing, `next.config` or `next/image` guidance to them — only `core/` and the general
shape (connect → render → component contract) carry over.

## Tools (read once)

All authoring goes through the dotCMS MCP tools — `page_create`, `upload_assets` /
`download_assets`, `page_place_content`, `page_verify`, `execute`, and `search`.
**Each tool's own description is the source of truth for how to call it and the traps
it absorbs.** These files cover only what the tools don't say: which tool to reach for
at each step, and the dotCMS behaviors that live outside any single call. Reach for
`execute` only when no dedicated tool fits; run raw VTL via `POST /api/vtl/dynamic`.

## Spec status (read once)

Many traps ship in the curated OpenAPI spec, so what the `search` tool returns is the
source of truth for them. These files keep what the spec **can't** express: traps on
endpoints not in the spec, and behavioral details no annotation captures. A few are
**corrections** where earlier guidance was inaccurate — flagged inline.
