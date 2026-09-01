# dotcms/skills

## What this repo is

**The knowledge and the channels it reaches agents through** — the skills themselves, plus the
plugin and marketplace manifests that make them discoverable.

**The CLI work is not here.** It lives in `dotcms/core` at
`docs/cli/CLI_DISTRIBUTION_PLAN.md` — capability libraries, `dotcms` commands, client config
writing, token minting, provisioning. The CLI *installs* what this repo publishes.

Both plans carry an identical **seam** section naming the contract between them. Read it before
changing anything that crosses the boundary.

## Read these, in this order

| File | Holds | Lifetime |
|---|---|---|
| **`PLAN.md`** | **This repo's plan. Start here.** The two skills, content changes forced by CLI decisions, distribution, manifests, the seam with the CLI | Updated as work lands |
| `../core/docs/cli/CLI_DISTRIBUTION_PLAN.md` | The paired CLI plan — capability libraries, command surface, client registry, secrets, phases | Lives in `dotcms/core` |
| `architecture.md` | How the two skills fit together — the corpus, its three indexes, the delivery-mode fork, build order, install model, and where the CLI stops | Diagrams; update when the shape changes |
| `dotcli.md` | The dotCLI MVP spec — its four invariants, commands, API surface. Consumed by the CLI plan, not replaced by it | Freddy's, authoritative |
| `ecosystem.md` | Inventory — every package, version, command surface, repo location, npm namespace. No analysis | Re-check before relying |
| `archive/findings.md` | Verified facts, each with source and date checked. Facts about npm versions and competitor behavior rot | **Goes stale** |
| `archive/decisions.md` | The reasoning trail — 35 entries, several superseded or corrected more than once. Archive, not a working doc | Append-only |
| `archive/sanity-onboarding-teardown.md` | The benchmark: both run transcripts, what to steal, where it broke | Immutable |
| `skills/dotcms-create-sites/` | The skill being distributed. 26 files | The product |

## The protocol

- **Learn a fact?** → `archive/findings.md`, with source and date. Undated facts are a liability.
- **Settle a question?** → `archive/decisions.md`, and strike it from `PLAN.md`'s open items.
- **Hit an unknown?** → `PLAN.md`'s appendix, and say what it blocks.
- **Change your mind?** Never edit a decision in place. Add a new one, mark the old superseded.
- **Nothing is decided because Claude recommended it.** Proposals stay proposed until Freddy
  accepts them.
- **Cite the file, endpoint or version — never the `F-0NN`/`D-0NN` ids** in anything Freddy reads.
  They exist so entries can cross-reference each other, not as shorthand in prose.

## The one rule from the benchmark

**Never print a success screen whose next suggested command fails.** That was Sanity's fatal bug,
and it happened on both of Freddy's runs.
