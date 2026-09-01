# Interview reference — questions & tagging

## Contents
- Tagging: FACT vs VOICE/STRUCTURE, and the three fact states
- Interview method
- The coverage spine (11 items)
- What NOT to ask

## Tagging every answer

- **FACT** — real-world truth only the human knows: hostname, legal/brand name, address, phone, email, hours, prices, real dates, social links, genuine "featured" picks, legal copy. Never invent. A fact takes one of three states:
  - `[confirmed]` — human gave the real value.
  - `[PLACEHOLDER — needs human]` — real value exists but not available yet → build renders a visible TODO.
  - `[n/a — intentionally omitted]` — fact genuinely doesn't exist (e.g. online-only shop has no address) → build removes the field/section, does not flag it.
  Ask which of the latter two applies; never assume a missing fact is a placeholder.
- **VOICE / STRUCTURE** — sitemap, section order, tone, headings, descriptions, taglines, hero copy, CTA labels. AI may **draft**; human **approves**. Mark `[ai-draft — approve]` once at the **section heading**, not on every row — the approval is per section. Swap it to `[confirmed]` when the user signs off.

## Interview method

The goal is the **fewest questions** that still prevent fabrication. Infer everything you can; ask only what you genuinely cannot derive.

- **Infer first, then confirm in one batch.** Read the assets and brief, draft a *complete* proposed plan from them — sitemap, sections, data model, voice, colors, featured picks — then present it as a single "here's what I'll build; correct anything" confirmation (the spine below is the coverage checklist for that draft, **not** a script to ask one-by-one). Prefer inferring-and-stating over asking: if the logo, assets, or brief answer something, fold your inference into the confirmation rather than asking it open-ended. A bookstore's sitemap and data model, a name and tagline from a logo, a palette from brand colors — these are proposals to confirm, not questions.
- **Ask upfront only for what can't be inferred** — typically just: the **delivery mode** (VTL vs. headless — see spine item 4), the transaction model (link-out vs. checkout vs. catalog, if selling is involved), and the real-vs-placeholder/n-a status of facts (contact, prices, hours). These three carry real consequences and no safe default; everything else can usually ride in the confirmation batch. Batch related items into one question with multiple fields rather than serial questions.
- **Adaptive depth.** Go deeper only where an answer opens real complexity the human invited. Don't branch into complexity they didn't ask for.
- **Read before asking.** A brand doc, logo, or existing content may answer many questions — use it and confirm rather than re-ask. **PLAN.md and DESIGN.md are outputs you produce, not inputs**; only if one already exists, read it, confirm, and cover just the gaps.
- **Colors are never invented.** If the user gave a **logo or image assets**, sample the palette (prefer the logo) and present it as the proposed palette — don't ask "what colors?". Only ask when there's no asset to sample. Draft tokens either way, mark for approval, record the source.
- **Don't validate — probe.** Where you do ask, surface the trade-off the human missed, then recommend.
- **Facts get a firm gate:** "Do you have the real value, or mark it placeholder / n-a?" A marked gap is success; a plausible fabrication is the failure this skill prevents. This gate is the one thing you never skip to save a question.

## The coverage spine

This is the checklist your drafted plan must **cover** — not a list to ask one-by-one. Infer each item from assets/brief and put it in the confirmation batch; escalate to a real upfront question only for the ones you can't derive (see the method above — usually just delivery mode + transaction model + fact status). **→PLAN** / **→DESIGN** marks which artifact each item populates.

1. **Purpose & audience** — what it is, who for, the home page's single job. (VOICE) Confirm in one sentence. **→PLAN** (purpose/audience); voice also seeds **→DESIGN** prose.
2. **Hostname / domain** — (FACT) real hostname, or placeholder; note if it's a throwaway local host for now. **→PLAN**
3. **Transaction intent** — (STRUCTURE, ask before the data model) if the purpose involves selling/booking/applying, pin *how*: **transact-in-dotcms** (real checkout — heavy, usually out of v1), **link-out per item** (adds a buy-URL fact field + external CTA), or **catalog-only** (no buy path). Recommend link-out or catalog for v1. Skip for purely informational sites. **→PLAN**
4. **Delivery mode** — (STRUCTURE, ask upfront) **VTL-rendered** (dotCMS renders the HTML; you author theme + container VTL) or **headless** (dotCMS serves the page, a front-end app renders it via the dotCMS SDK). Cannot be inferred and changes half the build, so ask. If headless, also pin **which framework** — only Next.js has a build branch; Angular, Vue and Astro have upstream examples but no guidance here, so say so rather than improvising. Default to VTL unless the user has a front-end app or names a framework. Answering
   *headless* removes two things from the dotCMS build — no theme is created (the
   template takes `SYSTEM_THEME`), and containers are created but carry no markup — so
   it is worth getting right before the scaffold is built, not after. **→PLAN**
5. **Sitemap** — (STRUCTURE) pages + URLs; which use a urlmap detail. Recommend from purpose. **→PLAN**
6. **Sections per page** — (STRUCTURE) what each page contains, in order. Recommend; confirm. **→PLAN**
7. **Brand & visual identity** — logo / image assets? colors (sample from logo, else ask — never invent)? fonts (pair on a contrast axis)? voice in 3 words? What's fixed vs. open. **→DESIGN** (tokens + prose per the DESIGN.md spec); logo/asset paths also **→PLAN** §6.
8. **Data model** — (STRUCTURE) the core repeating thing + its fields; fold in any field the transaction answer requires. Confirm which are required and which drives the detail URL. **→PLAN**
9. **Content** — per data item & editable section: **facts** (prices, dates, specs, contact) → collect / placeholder / n-a; **prose** (descriptions, taglines, hero/newsletter) → offer to draft, mark `[ai-draft — approve]`. **→PLAN**
10. **Featured / curation** — (FACT if a real merchandising choice) which items, or "AI picks **N=<count>**, human approves" — never an undefined count. **→PLAN**
11. **Deferred-complexity check** — one pass: i18n? real form submission? auth? search? (Commerce handled in step 3.) For each yes, ask the 1–2 follow-ups that unblock the build; for each no, record it as out of scope so the build doesn't add it speculatively. **→PLAN**

## What NOT to ask

The build owns these; asking is noise. Check the `dotcms-best-practices` skill's references and
the codebase first — never re-ask what they answer:

- Content-type vs. widget vs. SimpleWidget; container scaffold; per-type VTL.
- urlmap patterns, detail-page wiring, template/theme mechanics.
- API payload shapes, field `dataType`, reserved-name workarounds, cache-busting.
