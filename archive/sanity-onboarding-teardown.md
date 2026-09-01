# Sanity.io onboarding teardown — the bar to beat

**Date captured:** 2026-08-31
**Source:** `Sanity Review - 08_31_2026.pdf` (19-page screenshot deck, ~/Downloads) + full terminal transcript
**Ran by:** Freddy Montes (`freddy+sanity@dotcms.com`), macOS, node v24.18.0, pnpm 11.21.0 via mise
**Versions:** `create-sanity@6.0.40`, `vite@8.2.2`, Studio dev on `localhost:3333`

## Why this document exists

This is the **reference experience** for dotCMS agent/CLI onboarding. The goal is not to
copy it — it is to ship something **10x better**. Everything below is written so the
good parts can be lifted deliberately and the bad parts are never re-invented.

The single most important thing Sanity got right: **one command creates the cloud
resources, the local project, AND wires up the user's AI coding agents — then hands
the user a sentence to type into that agent.** The CLI stops being the destination and
becomes the on-ramp to an agent session.

---

## 1. The shape of the flow

```
npm create sanity@latest
  │
  ├─ 1. telemetry notice (boxed, opt-out command inline)
  ├─ 2. auth        → browser login, 4-digit email code, "Return to the terminal"
  ├─ 3. project     → name, org (creates org on the fly)
  ├─ 4. dataset     → "use the default? (Y/n)" — one keypress, explains public/private first
  ├─ 5. AGENTS      → multi-select editors → writes MCP config + installs agent skills
  ├─ 6. output path → prefilled default
  ├─ 7. template    → Clean / Blog / E-commerce (Shopify) / Movie / Page Builder
  ├─ 8. TypeScript? → (Y/n)
  ├─ 9. sample data → optional hosted import (205 docs on the Movie template)
  ├─ 10. package manager → npm / yarn / pnpm / manual
  └─ 11. install + success screen → next commands + "type this in your agent chat"
```

Total: ~11 prompts, every one with a sane default, most answerable with Enter.

## 2. Verbatim: the moment that matters

```
✔ Configure Sanity MCP and agent skills for these editors? Claude Code, Codex CLI, OpenCode, VS Code
✔ MCP configured for Claude Code, Codex CLI, OpenCode, VS Code
✔ Sanity agent skills installed: [sanity-best-practices, sanity-migration]

  Universal (~/.agents/skills)
    Codex, OpenCode, GitHub Copilot

  Additional agents
    Claude Code (~/.claude/skills)
```

The picker offered: **Antigravity, Claude Code, Codex CLI, Cursor, GitHub Copilot CLI,
OpenCode, VS Code** — multi-select, all pre-checked.

And the payoff, in the success screen:

```
Restart Claude Code, Codex CLI, OpenCode, and VS Code and type "Get started with Sanity" in the chat.

Learn more: https://mcp.sanity.io
```

Then in the agent (page 17 of the deck), typing `get started with sanity` produced a
session that already knew the project: it detected the Studio was bootstrapped from the
movie template, ran the dev server, reported `localhost:3333`, listed the schema
(`movie`, `person`, `screening`) and objects (`blockContent`, `plotSummary`,
`plotSummaries`, `castMember`, `crewMember`), named the config values
(`projectId gjb0nqc`, `dataset production`), and flagged the uncommitted
`esbuild: false` in `pnpm-workspace.yaml` as something to note.

Then `wire up a frontend with nextjs` loaded the `sanity-best-practices` skill and
presented **interactive option cards** rather than prose:

- **Layout** — "Move to `studio/` + `web/` (Recommended)" vs "Keep Studio at root, add `web/`",
  with an ASCII tree preview of the resulting monorepo, and `press n to add notes`.
- **Scope** — Full setup (Live Content API `defineLive`, TypeGen, GROQ queries + pages,
  Presentation tool with click-to-edit Visual Editing, draft mode route, `next/image`
  with Sanity image URLs) / Data fetching only / Minimal wiring / Type something /
  Chat about this.

## 3. What Sanity got right (steal these)

