---
name: dotcms-best-practices
description: Reference for doing any single thing in dotCMS correctly — create a content type, page, template or container; place content; author VTL; wire a headless Next.js frontend; or debug a page that renders blank. Indexed by intent, so you load one file for the task at hand. Use whenever working with dotCMS content types, fields, pages, templates, containers, content placement, VTL/Velocity, the Universal Visual Editor, or a headless dotCMS frontend — and especially when a page renders empty, a slot shows "no component", or a change doesn't appear in LIVE.
---

# dotCMS Best Practices

The reference for **one task at a time**. Load the file for what you're doing — never the folder.

Also serves as the build reference for the `dotcms-create-sites` skill, which plans a whole site
and then works through these files in dependency order. If you're building a complete site from
scratch, start there instead.

## Read this first

**A missing piece yields a blank or shell-only page with HTTP 200 — never an error.** That single
fact shapes everything here: you cannot trust a successful response as evidence that anything
rendered. Every build path ends in an explicit verify step.

Before building anything, know the wiring contract — [reference/core/00-what-must-exist.md](reference/core/00-what-must-exist.md).
Four requirements, both delivery modes: a published site · a page pointing at a published template
whose named containers already exist · content placed into a slot · everything published, page last.

**Then establish the delivery mode**, because it changes which files apply:

| Mode | dotCMS renders? | You need |
|---|---|---|
| **VTL-rendered** | yes — theme + container VTL | `core/` + `vtl/` |
| **Headless** | no — it serves the page, an app renders it | `core/` + `nextjs/` |

If the user hasn't said, ask. Guessing wrong wastes the whole build.

## I want to…

**Content model**

| Task | File |
|---|---|
| Create or publish a site | [core/01-site.md](reference/core/01-site.md) |
| Create or change a content type, add fields | [core/02-content-types.md](reference/core/02-content-types.md) |
| Create content | [core/03-content.md](reference/core/03-content.md) |

**Pages and rendering scaffold**

| Task | File |
|---|---|
| Create a page | [core/04-pages.md](reference/core/04-pages.md) |
| Build or change a template — layout, rows, columns | [core/05-templates.md](reference/core/05-templates.md) |
| Set up a container (a slot content goes into) | [core/06-containers.md](reference/core/06-containers.md) |
| Put content onto a page | [core/09-placement.md](reference/core/09-placement.md) |

**VTL-rendered delivery**

| Task | File |
|---|---|
| Know what VTL mode adds, and see the whole tree you must author | [vtl/00-wiring.md](reference/vtl/00-wiring.md) — **nothing scaffolds VTL; start here** |
| Decide how something should render — content type vs widget vs detail page | [vtl/01-choose-mechanism.md](reference/vtl/01-choose-mechanism.md) |
| Build a theme — HTML shell, grid, SEO | [vtl/02-themes.md](reference/vtl/02-themes.md) |
| Write container markup | [vtl/03-containers.md](reference/vtl/03-containers.md) |
| Build a listing page or a URL-mapped detail page | [vtl/04-listings-and-details.md](reference/vtl/04-listings-and-details.md) |
| Look up VTL/Velocity syntax while writing `.vtl` | [vtl/velocity.md](reference/vtl/velocity.md) |

**Headless delivery (Next.js)**

| Task | File |
|---|---|
| Connect an app to dotCMS and render a page | [nextjs/00-connect.md](reference/nextjs/00-connect.md) — §A is yours in every case; §B is what `dotcms init` already wrote |
| Register a component for a content type | [nextjs/01-component-contract.md](reference/nextjs/01-component-contract.md) |
| Configure `next.config` | [nextjs/02-next-config.md](reference/nextjs/02-next-config.md) |
| Set up routing | [nextjs/03-routing.md](reference/nextjs/03-routing.md) |
| Build a listing or detail route | [nextjs/04-listings-and-details.md](reference/nextjs/04-listings-and-details.md) |

