# Decisions

Append-only. **Never edit a row in place** — add a new decision and mark the old one
`superseded by D-0NN`. The reasoning trail is the point.

Status: **proposed** = on the table, awaiting Freddy · **accepted** = settled ·
**rejected** = considered and declined, kept so we don't re-litigate ·
**superseded** = replaced by a later decision.

> Nothing is `accepted` because Claude recommended it. Proposals stay `proposed`.

---

## D-001 — Entry point: `npm create dotcms@latest`, not `curl … | sh`

**Status:** proposed (2026-08-31) · **Supersedes:** the `install.sh` approach in `idea-plan.md`

Ship the installer as a Node program published to npm, invoked `npm create dotcms@latest`.
Drop the shell script entirely.

**Why:**
- Node ≥20 is already a hard requirement for the MCP server, and `idea-plan.md` already
  uses `node` for all JSON/JSONC/TOML editing — so `install.sh` is a POSIX wrapper around
  a Node program. Removing it leaves one artifact in one language, testable with normal
  tooling instead of `sh -n`.
- It eliminates the plan's own first open item ("`curl | sh` executes an unreviewed
  script — document the download-then-run form too"). `npm create` needs no apology.
- Versioning and rollback come free. `create-sanity@6.0.40` was legible in the transcript;
  "whatever `main` said that day" is not.
- Matches the bar exactly (F-017), and `create-dotcms` is available today (F-002).

**Cost:** loses "works with nothing checked out" — but `npx` does that too, so the
JSON-data-block-inside-the-script trick was designed around a constraint that goes away.

**Open:** does the package own provisioning too, or only wiring? Blocked on Q-001.

---

## D-002 — Verify the MCP server actually works before printing success

**Status:** proposed (2026-08-31)

After writing client configs, spawn `@dotcms/mcp-server` and list its tools. If the seven
tools (F-008) don't come back, do not print a success screen — report what failed.

**Why:** This is Sanity's critical bug (F-022) and it is entirely avoidable. `idea-plan.md`
already validates the token before writing anything, which is the right instinct; this
extends it past the write. A success screen is a promise.

---

## D-003 — Pin the MCP server version; do not ship `@latest`

**Status:** proposed (2026-08-31) · **Amends:** `idea-plan.md` §Implementation-2

Every manifest in `idea-plan.md` references `@dotcms/mcp-server@latest`, against a package
at **0.0.13** (F-001). A `0.0.14` with a breaking change would silently break every config
ever written, on every machine, with no user action. Pin a range, and record the resolved
version in `~/.dotcms/env` so we can diagnose from a user's report.

---

## D-004 — One copy of each skill, symlinked per client

**Status:** proposed (2026-08-31)

Install real skill files once, symlink into each client's skill directory — the pattern
Sanity uses (F-020: real files in `~/.agents/skills/`, symlinks in `~/.claude/skills/`).
An update to one file then propagates everywhere.

**Depends on Q-007:** `idea-plan.md` delegates the whole step to `npx skills add`, which
may copy into all 76 directories instead. Check before delegating.

---

## D-005 — The install ends with a sentence to type into the agent

**Status:** proposed (2026-08-31)

The final line of output names the clients to restart and gives a literal sentence to type
in the chat.

**Why:** the single highest-leverage line in Sanity's flow (F-019) and the cheapest thing
on this list. It converts a finished install into a working session. `idea-plan.md`'s flow
currently ends at `→ report`, with no equivalent. Exact wording is Q-003.

---

## D-006 — Idempotent re-runs, but the hand-off always prints

**Status:** proposed (2026-08-31)

A second run detects existing config and reports it rather than redoing work — but it
still prints the hand-off sentence from D-005.

**Why:** Sanity got the first half right and the second half wrong (F-023): their returning
-user run skipped MCP config *and* silently dropped the hand-off, so anyone who missed the
instruction the first time never saw it again.

---

## Carried from `idea-plan.md` — treated as settled unless revisited

These came out of brainstorming and, per Freddy, each one cost a real bug in the draft.
Recorded here so they survive a rewrite of the plan.

| ID | Decision | Status |
|---|---|---|
| D-007 | **Literal token in every client config except VS Code**, which uses `envFile` → `~/.dotcms/env`. Forced by F-010. | accepted |
| D-008 | Write `~/.dotcms/env` in **dotenv form** (`KEY=value`, no `export`) so VS Code's `envFile` can parse it. Shell users source with `set -a; . ~/.dotcms/env; set +a`. | accepted |
| D-009 | **`chmod` as a separate call after writing**, never `writeFileSync`'s `mode` (F-015). | accepted |
| D-010 | **Merge, never replace.** Read existing config, add one key, write back. Unrelated servers and unrelated top-level TOML keys must survive. | accepted |
| D-011 | **Detect by CLI binary *or* config dir** (F-014). | accepted |
| D-012 | **Validate the token with a real API call before writing anything.** | accepted |
| D-013 | **Never echo the token**; read passwords with `stty -echo`. Print at the end which configs hold a literal token, since those need a re-run on rotation. | accepted |
| D-014 | Use `POST /api/v1/apitoken`, not the deprecated `/authentication/api-token` (F-005, F-006). | accepted |
| D-015 | Adding a client is **a row in a registry, not a code path** (F-009). | accepted |
| D-016 | Delegate skill installation to `npx skills add dotcms/skills` rather than reimplementing 76 agents' layouts; fall back to a printed manual command. | accepted, pending Q-007 |
| D-017 | Ship `devin` with `verified:false` — name the path written and invite a bug report. It's shape A (verified 3× over), so the path is the only risk. | accepted |

---

## D-018 — Entry point is `@dotcms/create-app`, extended. Do not build a new package.

**Status:** proposed (2026-08-31) · **Supersedes:** D-001 (`create-dotcms` as a new npm package)

`@dotcms/create-app` already exists, is published (F-025), already provisions dotCMS two
ways (F-026, F-027), already mints a token, reads the default site and configures UVE
(F-029), already scaffolds four frontends (F-030), and already has the spinner/prompt/
error-handling furniture we would otherwise rebuild (F-035). It knows nothing about MCP
or skills (F-033) — that is the *only* gap.

