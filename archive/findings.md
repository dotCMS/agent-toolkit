# Findings

Verified external facts. **Every row carries a source and a date checked** — facts about
npm versions, competitor behavior, and API endpoints rot. Re-verify before relying on
anything older than a few weeks.

Confidence: **verified** = exercised in-session against the real thing · **documented** =
from official docs, not exercised · **reported** = from Freddy's brainstorm/testing,
not independently re-checked.

## Our own stack

| ID | Finding | Confidence | Source | Checked |
|---|---|---|---|---|
| F-001 | `@dotcms/mcp-server` is published on npm at version **0.0.13** | verified | `npm view` | 2026-08-31 |
| F-002 | **`create-dotcms` is unclaimed on npm** (404). The name is available. | verified | `npm view` | 2026-08-31 |
| F-003 | `skills` npm package (for `npx skills add`) is real, at **v1.5.23** | verified | `npm view` | 2026-08-31 |
| F-004 | `skills/dotcms-create-sites/` is **26 markdown files** | verified | `find` | 2026-08-31 |
| F-005 | dotCMS token mint path: Basic auth → `GET /api/v1/users/current` for `userId` → `POST /api/v1/apitoken` with `{userId, expirationSeconds, claims:{label}}` → read `entity.jwt`. This is what the admin UI uses; keys are listed/revocable under System > Users. | reported | idea-plan.md §Secret handling, tested against a live instance | 2026-08-31 |
| F-006 | `/authentication/api-token` is `@Deprecated` and `@Hidden` — do not use | reported | idea-plan.md | 2026-08-31 |
| F-007 | Minted key is a **JWT with a TTL (1 year default)** — users will hit silent expiry | reported | idea-plan.md | 2026-08-31 |
| F-008 | The seven MCP tools: `search`, `execute`, `upload_assets`, `download_assets`, `page_create`, `page_verify`, `page_place_content` | reported | idea-plan.md §Verification | 2026-08-31 |

## MCP client landscape

| ID | Finding | Confidence | Source | Checked |
|---|---|---|---|---|
| F-009 | Seven target clients reduce to **four config shapes**: A `{mcpServers:{…}}` (Claude Code, Cursor, Devin) · B TOML `[mcp_servers.NAME]` (Codex) · C `{mcp:{NAME:{type:"local",command:[…],environment:{}}}}` — command is ONE array (opencode) · D `{servers:{NAME:{type:"stdio",…,envFile}}}` (VS Code). `pi` has no MCP support, skill only. | reported | idea-plan.md §Client registry | 2026-08-31 |
| F-010 | **Claude Code passes an unset `${VAR}` through literally** — it expands only from the launching shell's environment and has no `envFile`. So a config with `${AUTH_TOKEN}` sends the literal string and 401s confusingly. Forces a literal token everywhere except VS Code. | reported | idea-plan.md §Secret handling | 2026-08-31 |
| F-011 | **VS Code is the only client with a real `envFile` field** — it can point at `~/.dotcms/env` and hold no secret in its config | reported | idea-plan.md | 2026-08-31 |
| F-012 | Windsurf was renamed **Devin Desktop** (2 June 2026). Its default agent reads the Devin CLI config at `~/.config/devin/mcp_config.json`, so one path covers CLI + IDE. `.devin/mcp_config.local.json` is documented as a gitignored project-secret file. | documented | idea-plan.md | 2026-08-31 |
| F-013 | Client config paths — claude-code `~/.claude.json` + `./.mcp.json` · codex `~/.codex/config.toml` · cursor `~/.cursor/mcp.json` + `./.cursor/mcp.json` · opencode `~/.config/opencode/opencode.json` + `./opencode.json` · vscode `~/Library/Application Support/Code/User/mcp.json` + `./.vscode/mcp.json` · devin as F-012. First four **live-verified**, vscode is docs+path, devin is docs only. | mixed | idea-plan.md §Client registry | 2026-08-31 |
| F-014 | `command -v claude` **fails under mise/nvm in a non-login shell** — version-manager shims hide CLIs. Detection must fall back to config dir. | reported | idea-plan.md | 2026-08-31 |
| F-015 | `writeFileSync`'s `mode` option is **ignored when the file already exists** — silently leaves tokens world-readable at 644. Must `chmod` as a separate call after writing. | reported | idea-plan.md (cost a real bug in the draft) | 2026-08-31 |
| F-016 | The two `agent-plugins.org` schema URLs **404 today** | reported | idea-plan.md | 2026-08-31 |

