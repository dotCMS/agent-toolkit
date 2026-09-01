---
name: dotcms-create-sites
description: Plans and builds a complete dotCMS site in two phases. Phase 1 interviews the user and writes PLAN.md (purpose, sitemap, data model, every fact tagged) and DESIGN.md (visual identity tokens). Phase 2 builds the site through the dotCMS MCP tools — content types, rendering scaffold, pages, content, placement, and verification — working through the `dotcms-best-practices` skill's references, which keep the build off known failure paths, and stopping invented facts shipping as real. Supports both VTL-rendered and headless (Next.js) delivery. Use when someone wants to build, scaffold, or create a new dotCMS site or microsite.
---

# dotCMS Create Sites

Two phases: **plan**, then **build**. You do both.

- **Phase 1 — Plan.** Interview the user and write two artifacts:
  - **`PLAN.md`** — everything non-visual: purpose, audience, hostname, sitemap, sections, data model, and every fact tagged confirmed / placeholder / n-a.
  - **`DESIGN.md`** — the visual identity (YAML tokens + prose rationale). **Colors are never invented** — sample them from the user's logo/assets if provided, or ask.
- **Phase 2 — Build.** Read both files, then build the site in dotCMS in dependency order, following the build references in the **`dotcms-best-practices`** skill: site → content types → rendering scaffold → pages → content → placement → publish → verify. The scaffold and the verify step differ by delivery mode (§3b of PLAN.md).

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

Build Progress (Phase 2)
>> EVERY file cited below is `dotcms-best-practices/reference/<branch>/<file>`. Load that skill
>> once, up front. Its reference/README.md carries the same list in dependency order plus the
>> branch map and tool routing.
>> Note: step numbers and file numbers are different sequences — step 9 is not core/09.
Order is dependency order: everything needs the site, a template needs its theme and
containers, and a page needs the template — so the scaffold is built bottom-up before
pages and placement.
- [ ] 8.  Check what a page needs to render — the wiring contract (core/00-what-must-exist.md)
- [ ] 9.  Choose the mechanism per need — DESIGN ONLY, nothing is built yet.
          VTL: content type vs widget vs detail page. Headless: plan one component
          per content type that can appear on a page (vtl/01-choose-mechanism.md or nextjs/01-component-contract.md)
- [ ] 10. Create and publish the SITE — everything below needs its id (core/01-site.md)
- [ ] 11. Create content types — data + editable sections (core/02-content-types.md)
- [ ] 12. Build the rendering scaffold, IN THIS ORDER (the template's POST names
          container paths that must already resolve, plus a theme id if VTL):
          a. theme — VTL: read vtl/00-wiring.md first (the full file tree you must author,
             and the author-locally-then-upload rule), then create it (vtl/02-themes.md).
             **DESIGN.md is consumed here**: its tokens become CSS in the theme folder —
             there is no separate design step and no other home for the stylesheet.
             HEADLESS: create NO theme; omit the key and the template takes SYSTEM_THEME.
          b. containers (core/06-containers.md) — both modes create the folder and one
             <Var>.vtl per accepted type. VTL writes the markup (vtl/03-containers.md);
             HEADLESS leaves those files empty — React renders, the filename only
             registers the type for the editor.
          c. create + publish the template (core/05-templates.md)
          d. HEADLESS ONLY — the app side, once the types from step 11 exist:
             client config (nextjs/00-connect.md), next.config (02), routing (03), and
             **write + register one component per content type** (01). The map keys
             are the type variables, so the types must exist first. Skip this and
             every slot renders "no component".
- [ ] 13. Create pages — requires the template from step 12c (core/04-pages.md)
- [ ] 14. Wire listings & detail pages (vtl/04-listings-and-details.md or nextjs/04-listings-and-details.md)
- [ ] 15. Create content — fire an action on each contentlet (core/03-content.md)
- [ ] 16. Place content into slots — requires the container from step 12b (core/09-placement.md)
- [ ] 17. Publish everything, page last
- [ ] 18. Verify (vtl/05-verify-and-debug.md or nextjs/05-verify.md) — VTL: validate with /api/vtl/dynamic AND
          page_verify every page type. Headless: page_verify does NOT apply; confirm
          every content type on every page resolves to a component.
          Either way, nothing renders as [PLACEHOLDER] that shouldn't
```

Phase 1 is the interview and cannot be skipped unless both files already exist and the user confirms them. Don't start Phase 2 until the plan is confirmed.

## References

This skill carries only the Phase 1 references; Phase 2's live in `dotcms-best-practices`. Load a
file when you reach its step — don't read everything up front.

**Phase 1 (plan) → `reference/plan/`**
- **How to interview + how to tag answers** → [reference/plan/interview.md](reference/plan/interview.md)
- **DESIGN.md output format** (visual identity) → [reference/plan/design-template.md](reference/plan/design-template.md)
- **PLAN.md output format** (structure + facts) → [reference/plan/plan-template.md](reference/plan/plan-template.md)

**Phase 2 (build) → the `dotcms-best-practices` skill**

The build reference is not in this skill. Load **`dotcms-best-practices`** and open the file named
at each checklist step — `core/NN`, `vtl/NN` or `nextjs/NN` under its `reference/` folder. Its
`SKILL.md` also indexes the same files by intent, and its `reference/README.md` carries the branch
map, tool routing and spec-status note.

Both delivery branches share the same numbering — `00` wire up · `01` type↔renderer contract ·
`02`–`03` mode-specific plumbing · `04` listings & detail · `05` verify — so a shared step is the
same number in either mode.

## Tagging (the core rule)

Every field carries one tag:
- `[confirmed]` — real value the user gave.
- `[PLACEHOLDER — needs human]` — real value exists but not yet available → build renders a visible TODO.
- `[n/a — intentionally omitted]` — fact doesn't exist → build removes the field/section.
- `[ai-draft — approve]` — AI-written prose/tokens awaiting sign-off (never invented facts).

## Done when

Both `PLAN.md` and `DESIGN.md` exist and are fully tagged (every FACT field, every STRUCTURE section); the site is built in dotCMS, everything is published, and **every page type verifies through its delivery mode's verify step** — VTL: the LIVE render is correct (`vtl/05-verify-and-debug.md` in `dotcms-best-practices`); headless: the published page returns populated contentlets and the app renders every one (`nextjs/05-verify.md` in the same skill); no `[PLACEHOLDER]` field renders as if it were a real value, and every `[n/a]` field/section was removed rather than flagged. `[ai-draft]` copy is called out for human approval before launch.
