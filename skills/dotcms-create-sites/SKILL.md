---
name: dotcms-create-sites
description: Plans and builds a complete dotCMS site in two phases. Phase 1 interviews the user and writes PLAN.md (purpose, sitemap, data model, every fact tagged) and DESIGN.md (visual identity tokens). Phase 2 builds the site through the dotCMS MCP tools — content types, rendering scaffold, pages, content, placement, and verification — following step-by-step references that keep the build off known failure paths and stop invented facts shipping as real. Supports both VTL-rendered and headless (Next.js) delivery. Use when someone wants to build, scaffold, or create a new dotCMS site or microsite.
---

# dotCMS Create Sites

Two phases: **plan**, then **build**. You do both.

- **Phase 1 — Plan.** Interview the user and write two artifacts:
  - **`PLAN.md`** — everything non-visual: purpose, audience, hostname, sitemap, sections, data model, and every fact tagged confirmed / placeholder / n-a.
  - **`DESIGN.md`** — the visual identity (YAML tokens + prose rationale). **Colors are never invented** — sample them from the user's logo/assets if provided, or ask.
- **Phase 2 — Build.** Read both files plus the references below, then create the site in dotCMS in dependency order: site → content types → rendering scaffold → pages → content → placement → publish → verify. The scaffold and the verify step differ by delivery mode (§3b of PLAN.md).

## Workflow

Copy this checklist and track progress.

```
Plan Progress (Phase 1) — references live in reference/plan/:
- [ ] 1. If PLAN.md/DESIGN.md already exist, read, confirm, interview only on gaps.
        Otherwise start fresh — you are building them, not reading them.
- [ ] 2. Run the interview (plan/interview.md) — infer from assets, confirm the drafted plan in ONE batch; ask upfront only what can't be inferred (delivery mode, transaction model, real-vs-placeholder facts)
- [ ] 3. Draft prose in the agreed voice; collect or defer every fact; source colors from logo/assets or ask
- [ ] 4. Write DESIGN.md (visual identity) from plan/design-template.md
- [ ] 5. Write PLAN.md (structure + tagged facts) from plan/plan-template.md
- [ ] 6. Confirm tagging is complete — every FACT field tagged, every STRUCTURE section
        carrying a heading tag — and PLAN.md's top checklist lists all gaps
- [ ] 7. Confirm the plan with the user before building

Build Progress (Phase 2) — load only the build/ file for the step you're on (see build/README.md
for the branch map and tool routing). Order is dependency order: everything needs the site,
a template needs its theme and containers, and a page needs the template — so the
scaffold is built bottom-up before pages and placement.
- [ ] 8.  Check what a page needs to render — the wiring contract (build/core/00)
- [ ] 9.  Choose the mechanism per need — DESIGN ONLY, nothing is built yet.
          VTL: content type vs widget vs detail page. Headless: plan one component
          per content type that can appear on a page (build/{vtl,nextjs}/01)
- [ ] 10. Create and publish the SITE — everything below needs its id (build/core/01)
- [ ] 11. Create content types — data + editable sections (build/core/02)
- [ ] 12. Build the rendering scaffold, IN THIS ORDER (the template's POST names
          container paths that must already resolve, plus a theme id if VTL):
          a. theme — VTL: create it (build/vtl/02). HEADLESS: create NO theme; omit
             the key and the template takes SYSTEM_THEME.
          b. containers (build/core/06) — both modes create the folder and one
             <Var>.vtl per accepted type. VTL writes the markup (build/vtl/03);
             HEADLESS leaves those files empty — React renders, the filename only
             registers the type for the editor.
          c. create + publish the template (build/core/05)
          d. HEADLESS ONLY — the app side, once the types from step 11 exist:
             client config (build/nextjs/00), next.config (02), routing (03), and
             **write + register one component per content type** (01). The map keys
             are the type variables, so the types must exist first. Skip this and
             every slot renders "no component".
- [ ] 13. Create pages — requires the template from step 12c (build/core/04)
- [ ] 14. Wire listings & detail pages (build/{vtl,nextjs}/04)
- [ ] 15. Create content — fire an action on each contentlet (build/core/03)
- [ ] 16. Place content into slots — requires the container from step 12b (build/core/09)
- [ ] 17. Publish everything, page last
- [ ] 18. Verify (build/{vtl,nextjs}/05) — VTL: validate with /api/vtl/dynamic AND
          page_verify every page type. Headless: page_verify does NOT apply; confirm
          every content type on every page resolves to a component.
          Either way, nothing renders as [PLACEHOLDER] that shouldn't
```