| # | Move | Why it works |
|---|---|---|
| 1 | **`npm create` as the only entry point** | No install step, no global binary, no docs page first. One line, copy-pasteable. |
| 2 | **Cloud + local + agent in one run** | Org, project, dataset, local repo, MCP config, and skills all provisioned before the user ever opens an editor. No "now go to the dashboard and copy your API key." |
| 3 | **Auth via browser with a return-to-terminal page** | The 4-digit email code + "Login successful / Return to the terminal" page closes the loop visually. The CLI spinner says exactly what it's waiting for and how to cancel. |
| 4 | **Explains before it asks** | The dataset prompt spends two sentences on public vs private *before* the Y/n. Teaches the model while collecting the answer. |
| 5 | **Agent wiring is a first-class prompt, not a footnote** | Multi-select, all editors pre-checked, and it reports exactly which paths were written (`~/.agents/skills`, `~/.claude/skills`). |
| 6 | **Ships skills, not just an MCP server** | `sanity-best-practices` + `sanity-migration` mean the agent has opinions and a house style, not just tool access. |
| 7 | **Hands over a literal sentence to type** | `type "Get started with Sanity" in the chat` — zero ambiguity about the next action. This is the hand-off primitive. |
| 8 | **Idempotent on the second run** | Second project: `4 editors already configured for Sanity MCP`, `MCP configuration skipped`. It remembered. |
| 9 | **Templates with real data** | Movie template imported 205 documents with assets, with progress percentages per phase, and told the user how to undo it (`npx sanity dataset delete production`). |
| 10 | **Success screen is a menu, not a paragraph** | cd line, dev command, agent hand-off, docs/manage/help commands, community link. |
| 11 | **Undo instructions shipped with the destructive-ish action** | Sample data import immediately followed by how to delete it. |
| 12 | **In-agent option cards over prose** | The Layout/Scope pickers with an ASCII tree preview and "press n to add notes" — decisions made visually, inside the agent. |

## 4. Where it broke or fell short (do not repeat)

| # | Problem | Evidence | Severity |
|---|---|---|---|
| 1 | **First `pnpm dev` fails outright** | `[ERR_PNPM_IGNORED_BUILDS] Ignored build scripts: esbuild@0.28.2` → `exit code 1` + a 10-line pnpm internal stack trace. Happened on **both** projects. The CLI just told the user to run `pnpm dev`, and `pnpm dev` didn't work. | **Critical** — breaks the very first thing the success screen tells you to do |
| 2 | **Recovery requires unrelated knowledge** | `pnpm approve-builds` is a pnpm concept, not a Sanity one. Nothing in the CLI mentioned it. | High |
| 3 | **The recovery has a silent wrong path** | On the second project, `approve-builds` was submitted with nothing selected → `All packages were added to allowBuilds with value false.` Dev then "worked" but esbuild was permanently denied. A wrong-but-quiet outcome. | High |
| 4 | **`[ELIFECYCLE] Command failed.`** | Printed on Ctrl+C after a *successful* dev server. Reads as an error when nothing failed. Exit 143 = SIGTERM. | Medium — erodes trust in every other message |
| 5 | **Deprecation warning before hello** | `npm warn deprecated uuid@10.0.0` is the second line the user ever sees. | Medium — first impression is someone else's tech debt |
| 6 | **No monorepo/frontend story in the CLI** | The CLI creates a Studio at repo root. The *agent* then has to propose restructuring to `studio/` + `web/`. The right layout should be offered at create time. | Medium |
| 7 | **"Restart your editor"** | Manual step, easy to skip, silently breaks the payoff if skipped. | Medium |
| 8 | **Second-run project placement is on the user** | `mkdir sanity && mv my-test-sanity/ sanity/` was done by hand. The CLI has no notion of "I'm collecting several projects." | Low |
| 9 | **Org creation is a name prompt with no confirmation** | `✔ Creating organization` for "freddy sanity" — an org got created as a side effect of typing a name. | Low |
| 10 | **Success screen differs between runs** | Run 2 dropped the MCP/agent hand-off lines entirely (because MCP was skipped) — so the "type this in your chat" instruction vanished for a returning user who might still not know it. | Low |

## 5. Full transcript (run 1 — Page Builder template)

