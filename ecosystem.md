# dotCMS CLI + SDK inventory

**Captured:** 2026-08-31 · **Sources:** npm registry, `dotcms/core` working tree, `dotcli.md`

Reference only — what exists, where it lives, what version it is. No analysis.
Interpretation and open issues live in `context/findings.md` and `context/decisions.md`.

---

## CLIs

Things a developer invokes as a command.

| | `@dotcms/create-app` | `@dotcms/dotcli` |
|---|---|---|
| Command | `create-dotcms-app` | `dotcli` |
| npm version | `26.8.31-1` | `26.8.31-1` |
| In-repo version | `1.2.5` | — |
| Source | `core-web/libs/sdk/create-app` | `core/tools/dotcms-cli` (365 `.java` files) |
| Language | TypeScript | Java/Quarkus; TypeScript rewrite specced 2026-08-26 |
| First published | 2026-01-07 | 2024-02-07 |
| Status | Beta ("Behavior and flags may change") | Rewrite "Decided — ready to build" |
| Purpose | Provision dotCMS (Docker or existing instance), scaffold a frontend, configure UVE | Move files between a local folder and dotCMS |
| How the bin is installed | `bin` field | `postinstall` symlinks a platform binary using the `alias` field |

`dotcli` npm package ships three native binaries — `dotcms-cli-26.08.31-01-{linux-x86_64,
osx-aarch_64, osx-x86_64}` — plus `src/postinstall.js`. Internal `packageName` is `dotcms-cli`,
`alias` is `dotcli`.

### create-app command surface

```
create-dotcms-app [projectName] [options]
  -f, --framework <nextjs|astro|angular|angular-ssr>
  -d, --directory <path>
  --local                     local dotCMS via Docker
  --starter <url>             custom starter ZIP (implies --local)
  --url <url>                 existing instance
  -u, --username <username>
  -p, --password <password>
  -V, --version
```

Framework aliases: `next`/`next.js` → `nextjs`, `ng` → `angular`, `angular-server` →
`angular-ssr`. Local mode uses ports 8082, 8443, 9200, 9600 and default credentials
`admin@dotcms.com` / `admin`.

### dotcli command surface (specced, TypeScript rewrite)

```
login --env <url>            sites · ls <path> · tree <path> [--depth n]
pull <path> · pull           status · diff [path]
push [path] · push --force   rm <path> [--destroy]
publish [path]               unlock <path>
doctor [--env url]
```

Exit codes: `0` success · `1` generic · `2` auth/token expired · `3` rejected, remote moved ·
`4` unresolved conflicts · `5` partial · `6` permission denied.

---

## Server packages

| | `@dotcms/mcp-server` |
|---|---|
| Bin | `dotcms-mcp-server` (spawned by an AI client over stdio, not typed by a user) |
| npm version | `0.0.13` |
| In-repo version | `0.1.0-beta.2` |
| Source | `core-web/apps/mcp-server` |
| Built on | `@dotcms/ai` — imports `@dotcms/ai/runtime` and `@dotcms/ai/spec` |

### Tools exposed

`core-web/apps/mcp-server/src/tools/`

| Tool | Notes |
|---|---|
| `search` | imports `@dotcms/ai/runtime` + `@dotcms/ai/spec` |
| `execute` | runs a JavaScript async function body (max 100,000 chars) against the dotCMS API via the sandbox's `api` adapter |
| `upload_assets` | |
| `download_assets` | |
| `page_create` | |
| `page_verify` | |
| `page_place_content` | |

---

## SDK libraries

`core-web/libs/sdk/` — all published at `26.8.31-1`, none ship a bin.

| Package | In-repo version | Purpose |
|---|---|---|
| `@dotcms/client` | `1.2.0` | JS library for the dotCMS REST APIs — `createDotCMSClient`, page fetch, GraphQL, collections |
| `@dotcms/types` | `1.2.0` | Shared TypeScript definitions |
| `@dotcms/uve` | `1.1.1` | Universal Visual Editor bridge — `isRequestFromUVE` |
| `@dotcms/react` | `1.2.6` | React renderer — `DotCMSLayoutBody`, `useEditableDotCMSPage` |
| `@dotcms/angular` | `1.1.1` | Angular renderer |
| `@dotcms/vue` | `1.5.5` | Vue renderer |
| `@dotcms/ai` | `1.5.6` | Agentic runtime — a library you import; see below |
| `@dotcms/analytics` | `0.0.1-beta.2` | Content Analytics |
| `@dotcms/experiments` | `1.0.1` | A/B experiments |
| `create-app` | `1.2.5` | the CLI above |

### `@dotcms/ai`

A package you `npm install` into your own project — no bin, no command. Per its README: the
model writes code and the runtime runs it in a sandbox against the whole dotCMS API, with auth
and policy in one place. Stated properties:

- the caller's token never enters the sandbox; auth is injected host-side
- adapters are the only way out — `fetch`, `require`, `process.env` are removed
- an allow-list (or typed `defineAdapter` operations) bounds the reachable surface