So the work is **an agent-wiring stage added to an existing CLI**, not a new installer.
D-001's reasoning (npm over `curl | sh`, versioning, one language) still holds and is
satisfied better this way: the package exists, is on the release train, and needs no new
name claimed.

**Consequence:** `create-dotcms` on npm (F-002) is no longer needed as our entry point.
Q-002 becomes "claim it defensively as a redirect/alias, or ignore it?"

**Open:** does agent wiring run inline in the create flow, or as a separate
`create-dotcms-app --agents` / `dotcms mcp install` subcommand for people who already
have a project? See Q-016.

---

## D-019 — Write `.env` instead of printing the token

**Status:** proposed (2026-08-31)

Today the CLI prints the env block with the live token to stdout and asks the user to
`touch .env` and paste it (F-032). Write the file directly, `chmod 600`, and print only
the path.

**Why:** it removes a manual step from the critical path, keeps the token out of terminal
scrollback and screen-shares, and the installer is already writing secrets elsewhere under
D-007/D-008/D-009 — the same rules should apply here. Printing a secret and asking the
user to move it by hand is the least safe and least reliable option available.

---

## D-020 — Resolve the token-endpoint conflict in favour of `/api/v1/apitoken`

**Status:** proposed (2026-08-31) — **needs a dotCMS-side answer, see Q-017**

`create-app` uses `/api/v1/authentication/api-token` with a 30-day TTL (F-028).
`idea-plan.md` says that endpoint is `@Deprecated` + `@Hidden` and mandates
`POST /api/v1/apitoken` (F-005, F-006, D-014). Both cannot be right. One code path should
exist for minting, used by both the frontend-env token and the MCP token.

---

## D-021 — Two entry paths, both first-class

**Status:** accepted (2026-08-31, Freddy: "both, 100%") · **Answers:** Q-016

Agent wiring is reachable **both** as a stage inside the `create-app` flow (greenfield:
provision + scaffold + wire, one command) **and** as a standalone command for people who
already have a dotCMS project and want only the MCP server + skills.

Neither is a second-class alias. The standalone path serves the larger population.

---

## D-022 — Token minting: `/api/v1/apitoken`, 90-day TTL

**Status:** accepted (2026-08-31, Freddy) · **Answers:** Q-017 · **Supersedes:** D-020 (proposed), and corrects shipping behavior

Mint with `POST /api/v1/apitoken` (Basic auth → `GET /api/v1/users/current` for `userId`
→ `POST /api/v1/apitoken` with `{userId, expirationSeconds, claims:{label}}` → read
`entity.jwt`). **TTL is 90 days.**

`@dotcms/create-app` currently ships `/api/v1/authentication/api-token` with
`expirationDays: '30'` (F-028) — that is the deprecated, hidden endpoint. **This is a bug
to fix in the existing CLI**, not just a rule for new code. One minting path serves both
the frontend `.env` token and the MCP token.

**Consequence for Q-008:** 90 days is short enough that expiry is a *routine* event, not a
distant edge case. Renewal has to be designed, not warned about.

---

## D-023 — `@dotcms/mcp-server` joins version lockstep; out of scope here

**Status:** accepted (2026-08-31, Freddy) · **Answers:** Q-018

The MCP server will ship at the same version as every other `@dotcms/*` package (F-031).
Do not design compatibility shims around its current `0.0.13`. **Explicitly out of scope
for distribution work** — assume lockstep and move on. This retires D-003's pinning
question: pin to the instance version like everything else.

---

## D-024 — Token TTL is 1 year, plus a re-auth command

**Status:** accepted (2026-08-31, Freddy) · **Supersedes:** D-022's 90-day TTL (endpoint
choice in D-022 stands: `POST /api/v1/apitoken`)

Mint with a **1-year** TTL. Ship a **re-auth command** that re-mints and rewrites every
place the token lives, and document where to change it manually.

**Why the change:** at 90 days expiry is a scheduled event for every retained user, hitting
them as an unexplained 401 inside an agent session. A year pushes it out of the first-run
experience, and an explicit re-auth command means the recovery is one command instead of a
manual hunt through per-client config files.

**Retires Q-008** (JWT renewal unsolved) — renewal is now a command, not a warning.

**Still open:** what the expiry actually *looks like* when it lands (does the MCP server
return an error the skill can recognise and route to the re-auth command?). Tracked as Q-024.

---

## D-025 — Editor wiring is a pre-checked multi-select, and "none" is valid

**Status:** accepted (2026-08-31, Freddy) · **Closes:** the "do you use an AI agent?" question

