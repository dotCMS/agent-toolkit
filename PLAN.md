# dotCMS skills, plugins and marketplaces — execution plan

**Date:** 2026-09-01
**Author:** Freddy Montes
**Status:** Decided — ready to build
**Repo:** `dotcms/skills` — this plan covers **only** what ships from here
**Paired plan:** `dotcms/core` → `docs/cli/CLI_DISTRIBUTION_PLAN.md` (the CLI, capability libraries, MCP wiring)
**Reference:** `ecosystem.md` (inventory) · `archive/decisions.md` (why) · `dotcli.md` (the sync half)

---

## 1. What we're building

The **knowledge and the channels it reaches agents through**: the skills themselves, and the
plugin and marketplace manifests that make them discoverable.

The CLI *installs* what this repo publishes. It does not live here. Everything about `dotcms init`,
capability libraries, token minting and client config files belongs to the paired plan.

## 2. Scope

|  |  |
|---|---|
| **In** | `dotcms-create-sites` — the existing orchestrator skill |
|  | `dotcms-best-practices` — extracted from it |
|  | The inventory script the agent runs to discover an instance |
|  | Skill content updates forced by CLI decisions (§5) |
|  | Plugin manifests — Claude Code plugin + its MCP declaration |
|  | Marketplace manifests — agent-plugins.org, skills.sh |
| **Out** | Everything CLI: capability libraries, `dotcms` commands, the rename and sunset |
|  | Writing client config files, minting tokens, provisioning |
|  | A migration skill — not in v1 |
|  | Versioning skills — they ship unversioned from this repo (§6) |

## 3. Invariants

1. **A skill must work for someone who found it without our CLI.** Registry installs are a real
   path; a skill that assumes `dotcms init` ran is broken for them.
2. **The reference content lives once.** `create-sites` and `best-practices` share it by reference,
   never by duplication.
3. **What the CLI writes, the skill documents but does not re-derive.** Where the CLI owns a file,
   the skill describes the shape it will find (§5).

## 4. The two skills

**Ship exactly two.** No migration skill in v1 — it is a much larger surface (AEM, Contentful,
WordPress, Drupal each need real research) and it does not block onboarding.

Today `dotcms-create-sites` is an orchestrator with no reference: nothing answers *"create a content
type."* Extract **`dotcms-best-practices`** from it.

The extraction is cheap because the skill is already split along that seam:

```
skills/dotcms-create-sites/
  SKILL.md              113 lines   orchestration  → stays
  reference/plan/       225 lines   orchestration  → stays
  reference/build/      940 lines   already a task-indexed manual  → becomes the new skill's body
    core/    8 files    what-must-exist, site, content-types, content,
                        pages, templates, containers, placement
    vtl/     7 files
    nextjs/  6 files
```

`reference/build/`'s own README already says *"Load only the file for the step you're on — don't
read the folder up front."* That is a lookup manual, not a workflow. The new skill is an
**intent-indexed front door** over existing content — indexed by what the user wants rather than by
build step — not a rewrite.

**Sharing, not duplicating.** Skill frontmatter has no dependency mechanism (`name` and
`description` only), and none is needed: both skills install from the same
`npx skills add dotcms/skills`, so `create-sites` references `dotcms-best-practices` by name and the
reference content exists once.

## 5. Skill content changes forced by CLI decisions

**Headless — `reference/build/nextjs/00-connect.md` splits.** Roughly half of it (the four env vars,
`createDotCMSClient`, `DotCMSLayoutBody`/`useEditableDotCMSPage`) becomes *"the CLI already did this
— here is the shape you will find."* The other half stays essential and the CLI cannot provide it:
in headless you omit the theme so the server assigns `SYSTEM_THEME`, containers are still required,
and each content type still needs a `<Var>.vtl` that is only a comment — the filename is what
registers the type so UVE offers it to authors.

**Traditional — the skill now owns the whole structure.** The CLI creates the project directory and
nothing inside it. The agent builds the theme folder, `template.vtl`, container folders and
`preloop`/`postloop` from the skill and the captured plan. So the skill must state unmissably that
**`template.vtl` has to loop `$dotThemeLayout`** — without it the page is a bare shell whatever you
place, and a VTL error is swallowed into an empty string **with HTTP 200**, so "no error" is not
evidence anything rendered. `vtl/00-wiring.md` and `vtl/02-themes.md` say this; the question is
whether they say it loudly enough to be executed without the CLI's help.