README also states it is the layer dotCMS's own MCP server and first-party agents run on.

---

## Frontend examples

`core/examples/` — fetched at runtime by `create-app` via blobless sparse checkout of
`dotCMS/core` at `main`, then `sparse-checkout set examples/{framework}`.

| Example | Offered by create-app? |
|---|---|
| `nextjs` | yes |
| `astro` | yes |
| `angular` | yes |
| `angular-ssr` | yes |
| `nextjs-experiments` | no |
| `vuejs` | no |

The `nextjs` example maps 13 content types in `src/components/content-types/index.ts`:
`Activity`, `Banner`, `BannerCarousel`, `calendarEvent`, `CallToAction`, `CategoryFilter`,
`Image`, `Product`, `SimpleWidget`, `StoreProductList`, `VtlInclude`, `webPageContent`,
`YouTube` — plus a `CustomNoComponent` fallback key. It also carries demo-specific routes
(`/blog`, `blog/post/[[...slug]]`) and components (`BlogCard`, `DestinationListing`), and
`SearchResult.tsx` branches on `Blog`, `Activity`, `Product` and queries `Destination`.

---

## Versioning and release

- **Lockstep:** every `@dotcms/*` package publishes at the exact version of the dotCMS release
  it was built for (dotCMS `26.7.14-1` → `@dotcms/client@26.7.14-1`). In-repo `package.json`
  versions are dev-only; `nx release` rewrites them at publish.
- **Version resolution:** `currentVersionResolver: "git-tag"`, `fallbackCurrentVersionResolver:
  "disk"`, publishing from `dist/{projectRoot}`.
- The instance advertises the oldest SDK version it supports; SDKs self-check and warn in the
  console when too old.
- LTS releases get no matching SDK version — docs direct users to the closest regular release
  at or before their LTS.
- `@dotcms/mcp-server@0.0.13` is the only package not on the lockstep train.
- **Build:** `@nx/esbuild`, ESM, `platform: node`, bundled, `thirdParty: true`. Shebang banner
  injected only in the `production` configuration.
- dotcli MVP distribution is npm only; standalone binaries (bun compile) only if a customer's
  CI cannot run Node.

---

## npm namespace

**Ours, published:** `@dotcms/ai` · `@dotcms/analytics` · `@dotcms/angular` · `@dotcms/client` ·
`@dotcms/create-app` · `@dotcms/dotcli` · `@dotcms/experiments` · `@dotcms/mcp-server` ·
`@dotcms/react` · `@dotcms/types` · `@dotcms/uve` · `@dotcms/vue`

**Unclaimed:** `@dotcms/cli` · `dotcms-cli` · `create-dotcms`

**Command names:** `dotcli`, `create-dotcms-app`, `dotcms-mcp-server` are taken by us. A bare
`dotcms` command is not taken.

**Legacy / stray / third-party on the registry:**

| Name | Version | Note |
|---|---|---|
| `dotcli-test` | `24.4.2` | describes itself as "Official command-line tool to manage dotCMS content" |
| `dotcms-cli-demo` | `1.3.2` | "Demo - dotCMS CLI with NPM registry distribution" |
| `dotcms-js` | `4.2.0-b100` | legacy Angular UI app |
| `dotcms-ui` | `5.1.6-…` | legacy |
| `dotcms-models` | `0.0.12` | legacy interfaces/models |
| `dotcms-ema-elements` | `0.0.2` | legacy Edit Mode Anywhere web components |
| `dotcms-client` | `2.0.0` | third-party blog-post example |
| `@willowtreeapps/dotcms-utils` | `1.0.1` | third-party "CLI and utilities library for dotCMS" |

---

## Monorepo locations

```
core/
  tools/dotcms-cli/                 current Java dotcli (365 .java files)
  examples/{nextjs,nextjs-experiments,astro,angular,angular-ssr,vuejs}
  core-web/
    libs/sdk/{ai,analytics,angular,client,create-app,experiments,react,types,uve,vue}
    apps/mcp-server/
    apps/{ai-evals,dotcdn,dotcms-binary-field-builder,dotcms-block-editor,dotcms-ui,
          dotcms-ui-e2e}
```

`create-app` is filed under `libs/sdk/` despite being a CLI; `mcp-server` is under `apps/`.

---

## Skills

`dotcms-create-sites` — 26 markdown files, in this repo at `skills/dotcms-create-sites/`.

```
SKILL.md                 113 lines   two-phase orchestration
reference/plan/          225 lines   interview, plan-template, design-template
reference/build/         940 lines   task-indexed build reference
  core/    8 files                   what-must-exist, site, content-types, content,
                                     pages, templates, containers, placement
  vtl/     7 files                   wiring, choose-mechanism, themes, containers,
                                     listings-and-details, verify-and-debug, velocity
  nextjs/  6 files                   connect, component-contract, next-config,
                                     routing, listings-and-details, verify
```

No `dotcms-best-practices` or migration skill exists yet.