## Sanity (the bar)

Full teardown: `research/sanity-onboarding-teardown.md`

| ID | Finding | Confidence | Source | Checked |
|---|---|---|---|---|
| F-017 | Sanity's entry point is `npm create sanity@latest` → `create-sanity@6.0.40`. **~11 prompts, every one with a default**, most answerable with Enter. | verified | 19-page deck + full transcript | 2026-08-31 |
| F-018 | One run provisions **cloud (org + project + dataset) + local project + MCP config + agent skills**, across 7 editors (Antigravity, Claude Code, Codex CLI, Cursor, GitHub Copilot CLI, OpenCode, VS Code), multi-select, all pre-checked. | verified | transcript | 2026-08-31 |
| F-019 | **The hand-off primitive:** the success screen says `Restart Claude Code, Codex CLI, OpenCode, and VS Code and type "Get started with Sanity" in the chat.` Typing it produced a session that already knew the projectId, dataset, schema types and dev-server state. | verified | transcript + deck p17 | 2026-08-31 |
| F-020 | Sanity ships **two** skills in the box: `sanity-best-practices`, `sanity-migration`. Real files land in `~/.agents/skills/` and are **symlinked** into `~/.claude/skills/` — one copy, N clients. | verified | `ls` on this machine | 2026-08-31 |
| F-021 | In-agent decisions are **interactive option cards, not prose**: a Layout picker with an ASCII monorepo tree preview and "press n to add notes", and a Scope picker (Full setup / Data fetching only / Minimal wiring / Type something / Chat about this). | verified | deck p18–19 | 2026-08-31 |
| F-022 | **Their critical bug:** the success screen says to run `pnpm dev`, and `pnpm dev` fails — `ERR_PNPM_IGNORED_BUILDS: esbuild@0.28.2`, exit 1, plus a 10-line pnpm stack trace. Happened on **both** projects. Recovery (`pnpm approve-builds`) is a pnpm concept the CLI never mentions, and has a silent wrong path that permanently denies the build. | verified | transcript, both runs | 2026-08-31 |
| F-023 | Their returning-user run correctly reported `4 editors already configured for Sanity MCP` and skipped — but **also dropped the hand-off sentence entirely**, so a user who missed it the first time never sees it again. | verified | transcript run 2 | 2026-08-31 |
| F-024 | Templates offered: Clean / Blog (schema) / E-commerce (Shopify) / Movie (schema + sample data) / Page Builder (presets). Movie imported **205 documents** with assets, per-phase progress, and printed the undo command immediately after. | verified | transcript | 2026-08-31 |

## `@dotcms/create-app` — the existing CLI (added 2026-08-31)

Source: `/Users/fmontes/Developer/dotcms/core/core-web/libs/sdk/create-app` (nx lib
`sdk-create-app`, 11 TS files, ~3,240 lines). All rows read directly from source.