Next.js is the only framework branch here. Angular, Vue and Astro have upstream examples in
`dotCMS/core` but no branch in this skill. The SDK APIs belong to the `@dotcms/client`,
`@dotcms/react` and `@dotcms/uve` READMEs — these files cover the seam, never the API surface.

## Something is wrong

| Symptom | Start here |
|---|---|
| Page renders blank, or only the shell | [core/00-what-must-exist.md](reference/core/00-what-must-exist.md), then your mode's `00` |
| A slot renders "no component for X" | [nextjs/01-component-contract.md](reference/nextjs/01-component-contract.md) — the map key must equal the content type's Velocity variable, **case-exact** |
| A VTL slot renders empty with no error | [vtl/05-verify-and-debug.md](reference/vtl/05-verify-and-debug.md) — errors are swallowed into an empty string with HTTP 200 |
| A whole page is a bare shell whatever you place | `template.vtl` isn't looping `$dotThemeLayout` — [vtl/02-themes.md](reference/vtl/02-themes.md) |
| Theme, header and footer render but every slot is missing | Either the missing layout loop above, or a hand-rolled `#parseContainer` — [vtl/02-themes.md](reference/vtl/02-themes.md) |
| Container assembly broken | An empty `preloop.vtl` or `postloop.vtl`; they must be non-empty — [core/06-containers.md](reference/core/06-containers.md) |
| A template's container path doesn't resolve | Paths must be host-qualified `//<site>/application/containers/<name>/` — [core/06-containers.md](reference/core/06-containers.md) |
| Content exists but doesn't appear | Placement is a full replacement, and LIVE only changes on publish — [core/09-placement.md](reference/core/09-placement.md) |
| A layout change didn't take effect | Re-publish the template — [core/05-templates.md](reference/core/05-templates.md) |
| The right content renders in the wrong shape | Wrong mechanism chosen — [vtl/01-choose-mechanism.md](reference/vtl/01-choose-mechanism.md) |
| Verifying a headless page | [nextjs/05-verify.md](reference/nextjs/05-verify.md) — `page_verify` does **not** apply; confirm every type on the page resolves to a component |
| Verifying a VTL page | [vtl/05-verify-and-debug.md](reference/vtl/05-verify-and-debug.md) — validate through `/api/vtl/dynamic` **and** `page_verify` |

## Rules that bite

Four things that cause most failures, stated once so you don't have to hit them:

1. **Identifiers are case-exact.** A container's `<Var>.vtl` filename and a headless component-map
   key must both equal the content type's Velocity variable exactly. Wrong case renders nothing.
2. **Containers are folders.** There is no create endpoint — you build the folder and its files.
3. **Placement replaces.** Omitted slots are cleared, not left alone.
4. **Publishing is explicit and ordered.** LIVE changes only on publish, and the page publishes
   last — after content, placement, or a template edit.

And one that isn't a build failure but matters: a headless project's
`NEXT_PUBLIC_DOTCMS_AUTH_TOKEN` **ships to the browser**, and a scaffolded project's token carries
the permissions of whoever ran the CLI. It is development-only — see
[nextjs/00-connect.md §B.1](reference/nextjs/00-connect.md).

## Tool routing

Authoring goes through the dotCMS MCP tools: `page_create`, `page_place_content`, `page_verify`,
`upload_assets`, `download_assets`, `search`, `execute`. **Each tool's own description is the source
of truth for how to call it.** These files cover only what the tools don't say — which tool to reach
for, and the dotCMS behaviors that live outside any single call.

Reach for `execute` only when no dedicated tool fits. Run raw VTL through
`POST /api/vtl/dynamic`. What `search` returns is the source of truth for anything the curated
OpenAPI spec expresses; these files keep what the spec can't.

## Index by build step

If you're working through a full build rather than a single task, the same files are indexed in
dependency order in [reference/README.md](reference/README.md).