```
npm create sanity@latest
Need to install the following packages:
create-sanity@6.0.40
Ok to proceed? (y)
npm warn deprecated uuid@10.0.0: uuid@10 and below is no longer supported.  For ESM codebases, update to uuid@latest.  For CommonJS codebases, use uuid@11 (but be aware this version will likely be deprecated in 2028).

> npx
> "create-sanity"

   ╭─────────────────────────────────────────────────────────────────────────────╮
   │   The Sanity CLI now collects telemetry data on general usage and errors.   │
   │   This helps us improve Sanity and prioritize features.                     │
   │   To opt in/out, run npx sanity telemetry enable/disable.                   │
   │   Learn more here: https://www.sanity.io/telemetry                          │
   ╰─────────────────────────────────────────────────────────────────────────────╯

 ›   Warning: No valid authentication credentials found.
 ›   Authenticate with one of these commands:
 ›     echo "$TOKEN" | sanity login --with-token
 ›     sanity login --provider <providerId> --no-open
 ›       Provider IDs: google, github, sanity, vercel
 ›     sanity login --sso <organizationSlug> --no-open
 ›   `--no-open` prints a login URL instead of opening a browser.
✔ Please log in or create a new account E-mail / password

Opening browser at https://api.sanity.io/v1/auth/login/sanity?type=token&label=Mac5+%2F+MacOS&origin=http%3A%2F%2Flocalhost%3A4321%2Fcallback

✔ You are logged in as freddy+sanity@dotcms.com using Email
✔ Fetching existing projects

✔ Project name: My Test Sanity
✔ Organization name: freddy sanity
✔ Creating organization
Your content will be stored in a dataset that can be public or private, depending on
whether you want to query your content with or without authentication.
The default dataset configuration has a public dataset named "production".
✔ Use the default dataset configuration? Yes
✔ Creating dataset
Dataset created successfully
✔ Configure Sanity MCP and agent skills for these editors? Claude Code, Codex CLI, OpenCode, VS Code
✔ MCP configured for Claude Code, Codex CLI, OpenCode, VS Code
✔ Sanity agent skills installed: [sanity-best-practices, sanity-migration]

  Universal (~/.agents/skills)
    Codex, OpenCode, GitHub Copilot

  Additional agents
    Claude Code (~/.claude/skills)

✔ Project output path: /Users/fmontes/Developer/my-test-sanity
✔ Select project template Page Builder (presets)
✔ Do you want to use TypeScript? Yes
✔ Bootstrapping files from template
✔ Resolving latest module versions
✔ Creating default project files
✔ Package manager to use for installing dependencies? pnpm
✔ Running pnpm install

✅ Success! Your Studio has been created.

(cd /Users/fmontes/Developer/my-test-sanity to navigate to your new project directory)

Get started by running pnpm dev to launch your Studio's development server

Restart Claude Code, Codex CLI, OpenCode, and VS Code and type "Get started with Sanity" in the chat.

Learn more: https://mcp.sanity.io

Have feedback? Tell us in the community: https://www.sanity.io/community/join

Other helpful commands:
npx sanity docs browse     to open the documentation in a browser
npx sanity manage          to open the project settings in a browser
npx sanity help            to explore the CLI manual

Join the Sanity community: https://www.sanity.io/community/join
We look forward to seeing you there!
```

### The failure

```
cd my-test-sanity/
pnpm dev
✓ Lockfile passes supply-chain policies (verified 42s ago)
Lockfile is up to date, resolution step is skipped
Already up to date
[ERR_PNPM_IGNORED_BUILDS] Ignored build scripts: esbuild@0.28.2

Run "pnpm approve-builds" to pick which dependencies should be allowed to run scripts.
[ERROR] Command failed with exit code 1: /Users/fmontes/.local/share/mise/installs/pnpm/11.21.0/pnpm install

pnpm: Command failed with exit code 1: .../pnpm install
    at getFinalError (.../pnpm.mjs:89024:14)
    at makeError (.../pnpm.mjs:91331:21)
    at getSyncResult (.../pnpm.mjs:93175:10)
    at spawnSubprocessSync (.../pnpm.mjs:93135:14)
    at execaCoreSync (.../pnpm.mjs:93065:23)
    at callBoundExeca (.../pnpm.mjs:95593:23)
    at boundExeca (.../pnpm.mjs:95570:49)
    at sync2 (.../pnpm.mjs:95729:10)
    at runPnpmCli (.../pnpm.mjs:269870:5)
    at runDepsStatusCheck (.../pnpm.mjs:271638:7)

pnpm approve-builds
✔ Choose which packages to build (Press <space> to select, <a> to toggle all, <i> to invert selection) esbuild
✔ The next packages will now be built: esbuild.
Do you approve? Yes
node_modules/.pnpm/esbuild@0.28.2/node_modules/esbuild: Running postinstall script, done in 368ms

pnpm dev
✓ Lockfile passes supply-chain policies (verified 2m ago)
Done in 217ms using pnpm v11.21.0
$ sanity dev
ℹ Running with auto-updates enabled
✔ Checking configuration files...
✔ Starting dev server
Sanity Studio using vite@8.2.2 ready in 110ms and running at http://localhost:3333/
[ELIFECYCLE] Command failed.
```