| ID | Finding | Confidence | Checked |
|---|---|---|---|
| F-025 | **`@dotcms/create-app` is published and live at `26.8.31-1`** (published 2026-08-31 16:12 UTC — same day). Bin name is `create-dotcms-app`. Invoked `npx @dotcms/create-app my-app`. Built by nx/esbuild to a single ESM Node bundle with a shebang. | verified | 2026-08-31 |
| F-026 | **It already provisions dotCMS.** `--local` checks Docker, checks ports 8082/8443/9200/9600, downloads `docker-compose.yml` from `dotCMS/core` main (`single-node-demo-site`), runs `docker compose up -d`, polls health 60×5s, then uses default creds `admin@dotcms.com`/`admin`. **This answers Q-001.** | verified | 2026-08-31 |
| F-027 | Three modes: **cloud** (`--url`, point at existing instance), **local** (`--local`, Docker), **starter-only** (`--starter <zip-url>`, implies local, rewrites `CUSTOM_STARTER_URL`, and *skips* frontend scaffold + token + UVE setup). | verified | 2026-08-31 |
| F-028 | ⚠️ **It mints tokens via `/api/v1/authentication/api-token`** with `expirationDays: '30'` — the endpoint `idea-plan.md` says is `@Deprecated`/`@Hidden` and must not be used (F-006). **Direct conflict with D-014.** Also a different TTL from the plan's 1-year. | verified | 2026-08-31 |
| F-029 | Per-run work it already does: health check at `/api/v1/appconfiguration` (not `/probes/alive` — those have IP ACLs that block the Docker host, per GitHub #34509) → auth with 3 retries → `GET /api/v1/site/defaultSite` → configure UVE via `POST /api/v1/apps/dotema-config-v2/{siteId}` → scaffold → `npm install`. | verified | 2026-08-31 |
| F-030 | Frameworks: `nextjs`, `astro`, `angular`, `angular-ssr`, with aliases (`next`/`next.js`, `ng`, `angular-server`). Framework choice sets the UVE URL to `http://localhost:{port}`. | verified | 2026-08-31 |
| F-031 | 🔑 **`@dotcms/*` packages ship in version lockstep with dotCMS itself** — every SDK package carries the exact version of the dotCMS release it was built for (dotCMS `26.7.14-1` → `@dotcms/client@26.7.14-1`). The instance advertises the oldest SDK it supports and the SDK self-checks, warning in console when too old. LTS releases get no matching SDK version today. | verified | 2026-08-31 |
| F-032 | ⚠️ **The CLI does not write `.env`.** It prints the block (including the token) to stdout and says "Copy the block above and paste into your .env file", then `touch .env` as a manual step. Token lands in terminal scrollback. | verified | 2026-08-31 |
| F-033 | 🔑 **The CLI has zero awareness of MCP, skills, or agents.** `grep -niE 'mcp\|skill\|agent\|claude\|cursor\|codex'` over the whole source returns nothing. | verified | 2026-08-31 |
| F-034 | Frontend templates are **not shipped with the CLI** — it does a blobless sparse `git clone` of `dotCMS/core` and checks out `examples/{framework}` from **`main`**, then deletes the rest. So template content is unversioned relative to the CLI. Requires `git`. | verified | 2026-08-31 |
| F-035 | Existing UX assets: `cfonts` DOTCMS banner, `ora` spinners with succeed/fail per step, `inquirer` prompts with defaults, a `Result<T,E>` Ok/Err type, typed error classes, rich actionable error text (401 / ECONNREFUSED / port-busy / Docker-missing all have tailored remedies), `DEBUG=1` for stack traces, and validation that runs on all flags *before* any prompt. | verified | 2026-08-31 |
| F-036 | Non-empty target directory prompts for confirmation and then **`fs.emptyDir`s it** — destructive, gated behind one `confirm` defaulting to false. | verified | 2026-08-31 |

## The skill's internal seam (added 2026-08-31)

| ID | Finding | Confidence | Checked |
|---|---|---|---|
| F-037 | `dotcms-create-sites` is **already split along the seam we'd need**: `reference/build/` is 18 files / ~940 lines of task-indexed reference whose own README says *"Load only the file for the step you're on — don't read the folder up front"* — a lookup manual, not a workflow. The two-phase orchestration is just `SKILL.md` (113 lines) + `reference/plan/` (3 files, 225 lines). Extracting a standalone best-practices skill means re-fronting `build/` with an intent-indexed SKILL.md, not refactoring content. | verified | 2026-08-31 |
| F-038 | `reference/build/` forks by delivery mode: `core/` (8 files — what-must-exist, site, content-types, content, pages, templates, containers, placement) applies to both modes, then `vtl/` (7 files) or `nextjs/` (6 files). The core/ files are the granular "how do I do one thing" knowledge. | verified | 2026-08-31 |
| F-039 | dotCMS "templates" are **not code in the repo** the way Sanity's `schemaTypes/*.ts` are — dotCMS content types and content live in the *instance*. So our template axis is the **starter loaded into dotCMS** (`single-node-demo-site` compose, `CUSTOM_STARTER_URL`), which the CLI already supports (F-027). | verified | 2026-08-31 |

## 🚨 Security: admin token shipped to the browser (added 2026-08-31)

| ID | Finding | Confidence | Checked |
|---|---|---|---|
| F-040 | **The CLI writes a write-capable admin token into a public client bundle.** `getEnvVariablesForNextJS` in `create-app/src/utils/index.ts` emits `NEXT_PUBLIC_DOTCMS_AUTH_TOKEN=${token}`. `NEXT_PUBLIC_*` is inlined into the client bundle by Next.js at build time. The token was minted against the credentials the user typed — `admin@dotcms.com` locally, **their real admin account in cloud mode** — and dotCMS API tokens inherit the user's permissions. So anyone who loads the deployed site can read a full-access token out of the JS. | verified | 2026-08-31 |
| F-041 | The skill already documents the rule being broken. `reference/build/nextjs/00-connect.md`: *"The token ships to the browser… That is deliberate — the UVE bridge runs client-side and needs it — so the token you issue **must be read-only**. Never put a write-capable token in this variable."* | verified | 2026-08-31 |
| F-042 | Severity splits by mode: **local Docker** is low stakes (localhost, credentials are already `admin`/`admin`). **Cloud mode** is real — the user typed real admin credentials, and the resulting token lands in a bundle they may deploy. | verified | 2026-08-31 |
| F-043 | This settles the "one token or two?" question: the frontend needs **read-only** (it ships to browsers), the MCP server needs **write** (it creates content types, pages, content). Two tokens, for security reasons rather than just independent revocability. | verified | 2026-08-31 |
| F-044 | `examples/nextjs/.env.local.example` points at `localhost:8080` while the CLI's local Docker serves **8082**, and it ships `NODE_TLS_REJECT_UNAUTHORIZED=0`. | verified | 2026-08-31 |

## The CLI naming landscape (added 2026-08-31)

| ID | Finding | Confidence | Checked |
|---|---|---|---|
| F-045 | **`@dotcms/dotcli` already exists and calls itself "Official command-line tool to manage dotCMS content."** Created 2024-02-07 (2.5 years old), on the same lockstep train at `26.8.31-1`. It ships **native Java binaries** (`dotcms-cli-26.08.31-01-{linux-x86_64,osx-aarch_64,osx-x86_64}`) and has no `bin` field — a `postinstall` script symlinks the right binary into the global bin dir under the name in its `alias` field. | verified | 2026-08-31 |
| F-046 | **The command it claims is `dotcli`** (`"alias": "dotcli"`, internal `packageName: "dotcms-cli"`). So `dotcli` is taken; a bare `dotcms` command is not. | verified | 2026-08-31 |
| F-047 | **The org therefore already has two CLIs**: `dotcli` (native, content management — push/pull) and `create-dotcms-app` (Node, scaffolding). Adding a third name for agent setup would make three. | verified | 2026-08-31 |
| F-048 | `@dotcms/create-app` was first published **2026-01-07** — about 8 months old, with a long `1.2.1-next.*` prerelease trail, and its README still says *"Beta. Behavior and flags may change."* Renaming is cheap now in a way it won't be later. | verified | 2026-08-31 |
| F-049 | Neither `@dotcms/cli` nor `dotcms-cli` is claimed on npm. `create-dotcms` is also still unclaimed. | verified | 2026-08-31 |
| F-050 | No other `@dotcms/*` package ships a bin — `client`, `uve`, `experiments`, `angular` are all libraries. `@dotcms/dotcli` and `@dotcms/create-app` are the only two executables. | verified | 2026-08-31 |

## dotcli is being rewritten in TypeScript (added 2026-08-31)

Source: `dotcli.md` — "dotCLI MVP — Greenfield Spec", 2026-08-26, status *"Decided — ready to
build"*, supersedes the Asana "dotCLI Enhancements" epic.

| ID | Finding | Confidence | Checked |
|---|---|---|---|
| F-051 | **`@dotcms/dotcli` is being rebuilt as a TypeScript CLI**, bin still `dotcli`, with *"no code from the current Java/Quarkus one, which is too hard to maintain and release."* So F-045's "native Java binary" describes the version being replaced. | verified | 2026-08-31 |
| F-052 | **Same stack, same monorepo, same release train as `create-app`.** The spec's own appendix: *"Stack precedent to follow: `core-web/libs/sdk/create-app` — Nx library, ESM, `@nx/esbuild`, commander, inquirer, chalk, ora, axios, nx release with git-tag versioning."* Consolidation is no longer a cross-language problem. | verified | 2026-08-31 |
| F-053 | dotcli's scope is **deliberately narrow, and that narrowness is the design**: *"Because the only object is a file, identity is the path. No UUID mapping, no cross-environment key matching, no schema migration, no dependency graph. That is what makes this buildable in one pass."* Explicitly **out**: content types, languages, sites-as-objects, pages, contentlets. | verified | 2026-08-31 |
| F-054 | It already owns machinery the onboarding flow needs: **`login`** (interactive token flow, stored in the **OS keychain keyed by URL**, never in the repo, `DOTCMS_TOKEN` for CI), **`doctor`** (checks auth, **token expiry**, write and publish permission, and that a publish action resolves), and an `--env <url>` + `.dotcli/config.yml` model for "which instance". | verified | 2026-08-31 |
| F-055 | Four invariants govern every write: push never deletes · push is always draft · push is rejected if the remote moved since your last pull · **publish always fires the mapped workflow action and honors permissions, never the raw publish endpoint.** | verified | 2026-08-31 |
| F-056 | 🚨 **The spec twice records that the MCP server violates invariant 4.** §11: *"There is no `--force-publish`. The CLI cannot bypass a review step. **The MCP server currently can, by calling the endpoint directly — separate ticket, same rule should apply.**"* §16: *"Invariant 4 is not enforced server-side… The CLI must pre-check and refuse. **This is also why the MCP server bypasses today.**"* | verified | 2026-08-31 |
| F-057 | §14 sets an autonomy boundary: **Freddy decides** any new write path beyond push/rm/publish/lock/unlock, any exception to the invariants, and anything that bypasses a workflow action or permission check. Adding onboarding write paths to dotcli is explicitly his call. | verified | 2026-08-31 |
| F-058 | dotcli MVP distribution is **npm only**; standalone binaries (bun compile) only if a customer's CI can't run Node. | verified | 2026-08-31 |

## MCP secret handling — research (added 2026-08-31)

| ID | Finding | Confidence | Checked |
|---|---|---|---|
| F-059 | **stdio MCP has no secret mechanism beyond the client config `env` block.** Servers launched over stdio inherit only a limited, platform-dependent subset of the environment, so credentials must be handed in explicitly by the host. This is a protocol reality, not a per-client gap. | documented | 2026-08-31 |
| F-060 | **MCP's authorization spec is OAuth 2.1 with PKCE — and applies only to HTTP transports.** Introduced in the 2025-06-18 spec. Servers on that transport are called "remote", *"whether the MCP server lives on localhost, a private URL or a public URL"* — so localhost HTTP qualifies. Authorization is OPTIONAL for implementations. | documented | 2026-08-31 |
| F-061 | **dotCMS's MCP server is stdio-only today.** `xmcp.config.ts` sets `stdio: true`; the bin and `main` are `./stdio.js`; `src/lib/runtime.ts` reads `process.env.DOTCMS_URL` and `process.env.AUTH_TOKEN`. | verified | 2026-08-31 |
| F-062 | **xmcp (v1.1.2) supports both transports.** HTTP is configured as `http: { port, host, endpoint, bodySizeLimit }`. Auth for HTTP is middleware, not a config key — built-in `apiKeyAuthMiddleware` and `jwtAuthMiddleware`, plus third-party OAuth plugins (Auth0, Clerk, Better Auth). Switching transport is a config change; auth is an implementation. | documented | 2026-08-31 |
| F-063 | **Where the server looks for credentials is our choice, not a protocol constraint.** It reads `process.env` today; it could resolve them from a dotCMS config file or the OS keychain instead, which would leave client configs holding no secret at all — while staying on stdio. | verified (from source) | 2026-08-31 |

## Skill installation mechanics (added 2026-08-31)

| ID | Finding | Confidence | Checked |
|---|---|---|---|
| F-064 | **`npx skills add` symlinks — it does not copy.** The `skills@1.5.23` bundle carries `symlink`, `symlinked`, `symlinkType`, `symlinkAgents` and failure handling (`symlinkFailed`, `symlinkFailures`, implying a copy fallback where symlinks are unavailable). Real files land in `~/.agents/skills`; per-agent directories (`.claude/skills`, `.cursor`, `.codex`, `opencode`) get links. Confirmed independently on this machine: `~/.claude/skills/sanity-best-practices -> ../../.agents/skills/sanity-best-practices`. | verified | 2026-08-31 |
| F-065 | **Skill frontmatter has no dependency mechanism** — `name`, `description`, and optional metadata only. So one skill cannot formally depend on another. In practice it does not need to: both dotCMS skills install together from `npx skills add dotcms/skills`, so `create-sites` can reference `dotcms-best-practices` by name in its instructions and the reference content lives once. | verified | 2026-08-31 |

## Antigravity and GitHub Copilot CLI — registry research (added 2026-09-01)

| ID | Finding | Confidence | Checked |
|---|---|---|---|
| F-066 | **Antigravity is Shape A.** `{"mcpServers": {NAME: {command, args, env, cwd}}}` — note it also supports a `cwd` field the other Shape A clients don't. Global: `~/.gemini/config/mcp_config.json`; project: `.agents/mcp_config.json`. Antigravity 2.x **consolidated** the IDE, the `agy` CLI and the SDK onto that one global config. Legacy path, pre-2.x: `~/.gemini/antigravity/mcp_config.json` (macOS/Linux) and `C:\Users\<USER>\.gemini\antigravity\mcp_config.json`. | documented | 2026-09-01 |
| F-067 | **GitHub Copilot CLI is Shape A.** Global: `~/.copilot/mcp-config.json`, overridable via the `COPILOT_HOME` env var; project: `.copilot/mcp-config.json` in the repo root. **Live-verified** — the file exists on this machine and its top-level key is `mcpServers`. | verified | 2026-09-01 |
| F-068 | **Both new clients fold into Shape A. No fifth shape is needed** — the registry grows to eight clients across the same four config shapes. | verified | 2026-09-01 |
| F-069 | `.agents/` is emerging as a cross-vendor convention: Antigravity reads project MCP config from `.agents/mcp_config.json`, and `npx skills add` puts real skill files in `~/.agents/skills`. | documented | 2026-09-01 |