Phase 1 is the interview and cannot be skipped unless both files already exist and the user confirms them. Don't start Phase 2 until the plan is confirmed.

## References

The `reference/` folder mirrors the two phases. Load a file when you reach its step — don't read everything up front.

**Phase 1 (plan) → `reference/plan/`**
- **How to interview + how to tag answers** → [reference/plan/interview.md](reference/plan/interview.md)
- **DESIGN.md output format** (visual identity) → [reference/plan/design-template.md](reference/plan/design-template.md)
- **PLAN.md output format** (structure + facts) → [reference/plan/plan-template.md](reference/plan/plan-template.md)

**Phase 2 (build) → `reference/build/`** — open the file for your step. Start with
[reference/build/README.md](reference/build/README.md) if you need the branch map,
tool routing, or the spec-status note.

*Both delivery modes — `core/`:*
- [00-what-must-exist.md](reference/build/core/00-what-must-exist.md) — the wiring contract, read first
- [01-site.md](reference/build/core/01-site.md) — create and publish the site
- [02-content-types.md](reference/build/core/02-content-types.md) — content types + fields
- [03-content.md](reference/build/core/03-content.md) — creating content
- [04-pages.md](reference/build/core/04-pages.md) — creating pages
- [05-templates.md](reference/build/core/05-templates.md) — template layout + publish
- [06-containers.md](reference/build/core/06-containers.md) — containers as slots
- [09-placement.md](reference/build/core/09-placement.md) — placing content into slots

*VTL-rendered only — `vtl/`:*
- [00-wiring.md](reference/build/vtl/00-wiring.md) · [01-choose-mechanism.md](reference/build/vtl/01-choose-mechanism.md) · [02-themes.md](reference/build/vtl/02-themes.md) · [03-containers.md](reference/build/vtl/03-containers.md) · [04-listings-and-details.md](reference/build/vtl/04-listings-and-details.md) · [05-verify-and-debug.md](reference/build/vtl/05-verify-and-debug.md)
- [velocity.md](reference/build/vtl/velocity.md) — VTL authoring lookup, not a step; consult while writing `.vtl`

*Headless, Next.js — `nextjs/`:*
- [00-connect.md](reference/build/nextjs/00-connect.md) · [01-component-contract.md](reference/build/nextjs/01-component-contract.md) · [02-next-config.md](reference/build/nextjs/02-next-config.md) · [03-routing.md](reference/build/nextjs/03-routing.md) · [04-listings-and-details.md](reference/build/nextjs/04-listings-and-details.md) · [05-verify.md](reference/build/nextjs/05-verify.md)
- Next.js is the only framework branch in this skill; Angular/Vue/Astro have upstream examples but no branch here. The SDK APIs are owned by the `@dotcms/client`, `@dotcms/react` and `@dotcms/uve` npm READMEs and the `examples/nextjs` app in `dotCMS/core`; this branch shows the basics and links for detail, never restating the API.

**Both branches share the same numbering** — `00` wire up · `01` type↔renderer contract ·
`02`–`03` mode-specific plumbing · `04` listings & detail · `05` verify — so a shared
step is the same number in either mode.

## Tagging (the core rule)

Every field carries one tag:
- `[confirmed]` — real value the user gave.
- `[PLACEHOLDER — needs human]` — real value exists but not yet available → build renders a visible TODO.
- `[n/a — intentionally omitted]` — fact doesn't exist → build removes the field/section.
- `[ai-draft — approve]` — AI-written prose/tokens awaiting sign-off (never invented facts).

## Done when

Both `PLAN.md` and `DESIGN.md` exist and are fully tagged (every FACT field, every STRUCTURE section); the site is built in dotCMS, everything is published, and **every page type verifies through its delivery mode's verify step** — VTL: the LIVE render is correct ([reference/build/vtl/05-verify-and-debug.md](reference/build/vtl/05-verify-and-debug.md)); headless: the published page returns populated contentlets and the app renders every one ([reference/build/nextjs/05-verify.md](reference/build/nextjs/05-verify.md)); no `[PLACEHOLDER]` field renders as if it were a real value, and every `[n/a]` field/section was removed rather than flagged. `[ai-draft]` copy is called out for human approval before launch.