**Both modes — the agent adds per-content-type files only.** Component keys and `<Var>.vtl`
filenames must equal the content type's Velocity variable, case-exact.

## 6. Distribution

**Skills ship from this repo** via `npx skills add dotcms/skills`. No npm package, no bundling into
the CLI.

That installer **symlinks** rather than copies: real files land in `~/.agents/skills`, and each
agent's directory (`.claude/skills`, `.cursor`, `.codex`, `opencode`) gets a link, with a copy
fallback where symlinks are unavailable. One update propagates everywhere.

**Accepted tradeoff:** skills stay **unversioned**. There is no update path and nothing signals to a
developer that theirs describes an older dotCMS — the same trap as the frontend examples fetched
from `main`. Revisit when the content stabilises or a stale-skill failure is observed.

## 7. Plugins and marketplaces

Publish to every channel. Registry presence is an unproven assumption — `idea-plan.md` held that
registries drive discovery while the installer is the primary channel, and nothing has tested that —
but the manifests are cheap and the reach matters if it turns out to be real.

| Channel | Files |
|---|---|
| Claude Code plugin | `.claude-plugin/plugin.json` + `.mcp.json` |
| agent-plugins.org | `plugin.json` + `mcp.json` at root |
| skills.sh | consumed from `skills/` directly |

All manifests reference **`@dotcms/mcp-server`**. The two agent-plugins.org schema URLs **404 today**
— write to the documented shape anyway and revisit when they land.

## 8. The seam with the CLI

Stated identically in both plans. This is where a two-repo split goes wrong.

| Contract | Owner |
|---|---|
| Skills are installed by `npx skills add dotcms/skills` | The CLI **calls** it; this repo **publishes** what it fetches |
| The CLI prints `Get started with dotCMS` | The CLI owns the line; **the skills must respond well to that exact phrase** |
| Headless wiring — catch-all route, client config, component map, `.env`, `next.config` | CLI writes it; the skill documents the shape (§5) |
| Traditional structure — theme, `template.vtl`, containers | CLI writes nothing but the directory; **the skill owns all of it** |
| MCP server identity in manifests | This repo's manifests and the CLI's client configs must name the same server |
| Instance discovery | **Unresolved — see §10** |

## 9. Acceptance scenarios

| Scenario | Expected |
|---|---|
| A developer installs the skills from a registry, never having run our CLI | Both skills work. Neither assumes `dotcms init` ran, and each says what it needs (an instance, a token, MCP configured) |
| `Get started with dotCMS` typed into a fresh agent session | The agent inventories the instance and reports what it found, without starting a long build unasked |
| "Create a content type" — a small, single-step ask | `dotcms-best-practices` answers it directly. The user is not pulled into the two-phase site-building interview |
| "Build me a site" | `create-sites` runs its interview → plan → build, and pulls reference content from `best-practices` rather than carrying its own copy |
| Headless project scaffolded by the CLI, agent asked to add a content type | The agent adds the component and registers it under the case-exact Velocity variable. It does not recreate the catch-all route or `next.config` |
| Traditional project, empty directory | The agent creates theme, `template.vtl` with the `$dotThemeLayout` loop, containers, and per-type `<Var>.vtl` — then verifies in LIVE, since HTTP 200 is not evidence |
| Both skills installed, then one updated | The symlink means the update is live without reinstalling |

## 10. Action items

**Build**

- Extract `dotcms-best-practices` — intent-indexed front door over `reference/build/`.
- Rewrite the CLI-owned half of `nextjs/00-connect.md` as "here is the shape you will find."
- Harden the traditional branch: make the `$dotThemeLayout` requirement and the directory structure
  impossible to miss.
- Write the inventory script.
- Write the four manifests; agent-plugins.org to the documented shape despite the 404s.

**Unresolved**

- **Who owns instance discovery?** The skill ships an inventory script (this repo) and the CLI has an
  inventory capability (paired plan). They discover the same facts. Options: the script is
  independent · the script shells out to `dotcms inspect --json` · the CLI's capability is the only
  implementation and the skill requires the CLI. The last is cleanest but breaks invariant 1 —
  someone who installed from a registry has no CLI. **Decide before writing either.**