Detect installed editors and present a **multi-select with all found editors pre-checked**
(Sanity's shape, F-018 — deck p7). The user unchecks what they don't want, or selects
nothing at all.

**Why:** it never asks the user to self-identify as an agent user — a question many can't
answer — and it collapses the fork in the flow into one keypress. Selecting none is a
first-class outcome, which is what keeps the CLI complete for the customers who can't use
agents at all (D-026).

---

## D-026 — One flow, complete for non-agent users, no branch

**Status:** accepted (2026-08-31, Freddy: "not all our customers can use AI agents")

The CLI does the full job for everyone: dotCMS running, frontend scaffolded, `.env`
written, UVE configured, editable. Agent wiring is **additive** — an extra stage and a
final hand-off line, never load-bearing. A user who wires no editors still reaches a
complete, satisfying ending.

**Consequence:** the CLI can't be designed purely as a launchpad. It has two audiences and
one flow, and the aha (D-027) is only reachable by one of them.

---

## D-027 — The aha is the agent building a site, not the CLI finishing

**Status:** accepted (2026-08-31, Freddy: "B") · **Answers:** the Ending A / Ending B fork

The moment that sells dotCMS is the user watching an agent create content types, pages and
content that appear live in UVE — not the CLI's success screen. The CLI's ending is the
*halfway point* for agent-equipped users.

**Why this is our 10x:** Sanity hands you an empty Studio and a schema file (F-024). We can
hand you a site that built itself. The differentiator lives in the skill, not the CLI.

**Tension to resolve:** per D-026 the CLI must still be complete on its own, so the flow
has to deliver a real ending *and* a launchpad without branching.

---

## D-028 — A starter/experience picker sets expectations at scaffold time

**Status:** proposed (2026-08-31, Freddy's proposal) · **Resolves:** Q-025

Rather than designing a separate fast "proof moment", let the user **declare which
experience they want** while still in the CLI — the shape of Sanity's project-template
picker (F-024, deck p9), but named **starter**, not template (D-030). The picker is the expectation-setter: a user who picked "clean" expects to prompt
freely; a user who picked "let the agent build it" expects a planning interview and won't
experience it as homework.

**Why this is better than the proof-moment idea:** it costs one prompt in a place the user
already is, instead of adding a stage to the agent session, and it makes the long
`create-sites` interview *chosen* rather than sprung.

---

## D-029 — Extract a `dotcms-best-practices` skill from `create-sites`

**Status:** accepted (2026-08-31, Freddy: "we're going to have to do it giving everything we're deciding here")

Ship a granular reference skill alongside the orchestrator, so a user can prompt at any
size — "create a content type", "build me a listing page" — without entering the two-phase
site-building workflow.

**Why:** today we have an **orchestrator with no reference**. `create-sites` answers "build
me a whole site" and nothing answers "do this one thing well." Sanity ships exactly this
pair (F-020: `sanity-best-practices` + `sanity-migration`), and their best-practices skill
is what makes small one-line asks work.

**Why it's cheap:** F-037 — `reference/build/` is already a standalone task-indexed manual.
The extraction is a new intent-indexed front door over existing content, not a rewrite.

**Open:** does `create-sites` then *depend on* the best-practices skill (one copy of the
knowledge, two front doors), or do both ship the reference independently? One copy is
obviously right but skill-to-skill dependency support varies by client.

---

## D-030 — Vocabulary: the picker's axis is **starter**, never "template"

**Status:** accepted (2026-08-31, raised by Freddy)

In UI copy, docs, and these notes, the preset content bundle a user chooses is a
**starter**. Never "template".

**Why:** "template" collides three ways in a dotCMS context, and one of them is a
first-class dotCMS entity users already know:

| Term | Meaning | Lives in |
|---|---|---|
| dotCMS **Template** | Page layout — rows/columns, container references (`reference/build/core/05-templates.md`) | the instance |
| Sanity **project template** | Picker preset — content model + sample data (`schemaTypes/*.ts`) | Sanity's repo |
| **Frontend scaffold** | The Next.js/Astro/Angular example app | our repo, via sparse checkout |

Calling the picker "template" would tell a dotCMS developer we're about to choose a page
layout. **Starter** is already dotCMS's own word for this (`CUSTOM_STARTER_URL`,
`single-node-demo-site` — F-027, F-039), so it costs nothing and removes the ambiguity.

**Mapping for anyone reasoning from the Sanity teardown:**
Sanity `schemaTypes/*.ts` (code) ↔ dotCMS **content types** (instance data) ·
Sanity **project template** ↔ dotCMS **starter** (`.zip` loaded into the instance) ·
dotCMS **Template** ↔ no Sanity equivalent.

---

## D-031 — Defer JSON-defined content-type starters

**Status:** accepted (2026-08-31) · **Answers:** Freddy's question — "do we need this for a
good distribution experience?"

We could define content types as JSON and push them through the REST API to build
code-defined starters. **We are not doing it now.**

**Why:**
- The aha is the agent building the site (D-027). Pre-baked content types are the same
  output produced the weaker way, and a polished starter makes the agent's work look worse
  by comparison.
- The starter picker already has real options with no new machinery:
  `single-node-demo-site` (already in the compose file), `CUSTOM_STARTER_URL` (already
  supported), clean, and "let the agent build it".
- Sanity needs project templates because their skills are advisory — without a Movie schema
  there is nothing to look at. Ours builds.
- Real cost: a definition format to design and version, an idempotent apply mechanism,
  maintenance against every content-type change in core, a version-lockstep answer, and
  design work on sample content. That is a product, not a feature — on a path that is not
  broken.

**Trigger to revisit:** if the agent-built path proves too slow or too unreliable to *be*
the aha once people use it, pre-baked content becomes the fallback and this gets real.
Watch for it in usage; do not pre-build against it.

**Where the effort goes instead** — three things on the critical path that are already
wrong in the shipping CLI:
1. `src/index.ts` + `src/constants/index.ts` mint from
   `/api/v1/authentication/api-token` with `expirationDays: '30'` — the deprecated, hidden
   endpoint, and a TTL 10 months short of the 1 year decided in D-024.
2. `finalStepsForNextjs` in `src/utils/index.ts` prints the env block with the live token to
   the terminal and tells the user to `touch .env` and paste it (D-019).
3. `cloneFrontEndSample` in `src/git/index.ts` sparse-checkouts `examples/{framework}` from
   `dotCMS/core` **`main`**, so a `26.8.31-1` CLI installs whatever `main` holds that
   morning, despite the lockstep versioning promise.

---

## D-032 — The CLI writes the frontend wiring; the agent consumes it

**Status:** accepted (2026-08-31, Freddy) · **Refines:** D-026, D-027

Scaffold with the framework's **own** CLI (`create-next-app` etc., shape pinned by explicit
flags), then have our CLI write the dotCMS wiring deterministically: catch-all route,
client config, component map with fallback only, `.env.local`, and the `next.config`
additions. The agent starts from a rendering page and only ever adds deltas — components
for real content types, listing/detail routes.

**Why (Freddy):** "in sanity the agents took +8m just to show me something." Their agent had
to build the foundation *and* the content. Ours inherits a working foundation, so the first
agent response is fast and additive. This also serves the non-agent population with the same
code path — no branch.

**Consequence — we stop owning a frontend app.** Framework upgrades become
`create-next-app@latest`'s problem. It also removes the runtime sparse-checkout of
`examples/{framework}` from `core` `main`, and drops the hard `git` dependency for this path.

