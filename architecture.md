# Skill system architecture

**Updated:** 2026-09-01 · **Scope:** what ships from `dotcms/skills`. The CLI is a separate
system — see `PLAN.md` §8 and `../core/docs/cli/CLI_DISTRIBUTION_PLAN.md`.

The whole design in one sentence: **one reference corpus, three indexes over it, two entry
skills.**

---

## 1. The pieces

```mermaid
flowchart TD
    subgraph CS["dotcms-create-sites — orchestrator"]
        CSK["SKILL.md<br/>two-phase workflow, 18 steps"]
        PLAN["reference/plan/<br/>interview · plan-template · design-template"]
        CSK --> PLAN
    end

    subgraph BP["dotcms-best-practices — reference"]
        BPK["SKILL.md<br/>intent index + symptom index"]
        RM["reference/README.md<br/>build-step index"]
        CORE["core/ — 8 files<br/>site · content types · content · pages<br/>templates · containers · placement"]
        VTL["vtl/ — 7 files<br/>wiring · mechanism · themes · containers<br/>listings · verify · velocity lookup"]
        NEXT["nextjs/ — 6 files<br/>connect · component contract · next.config<br/>routing · listings · verify"]
        BPK --> CORE
        BPK --> VTL
        BPK --> NEXT
        RM --> CORE
        RM --> VTL
        RM --> NEXT
    end

    CSK -.->|"cites by skill name,<br/>never by relative path"| BPK
```

**Why the citation is by name, not path.** The installer puts real files in
`~/.agents/skills/<skill>/` and symlinks them into each agent's directory. A relative path
like `../dotcms-best-practices/reference/core/00-…` resolves differently depending on which
path the agent walked to get there. Naming the skill lets the agent resolve it.

## 2. Three indexes, one corpus

The 22 reference files are written once and indexed three ways, because the same file answers
different questions depending on why you arrived.

```mermaid
flowchart LR
    A["'create a content type'"] --> I["Intent index<br/>SKILL.md"]
    B["'my page is blank'"] --> S["Symptom index<br/>SKILL.md"]
    C["'build me a site'"] --> W["Workflow<br/>create-sites SKILL.md"]
    W --> D["Build-step index<br/>reference/README.md"]
    I --> F["the 22 files"]
    S --> F
    D --> F
```

| Index | Keyed by | Lives in | Answers |
|---|---|---|---|
| **Intent** | what you want to do | `best-practices/SKILL.md` | "create a content type" → `core/02` |
| **Symptom** | what you're seeing | `best-practices/SKILL.md` | "shell renders, slots missing" → mode-labeled causes |
| **Build step** | dependency order | `reference/README.md` | step 12b of a full build → `core/06` |

**The symptom index is the one that isn't just a table of contents.** It forks on
blank-vs-shell-only first, labels every row with its delivery mode, and exists because every
failure in dotCMS returns **HTTP 200**. A build-step index cannot answer "why is this blank."

## 3. The delivery-mode fork

Every rendering task branches. Content-model work does not.

```mermaid
flowchart TD
    T["a task"] --> Q{"does it touch<br/>rendering?"}
    Q -->|no| CM["core/ only<br/>content types, fields, content<br/><b>don't ask about mode</b>"]
    Q -->|yes| M{"delivery mode?"}
    M -->|VTL| V["core/ + vtl/<br/>dotCMS renders the HTML"]
    M -->|Headless| H["core/ + nextjs/<br/>an app renders it"]
    M -->|unknown| ASK["ask — guessing<br/>wastes the work"]
```

Both branches share the same numbering — `00` wire up · `01` type↔renderer contract ·
`02`–`03` mode plumbing · `04` listings & detail · `05` verify — so a shared step is the same
number in either mode.

**The asymmetry that matters:** in headless, the app wiring may already exist and the skill
tells you to detect it. In VTL, every file is authored from nothing.

## 4. Build dependency order

What `reference/README.md` encodes, and why the order isn't negotiable.

```mermaid
flowchart LR
    S["site<br/>everything is scoped to it"] --> CT["content types<br/>variables are derived"]
    CT --> TH["theme (VTL)<br/>+ the site's CSS"]
    TH --> CN["containers<br/>folders + per-type files"]
    CN --> TP["template<br/>names container paths<br/>that must already resolve"]
    TP --> PG["pages"]
    PG --> C["content"]
    C --> PL["placement<br/>full replacement"]
    PL --> PB["publish, page last"]
    PB --> VF["verify<br/>HTTP 200 proves nothing"]
```

Two loops the diagram flattens: a URL-mapped type needs `urlMapPattern` and `detailPage`
patched back **after** its detail page exists, and a template edit needs a re-publish before
the change reaches LIVE.

## 5. How it reaches a machine

```mermaid
flowchart TD
    R["dotcms/skills repo"] -->|"npx skills add"| A["~/.agents/skills/<br/><b>real files, one copy</b>"]
    A -->|symlink| CC["~/.claude/skills/"]
    A -->|symlink| CU["Cursor"]
    A -->|symlink| CX["Codex"]
    A -->|symlink| OC["opencode"]
```

One copy, N links — so an update propagates without reinstalling. Skills ship **unversioned**;
nothing tells a developer theirs describes an older dotCMS. That's an accepted risk, recorded
in `PLAN.md` §5, not an oversight.

## 6. Where the CLI stops

```mermaid
flowchart LR
    subgraph CLI["dotcms CLI — other repo"]
        P["provision · scaffold<br/>write MCP config · install skills<br/>mint token"]
    end
    subgraph SK["these skills"]
        K["content model · rendering<br/>build order · diagnosis"]
    end
    P -.->|"prints 'Get started with dotCMS'"| K
    P -.->|"npx skills add"| K
```

| Concern | Owner |
|---|---|
| Headless app wiring | **CLI writes it** — the skill detects and extends it |
| Traditional/VTL structure | CLI writes only a directory; **the skill owns everything inside** |
| The hand-off sentence | CLI prints it; **the skills must answer it well** |
| MCP server identity | manifests here and CLI configs must name the same server |

**The skills never assume the CLI ran.** They detect what exists — dotCMS deps in
`package.json`, an existing `createDotCMSClient`, a components object, a catch-all route — and
fill only the gaps. A registry install with no CLI anywhere is a supported path.

---

## The one rule underneath all of it

**Nothing fails loudly.** A missing theme loop, an empty `postloop.vtl`, a wrong-case component
key, content over `max_contentlets`, a container path that doesn't resolve — every one returns
**HTTP 200** with no error. That single fact is why the corpus is organised around failure modes
rather than API surface, why every build path ends in an explicit verify step, and why the
symptom index exists at all.