## 6. Full transcript (run 2 — Movie template, returning user)

```
cd ../ && mkdir sanity && mv my-test-sanity/ sanity/ && cd sanity/
npm create sanity@latest

> npx
> "create-sanity"

✔ You are logged in as freddy+sanity@dotcms.com using Email
✔ Fetching existing projects

✔ Create a new project or select an existing one Create new project
✔ Project name: my test sanity 2
✔ Select organization: freddy sanity [o5nkauw8q]
Your content will be stored in a dataset that can be public or private, depending on
whether you want to query your content with or without authentication.
The default dataset configuration has a public dataset named "production".
✔ Use the default dataset configuration? Yes
✔ Creating dataset
Dataset created successfully
✔ Configure Sanity MCP and agent skills for these editors?
MCP configuration skipped
✔ 4 editors already configured for Sanity MCP
✔ Project output path: /Users/fmontes/Developer/sanity/my-test-sanity-2
✔ Select project template Movie project (schema + sample data)
✔ Do you want to use TypeScript? Yes
✔ Add a sampling of sci-fi movies to your dataset on the hosted backend? Yes
✔ Bootstrapping files from template
✔ Resolving latest module versions
✔ Creating default project files
✔ Package manager to use for installing dependencies? pnpm
✔ Running pnpm install

✔ [100%] Reading/validating data file (25ms)
✔ [100%] Importing documents (1.41s)
✔ [100%] Importing assets (files/images) (45.63s)
✔ [100%] Setting asset references to documents (455ms)
✔ [100%] Strengthening references (733ms)
Done! Imported 205 documents to dataset "production"

If you want to delete the imported data, use
  npx sanity dataset delete production
and create a new clean dataset with
  npx sanity dataset create <name>

✅ Success! Your Studio has been created.
```

Note: run 2's success screen **omitted** the agent hand-off lines.

Same `ERR_PNPM_IGNORED_BUILDS` failure. This time `approve-builds` was submitted with
nothing selected:

```
pnpm approve-builds
✔ Choose which packages to build (Press <space> to select, <a> to toggle all, <i> to invert selection)
All packages were added to allowBuilds with value false.
```

Dev then started fine (`ready in 144ms`), exiting with `[ELIFECYCLE] Command failed with exit code 143.`

## 7. Notes on the source deck

The PDF is a Google Slides export (19 pages, 720×405, ~2.5 MB) where every page is a
screenshot with no text layer — only pages 2 and 15 carry extractable text. Reading it
requires rasterizing pages. Pages 1 and 5 are cropped: the right edge cuts off mid-line
(`freddy+sanity@d...`).

## 8. Open questions for the dotCMS equivalent

- What is our one-line entry point, and does it exist yet? (`npx create-dotcms`? `dotcms init`?)
- Can we provision a cloud dotCMS environment from the CLI the way Sanity provisions a
  project + dataset, or does onboarding have to assume an existing instance?
- Which editors do we wire? Sanity covered 7. What is our list and where do skills land?
- What is our "type this in the chat" sentence?
- Which skills ship in the box? `dotcms-create-sites` already exists in this repo — is
  that the flagship, and what pairs with it (migration? best-practices?)
- How do we avoid the `pnpm approve-builds` class of failure — i.e. verify the dev
  server actually starts before printing a success screen?