**Source of truth:** the CLI owns *creating* the wiring. The skill's
`reference/build/nextjs/` documents the *contract the CLI produced* and how to extend it —
not how to build it. Not duplicated logic; two different jobs.

**Keep:** the rich `examples/nextjs` app stays as what the **demo starter** gets. It stops
being the default, not the product.

**Must carry over** — `next.config.ts` holds knowledge no user would derive:
`reactStrictMode: false` (Strict Mode's double-invoked effects break the UVE bridge), the
custom image loader + `remotePatterns`, the `/dA/:path*` asset rewrite, and the
`/:path*/index` redirect.

---

## D-033 — Two tokens, two users: limited user for the frontend, privileged for MCP

**Status:** proposed (2026-08-31) · **Answers:** Q-030 · **Fixes:** the admin-token-in-browser problem

Permissions live on the **user**, not the token — a token inherits whatever its user can do.
So the frontend's browser-visible token must be minted against a **limited dotCMS user**,
and that makes it a provisioning step in the CLI rather than a parameter on the mint call.

Two tokens, two users, both labelled so they're identifiable and revocable under
System > Users:

| Token | User | Why |
|---|---|---|
| Frontend (`NEXT_PUBLIC_DOTCMS_AUTH_TOKEN`) | limited, read-only | it is inlined into the client bundle and served to every visitor |
| MCP server | privileged | it creates content types, pages, containers, content |

**The two modes need different handling** — consistent with the starter picker already only
working locally:

- **Local Docker:** create the limited user silently. Zero prompts. We own the instance, the
  credentials are already `admin`/`admin`, and there is nothing to protect the user from.
- **Cloud:** this is someone's real instance, and creating a user there is an outward-facing
  action that can also fail on permissions. One confirmation, using the admin credentials
  the CLI already collected — and state *why*: the frontend token ships to browsers, so it
  must not be able to write. Framed that way it builds trust rather than adding friction.

**Idempotency:** a second run must detect the existing limited user rather than creating
duplicates.

---

## D-034 — Use the credentials the user supplies; no limited user, no read-only token

**Status:** accepted (2026-08-31, Freddy: "Lets just do admin for now, no read only, whatever
the user provide as user and password we use that") · **Supersedes:** D-033 · **Closes:** Q-032, Q-033, Q-034

Mint against whatever user + password the user provides. No limited-user provisioning, no
read-only frontend user. The frontend token in `NEXT_PUBLIC_DOTCMS_AUTH_TOKEN` therefore
carries that user's full permissions and is inlined into the client bundle.

**Known and accepted tradeoff:** the concern in F-040/F-041 stands on the facts — a
write-capable token reaches the browser, and `reference/build/nextjs/00-connect.md` advises
against it. Freddy heard it and chose this deliberately to keep scope down. Severity is
confined to cloud mode plus deploying the bundle; local Docker is unaffected (localhost,
credentials already `admin`/`admin`).

**Free mitigation, no scope cost:** emit a comment in the generated `.env.local` and a line
in the cloud-mode output noting that this token is served to browsers and should be replaced
with a restricted user's token before a production deploy. Documentation only — no prompts,
no provisioning, no extra code paths.

**Revisit when:** someone asks for a production-hardening path, or the skill's read-only
guidance is reconciled with what the CLI actually does.

---

## D-035 — One token, used for both the frontend and MCP

**Status:** accepted (2026-08-31, Freddy) · **Answers:** Q-035

Mint once, use the same token for `NEXT_PUBLIC_DOTCMS_AUTH_TOKEN` and for the MCP server
config. Follows from D-034 — both are the same permission level, so separate tokens bought
only labelling and independent revocation, which isn't worth a second mint call.

---

## D-036 — The only content state we know is "empty"

**Status:** accepted, **corrected three times on 2026-08-31** · **Answers:** Q-027

Correction history — v1: cloud instances are empty (wrong). v2: cloud has an unknown state
(too narrow). v3: known only when we created it (still too generous). Freddy: *"'demo starter'
we don't know what is the shape either, demo change all the time"* and custom starter *"is the
same as demo."*

**Final position: the only content state we can reason about is an empty instance.** The demo
starter's shape drifts, and a custom starter's was never ours. Creating the instance is not
the same as knowing what's in it.

| Path | Content state | Known? |
|---|---|---|
| Local Docker, start empty | system content types only | ✅ the only known case |
| Local Docker + demo starter | the demo set — **drifts over time** | ❌ |
| Local Docker + `--starter <url>` | someone else's zip | ❌ |
| Cloud mode | anything | ❌ |
| Standalone MCP install | the customer's own model | ❌ |

**What follows:**
- **Discovery is the default, not the exception.** Every path but one begins by inventorying
  an instance whose contents we can't predict — so inventory is core machinery, not a
  fallback. See D-038.
- **The picker is only ever "start empty, or demo content?"** `--starter` was always a flag,
  never a menu item, so it isn't part of the picker at all.
- Still true: **"let the agent build it" is not a starter** — empty plus the agent is that.

**Consequence for the frontend:** the CLI writes generic wiring with a fallback component and
never tries to match components to content types. The one exception is narrow and conditional:
**if the user picked demo content *and* a framework we ship an example for, clone that
example.** Both parts must hold.

**A reversal worth recording:** F-034 flagged cloning `examples/{framework}` from `core` `main`
as an unversioned-scaffold bug. For the *demo* path that criticism is backwards — the demo
starter arrives via a docker-compose also fetched from `main`, so pulling the example from
`main` is what keeps the two paired. Pinning the example to the CLI's release version would
*break* the pairing whenever the demo moved. The criticism still stands for the generic path,
which is exactly the path that no longer clones anything.

---

## D-037 — The CLI gets a dedicated command for MCP + skills setup

**Status:** accepted (2026-08-31, Freddy: "we're going to need in the cli a command just to
set up the mcp server and skills") · **Implements:** D-021's standalone path

A command that only wires the MCP server and installs the skills — no project creation, no
provisioning, no scaffold. For the population that already has a dotCMS project.

It needs far less than the create flow: instance URL, credentials to mint a token, and the
client multi-select. No project name, directory, framework, or starter.

**This is the path that needs the restart line** — someone adding MCP to an existing project
almost certainly has their editor already open on it, so the config won't be picked up until
they restart. The create flow doesn't have that problem, since the editor is opened after.

---

## D-038 — Ship an inventory script in the skill

**Status:** accepted (2026-08-31, Freddy's proposal)

Since discovery is the default path (D-036), give the agent a **script** it can run to
inventory an instance — content types, sites, existing pages, delivery mode in use — rather
than having it discover the same facts through a series of MCP calls each session.

**Why:** deterministic output, one execution instead of many round trips, cheaper in tokens,
and the same answer every time. Skills can ship executable scripts, so this belongs with the
skill rather than in the CLI.

---

## D-039 — Ask headless or traditional; it's a top-level fork

**Status:** accepted (2026-08-31, Freddy: "we need to ask the user how they want to build the
frontend, headless or traditional, because the agent can build both, the skills is made for
that")

The CLI asks delivery mode, and it maps directly onto the fork the skill already has —
`reference/build/README.md` splits on it, and `PLAN.md §3b` records it:

| Mode | dotCMS renders? | What gets built |
|---|---|---|
| **Traditional (VTL)** | yes | theme + container VTL inside dotCMS — `core/` + `vtl/` |
| **Headless** | no, it serves the page | a frontend app renders it — `core/` + a framework branch |

**This reorders the flow.** "Which framework?" is a *headless-only* question, and in
traditional mode most of the frontend work disappears — no framework prompt, no
`create-next-app`, no wiring delta, no frontend `.env`. MCP and skills are still wired, and
the agent builds themes and container VTL instead.

---

## D-040 — Traditional mode has a local project too; both modes get content-independent wiring

**Status:** accepted (2026-08-31, Freddy) · **Answers:** Q-037 · **Refines:** D-039

Traditional/VTL mode **does** get a local project directory. The agent authors VTL locally and
pushes it with `upload_assets` under `/application/...` (never `/assets` — reserved, per
`core/03-content.md`), because local files are much faster to iterate and debug than editing
through the instance.

**So the flow stays unified longer than D-039 implied.** Project name and output directory are
asked in both modes. Only the directory's *initial contents* differ.

**And the two modes are structurally the same problem** — in each, exactly one piece of
non-obvious wiring must exist or the page silently renders blank, and neither depends on
content types, so the CLI can write both deterministically:

| | Headless | Traditional |
|---|---|---|
| CLI writes | `create-next-app` + delta: catch-all route, client, component map w/ fallback, `.env.local` | theme folder + `template.vtl`, container folder + `preloop`/`postloop` |
| **The line nobody derives** | `reactStrictMode: false` — Strict Mode's double-invoked effects break the UVE bridge | `template.vtl` must loop **`$dotThemeLayout`** — without it the page is a bare shell no matter what you place |
| Agent adds | a component per content type, keyed to the Velocity variable, case-exact | one `<Var>.vtl` per content type, filename = Velocity variable, case-exact |
| Failure mode if missing | unmapped types render the gray fallback bar | VTL errors are swallowed into an empty string **with HTTP 200** |

The same rule as headless applies: the CLI writes only what's content-independent; the
per-content-type files are the agent's job, because content state is unknown (D-036).

**Different endings, though.** Traditional mode has no local dev server — nothing to
`npm run dev`. Its final steps point at the dotCMS instance, not `localhost:3000`.

---

## D-041 — One CLI named `dotcms`, built by repointing the packages that already exist

**Status:** accepted (2026-08-31, Freddy) · **Answers:** Q-036 · **Supersedes:** D-018

The developer-facing surface is a single command, **`dotcms`**, with subcommand groups. It is
reached by changing what the existing packages *are*, not by publishing new ones.

| Package | Action |
|---|---|
| `@dotcms/dotcli` | **Kept.** Bin becomes `dotcms`. `dotcli` stays as an alias that warns and forwards for at least one release cycle. |
| `@dotcms/create-app` | **Kept, repointed** as a thin shim into `dotcms init`. Stops being a full CLI. |
| `dotcli-test` | Deprecated outright — a stray publish still describing itself as "Official command-line tool to manage dotCMS content." |
| `create-dotcms` | Optional. Buys only the shorter `npm create dotcms@latest`; unclaimed, free to hold. |

**Net: zero new packages, one real deprecation.**

**Resulting invocation surface** — every create path reaches the same code:

```
first contact, nothing installed
  npm create @dotcms/app@latest    → shim → dotcms init
  npx @dotcms/create-app           → same
  npx @dotcms/dotcli init          → direct, skips the shim

installed
  dotcms init · agent install · pull/push/publish/status/diff/rm/unlock
  dotcms inspect · login · doctor

legacy, warns and forwards
  create-dotcms-app                → dotcms init
  dotcli <anything>                → dotcms <anything>
```

The shim is not strictly necessary — `npx @dotcms/dotcli init` needs no install either. It buys
discoverability and the `npm create` idiom, which is the reflex form and what a docs homepage
wants.

**Why no new package name.** Freddy: *"why `@dotcms/cli` if I can use `@dotcms/dotcli` and bin
`dotcms` too."* Correct — package name and bin are independent, which `@dotcms/dotcli` already
demonstrates by shipping the `dotcli` command through an `alias` field. An earlier proposal for
`@dotcms/cli` was churn.

**Why create-app isn't deprecated.** It is *already* correctly named for npm's create
convention — `npm init <spec>` maps to `npx create-<spec>`, and the scoped form resolves
`@dotcms/app` → `@dotcms/create-app`, so `npm create @dotcms/app@latest` works today. Repointing
it keeps every existing doc, blog post and CI line working. It becomes to `dotcms` what
`create-sanity` is to `@sanity/cli` — a one-dependency wrapper.

**Precedent, verified.** `@sanity/cli@8.5.0` has bin `sanity` and owns `init`; `create-sanity@6.0.40`
declares exactly one dependency, `@sanity/cli@8.5.0`. Sanity ships **one CLI plus a create-shim**,
not two tools. An earlier claim here that "the industry norm is two separate tools" was wrong.

**Known risk, unresolved — lockstep carries no breaking-change signal.** Versions are dates, so
`@dotcms/dotcli@26.9.x` being a wholly different tool from `26.8.x` — different commands, model
and exit codes — reaches anyone tracking latest with no warning semver would normally provide.
Keeping the package name means this must be handled deliberately: a hard-stop release that
detects old-style usage and exits with instructions, plus docs and comms. Tracked as Q-044.

**Closes the `curl | sh` option.** It stayed open only as an escape from the naming problem.
Naming is settled, so it is now out of bounds.

---

## D-042 — Command groups follow the capability libraries

**Status:** proposed (2026-08-31)

| Group | Capability behind it |
|---|---|
| `dotcms init` | scaffold |
| `dotcms` sync — pull · push · publish · status · diff · rm · unlock | writes + invariants |
| `dotcms agent` | agent-configuration |
| `dotcms inspect` | inventory |
| `dotcms login` · `dotcms doctor` | instance identity |

**`init`, not `create`.** dotCMS already has many creatable things and the MCP server ships
`page_create`; the skill's whole reference is about creating content types, pages, containers and
content. `dotcms create` would read as "create a thing *in* dotCMS." `init` says "set up a project
here" and leaves `create` free for a future `dotcms create page`.

**The agent-configuration group had no home before this.** It is not file sync and not project
creation — its audience already has a project. It needs its own namespace rather than landing
wherever.

---

## D-043 — Capabilities are libraries that return plans; surfaces execute them

**Status:** proposed (2026-08-31)

```
SURFACES      dotcms CLI   MCP server   admin UI   agent   CI
                    └──────────┴──────┬───┴──────────┴───────┘
CAPABILITIES     scaffold · writes · agent-config · inventory
                                   │
FOUNDATION       instance identity · @dotcms/client · @dotcms/ai
```

Every capability is currently implemented *inside* a surface — create-app has its own auth and
health checks, dotcli specs its own `login` and `doctor`, the MCP server has its own everything.
That is why the same two ideas exist three times, and why the write invariants cannot be
enforced: they live in a CLI, so nothing else inherits them.

**The rule: a capability returns a described intent; only the outermost surface performs it.**
Agent-config returns the set of config files that *would* exist, not a writer that writes them.
Scaffold returns the files a project should contain. Consequences: dry-run is inherent rather
than a flag; the admin UI becomes a real surface with no new logic, rendering the same plan the
CLI executes; tests need no sandboxed filesystem.

**Where the invariants live is an API-shape question, not a code question.** The four dotcli
invariants are currently specced as properties of `dotcli push`. Moved into the write capability
— with *no other exported way to write* — they become true of dotCMS writes generally: the CLI,
the MCP server, an agent, and a customer's CI all inherit them. This is the only structural
answer to Q-041, and it is the same principle `@dotcms/ai` already claims for itself: *"Safety
isn't a setting you turn on; it's the shape of the runtime."*

Not published — scaffold, agent-config and inventory stay workspace-internal. Nobody outside
needs to generate a Next.js wiring delta.

---

## D-044 — Sunset both legacy commands after 6 months; `dotcms` is the only command

**Status:** accepted (2026-08-31, Freddy: "we should sunset both and just use dotcms and we can
say 6 months no problem") · **Refines:** D-041

Both legacy bins are transitional, not permanent:

| Command | Fate |
|---|---|
| `dotcli` | warns and forwards, removed after **6 months** |
| `create-dotcms-app` | warns and forwards, removed after **6 months** |
| `dotcms` | the only command a human types |

**Why sunset rather than keep:** the point of consolidating was to have one name. Keeping both
permanently means a name was added, not consolidated, and "which one should I use?" becomes a
support question forever. The window is generous enough to cover docs, blog posts, Dockerfiles
and CI scripts we don't control; the notice should be one quiet line, not a banner on every
invocation.

**Consequence — `create-dotcms` becomes load-bearing.** With `create-dotcms-app` gone, the only
remaining first-contact form is `npx @dotcms/dotcli init`, which puts the old package name on the
docs homepage beside a `dotcms` command. D-041 called `create-dotcms` optional and cosmetic; this
decision makes it the one form that reads correctly:

```
npm create dotcms@latest     → create-dotcms → dotcms init
```

**Migration note:** the current package puts `dotcli` on PATH via a postinstall symlink rather
than npm's `bin` field, so the upgrade has to clean up the symlink it previously created or a
stale one can shadow the new command.

**Reopened by this decision** — see Q-047: whether the package name should also align, since
after the sunset `@dotcms/dotcli` is still what appears in `npm i -g` lines and
`devDependencies` while every command says `dotcms`.

---

## D-045 — Keep the package name `@dotcms/dotcli`; no rename

**Status:** accepted (2026-08-31, Freddy) · **Answers:** Q-047 · **Confirms:** D-041

No `@dotcms/cli`, no package rename. All docs and communication get updated to point at the
`dotcms` command, so the package name surfaces only in the global-install line.

**This is a normal shape, not a wart.** Package name and command name differ routinely:
`@angular/cli` → `ng` · `typescript` → `tsc` · `@sanity/cli` → `sanity`. `@dotcms/dotcli` →
`dotcms` is unremarkable.

**Deprecation warnings** fire when someone invokes `dotcli` or `@dotcms/create-app` during the
6-month window (D-044). Requirements:

- **stderr, not stdout** — people have `dotcli` in CI that parses output; a notice on stdout can
  break a working pipeline during the very window meant to protect them
- **once per invocation**, not per operation
- **never change the exit code** — the warning must not turn a passing script into a failing one

Docs work is Freddy's, and it is what makes this decision safe: the mismatch costs nothing
precisely because no new documentation teaches the old names.

---

## D-046 — Extract capability libs first; ship value through `@dotcms/create-app` before any rename

**Status:** accepted (2026-08-31, Freddy: "we can ship `dotcms` commands + the updated
`@dotcms/create-app` supporting those commands by centralizing the code with the capability
libs") · **Supersedes:** the sequencing sketched earlier (freeze create-app → build CLI → swap)

**Order of work:**

1. **Extract the capability libs** — provisioning, validation, instance identity, scaffold,
   agent-config, inventory
2. **Rewire `@dotcms/create-app` onto them and add the agent-config stage.** Same name, still
   shipping, customers get MCP + skills now
3. **Build the `dotcms` commands** on the same libs, at whatever pace
4. **At parity:** create-app → shim, bin → `dotcms`, deprecations begin (D-041, D-044)

**Why this is better than the earlier plan:** it puts the capability extraction on the critical
path and makes naming, consolidation and sunsetting optional follow-on. Step 2 delivers the
business need without depending on 3 or 4 — if consolidation slips, nothing customer-facing is
blocked. It also avoids a frozen window on the one tool customers actually touch today.

**Everything else we decided lands in step 2, not after a rename** — the token endpoint fix, the
`.env` write, generating the scaffold instead of cloning from `main`, the delivery-mode fork.
None of them depend on what the command is called.

**Bonus:** the libs get exercised by a shipping product before a second consumer exists, which is
where API boundary problems are cheapest to find.

**Design caution — do not over-fit to create-app.** While it is the only consumer it will be
tempting to shape the libs around its flow, and create-app *always* has a TTY and *always* has a
project directory. Standalone `agent install` has neither: a customer with a cloud instance and
no repo is the case that decides whether config is project-scoped or machine-scoped. **Design
agent-config for that harder case from day one**, or the reduced-copy problem gets built in
reverse and stays invisible until the CLI tries to use it.

---

## D-047 — Signal the dotcli break through docs and comms, not a hard stop

**Status:** accepted (2026-08-31, Freddy) · **Answers:** Q-044

The TypeScript rewrite ships under `@dotcms/dotcli` with no in-band breaking-change mechanism.
Announce it, update all documentation, let the version bump carry it.

**Accepted risk:** lockstep versions are dates, so a pipeline pinned to `@latest` changes tools
without warning. Mitigated by the 6-month alias window (D-044) — `dotcli` keeps working and
forwards, so the common failure is a changed command surface rather than a dead command.

**Rejected:** a hard-stop release that detects old-style usage and exits (more work than the risk
warrants) · a new package name (reverses D-041/D-045) · versioning the CLI outside lockstep
(breaks the one rule the whole ecosystem follows).

---

## D-048 — Literal token per client config

**Status:** accepted (2026-08-31, Freddy) · **Answers:** Q-042 · **Confirms:** the plan as written

Each client config holds the token inline, as `idea-plan.md` researched. No keychain resolution,
no HTTP transport, no OAuth.

**Rejected, with the research behind each:** having the server resolve its own credentials from a
config file or keychain (possible — where it looks is our choice, not a protocol constraint — but
adds a dependency and makes "which instance" ambiguous on a multi-instance machine) · HTTP + OAuth
2.1 (where the ecosystem is heading, and xmcp already supports the transport, but it needs an
authorization server and changes the deployment model from spawned-process to something that must
be running).

**Accepted costs:** the secret is duplicated across N client config files, and rotation means
re-running the installer. The re-auth command (D-024) must therefore rewrite every location.

**Note for later:** stdio has no secret mechanism beyond the config `env` block — that is the
protocol, not a client gap. If dotCMS ever offers a hosted/remote MCP server, HTTP + OAuth becomes
available and this decision should be revisited then.

---

## D-049 — MCP server and CLI keep their own write logic, sharing `@dotcms/ai/runtime`

**Status:** accepted (2026-08-31, Freddy) · **Answers:** Q-041 · **Closes:** Q-046

Freddy: *"MCP server have its logic and cli will have its own, we still use the
`@dotcms/ai/runtime` in both and if there is anything to share we can do that."*

The shared substrate is **`@dotcms/ai/runtime`**, not an extracted write library. Each surface
implements its own write path on top of it; sharing happens opportunistically where it turns out
to be worth it, rather than by design up front.

**What this means, stated plainly:** dotcli's four invariants are properties of dotcli, not of
dotCMS writes generally. An agent writing through `upload_assets` or `execute` does not inherit
drift detection, draft-only, or workflow-respecting publish. That is a known and accepted position,
not an oversight — the risk is zero on local Docker (nobody else is writing) and real on shared or
cloud instances.

**Where governance can still land:** `@dotcms/ai`'s adapter and allow-list layer is common to both,
so it remains the one place a policy could be enforced across every surface — *"you decide the
surface… expose `scan` and `read`; never expose `delete`."* If the shared-instance failure shows
up in practice, that is the place to fix it, and it does not require the library boundary this
decision declined.

**Supersedes** the recommendation in D-043 that the invariants move into a capability library with
no other exported way to write. The rest of D-043 — capabilities returning plans, surfaces
executing — still stands.

---

## D-050 — The hand-off sentence is "Get started with dotCMS"

**Status:** accepted (2026-08-31, Freddy) · **Answers:** Q-003

The literal line the CLI prints for the user to type into their agent. Mirrors the benchmark,
works for both delivery modes, and reads as an invitation rather than a command.

---

## D-051 — Eight clients in the registry

**Status:** accepted (2026-08-31, Freddy) · **Answers:** Q-004

The six already researched — Claude Code, Codex, Cursor, opencode, VS Code, Devin — plus
**Antigravity** and **GitHub Copilot CLI**, both of which Sanity wires.

**Neither addition is researched yet.** Their config shapes, file paths, and scope support have to
be determined before they can be registry rows, and both may or may not fold into the existing four
shapes. Tracked as Q-048.

`pi` was not included — it has no MCP support and would have made the registry carry two kinds of
entry.

---

## D-052 — Skills keep shipping from the repo via `npx skills add`

**Status:** accepted (2026-08-31, Freddy) · **Answers:** Q-020, Q-045

No npm package, no bundling into the CLI. `npx skills add dotcms/skills` stays the mechanism.

**Accepted tradeoff, stated plainly:** skills remain **unversioned**. There is no update path and
no signal to a developer that theirs describes an older dotCMS — the same trap as the frontend
examples fetched from `main`. The knowledge-staleness problem is **not solved by this plan** and
remains open as a product risk.

**Why it's defensible now:** it costs nothing, skills ship independently of the release train, and
the content is still changing fast enough that pinning it to dotCMS releases would mostly create
friction. Revisit when skill content stabilises or when a stale-skill failure is observed.

---

## D-053 — Two skills in v1; no migration skill

**Status:** accepted (2026-08-31, Freddy) · **Answers:** Q-005

`dotcms-create-sites` (orchestrator) and `dotcms-best-practices` (reference, extracted from it).

Migration is a much larger surface — AEM, Contentful, WordPress, Drupal each need real research —
and it does not block onboarding. Sanity ships one, but ours is not a gate on Phase 2.

---

## D-054 — Ask everything up front, then boot

**Status:** accepted (2026-08-31, Freddy) · **Answers:** Q-026

All prompts complete before provisioning starts, then one uninterrupted wait the user can walk
away from.

**Why over interleaving:** simpler to reason about, simpler to run non-interactively, and no
answers are collected against an instance that might fail to come up. The cost is that the Docker
wait stays dead air — accepted.

---

## D-055 — Test tokens were revoked

**Status:** closed (2026-08-31, Freddy) · **Answers:** Q-015

All tokens minted during token-path testing have been revoked. The only security item on the open
list, now closed.

---

## D-056 — In traditional mode the agent builds the directory structure, not the CLI

**Status:** accepted (2026-08-31, Freddy) · **Answers:** Q-039, Q-040 · **Amends:** D-040

Freddy: *"the agent will create this based on the answers of the plan but in the skills they have
that information, we can make it more clear in the skill maybe."*

The CLI creates the project directory. **Everything inside it — theme folder, `template.vtl`,
container folders, `preloop`/`postloop` — is the agent's work**, driven by the skill and the answers
captured in `PLAN.md`/`DESIGN.md`. No `package.json`, no npm tooling; the mode never runs a build.

**This amends D-040**, which said the CLI writes traditional mode's content-independent wiring the
way it writes headless wiring. It does not.

**Consequences, stated so they are deliberate rather than discovered:**

- **The two modes are no longer symmetrical.** Headless: the CLI writes the wiring and the agent
  adds per-content-type files. Traditional: the agent writes everything.
- **The `$dotThemeLayout` loop moves from CLI-owned to skill-owned.** It is the line nobody derives
  and its absence renders a blank page with HTTP 200, so the skill must state it unmissably —
  `vtl/00-wiring.md` and `vtl/02-themes.md` already do, and Freddy flagged making it clearer.
- **A non-agent traditional user gets an empty directory.** That is acceptable: traditional dotCMS
  is authored in dotAdmin, so the CLI's job for that user ends at a running instance and a URL.
  Invariant 1 still holds — the ending is complete for them, it just isn't a local project.

**Action:** review the traditional branch of the skill for whether the directory structure and the
theme-loop requirement are stated clearly enough to be executed without the CLI's help.

---

## D-057 — `--starter` wires agents too

**Status:** accepted (2026-08-31, Freddy) · **Answers:** Q-022

A provisioned instance plus MCP and skills is a good "I'll build the rest with the agent" starting
point: content is loaded, nothing is scaffolded, the agent takes it from there.

**Consequence:** `--starter` currently skips token minting entirely. Agent wiring needs a token, so
**that mode must now mint one** — a real change to what the flag does, not just an added stage.

---

## D-058 — Expose Vue in the CLI; the demo-gap question dissolves

**Status:** accepted (2026-08-31, Freddy: "we have the vue example now, but is not in the cli") · **Answers:** Q-038

`core/examples/vuejs` exists and `@dotcms/vue` publishes at `26.8.31-1`, but the CLI offers only
four frameworks. Add Vue.

With every offered framework backed by an example, "demo content plus a framework with no example"
stops being a state that can occur. If a future framework ships without one, the generic path —
scaffold, dotCMS delta, fallback component only — is the fallback.

---

## D-059 — Token expiry surfaces as a recognizable MCP error

**Status:** accepted (2026-08-31, Freddy) · **Answers:** Q-024

On auth failure the MCP server returns a message the agent can act on — naming the re-auth command
rather than passing through a bare 401. The agent then tells the user what to run instead of
guessing at a fix or retrying.

No proactive expiry warning in v1.

---

## D-060 — UVE stays at its init-time value; re-pointing is a dotAdmin task

**Status:** accepted (2026-09-01, Freddy) · **Answers:** Q-023

The CLI sets a sane dev default (`http://localhost:{port}` for the chosen framework) and nothing
re-points it afterward. Changing it for staging or production is an admin task in dotCMS, where the
setting already lives. No new CLI surface, no `doctor` repair, no agent involvement.

---

## D-061 — Publish to all registries, writing agent-plugins.org to spec

**Status:** accepted (2026-09-01, Freddy) · **Answers:** Q-012, Q-010

Ship manifests for every registry — the Claude Code plugin manifest, skills.sh, and
agent-plugins.org — with agent-plugins.org written against the documented shape even though its two
schema URLs 404 today. Revisit when they land.

Accepted cost: writing manifests against a spec that cannot currently be validated. The upside is
maximum discovery reach if registries turn out to matter, and the assumption that they do stays
untested either way.

---

## D-062 — Verify the VS Code and Devin paths before release

**Status:** accepted (2026-09-01, Freddy) · **Answers:** Q-013 · **Now an action item, not a question**

Someone installs each client and runs the wiring for real. Both are already-verified config shapes
(A and D), so the file path is the only risk — and a wrong path fails silently in a way users
attribute to us.

Supersedes `idea-plan.md`'s proposal to ship Devin with `verified:false` and invite bug reports.
